"""
Database Manager for Counterfeit Product Detection System
Handles SQLite database operations for storing analysis history, favorites, and flagged products.
"""

import sqlite3
import json
import base64
from datetime import datetime
import os
from pathlib import Path
import logging
from typing import List, Dict, Any, Optional, Tuple

class DatabaseManager:
    def __init__(self, db_path: str = None):
        """Initialize database manager with SQLite database"""
        # Use environment variable if available, otherwise use default path
        self.db_path = Path(db_path or os.getenv('DB_PATH', "product_history/counterfeit_detection.db"))
        self.db_path.parent.mkdir(exist_ok=True, parents=True)
        
        # Set up logging with proper formatting for production
        logging.basicConfig(
            level=logging.INFO if os.getenv('ENVIRONMENT') == 'production' else logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(self.db_path.parent / 'database.log')
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize database
        self._init_database()
    
    def _init_database(self):
        """Initialize database tables"""
        try:
            # Ensure directory exists with proper permissions
            db_dir = os.path.dirname(self.db_path)
            os.makedirs(db_dir, exist_ok=True)
            
            # Check if database file is writable or can be created
            try:
                if not os.path.exists(self.db_path):
                    self.logger.info(f"Creating new database file at {self.db_path}")
                    # Create the database and its tables
                    with sqlite3.connect(self.db_path) as conn:
                        cursor = conn.cursor()
                        cursor.execute('''
                        CREATE TABLE IF NOT EXISTS analysis_history (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            image_data TEXT,
                            image_filename TEXT,
                            product_type TEXT,
                            brand TEXT,
                            model TEXT,
                            color TEXT,
                            price_range TEXT,
                            authenticity_status TEXT,
                            confidence_score REAL,
                            logo_analysis TEXT,
                            quality_analysis TEXT,
                            material_analysis TEXT,
                            pricing_analysis TEXT,
                            overall_verdict TEXT,
                            recommendations TEXT,
                            risk_factors TEXT,
                            verification_methods TEXT,
                            full_analysis TEXT,
                            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                            is_favorite BOOLEAN DEFAULT 0,
                            is_flagged BOOLEAN DEFAULT 0
                        )
                        ''')
                        conn.commit()
                        self.logger.info("Database tables created successfully")
                elif not os.access(self.db_path, os.W_OK):
                    self.logger.error(f"Database file {self.db_path} is not writable")
                    raise PermissionError(f"Database file {self.db_path} is not writable")
                else:
                    self.logger.info(f"Using existing database at {self.db_path}")
            except Exception as e:
                self.logger.error(f"Error checking/creating database file: {str(e)}")
                raise
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Analysis history table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS analysis_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        image_data TEXT,  -- Base64 encoded image
                        image_filename TEXT,
                        product_type TEXT,
                        brand TEXT,
                        model TEXT,
                        color TEXT,
                        price_range TEXT,
                        authenticity_status TEXT,
                        confidence_score REAL,
                        logo_analysis TEXT,
                        quality_analysis TEXT,
                        material_analysis TEXT,
                        pricing_analysis TEXT,
                        overall_verdict TEXT,
                        recommendations TEXT,
                        risk_factors TEXT,
                        verification_methods TEXT,
                        full_analysis TEXT,  -- JSON string of complete analysis
                        is_favorite BOOLEAN DEFAULT 0,
                        is_flagged BOOLEAN DEFAULT 0,
                        notes TEXT,
                        tags TEXT  -- Comma-separated tags
                    )
                ''')
                
                # User settings table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS user_settings (
                        id INTEGER PRIMARY KEY,
                        setting_name TEXT UNIQUE,
                        setting_value TEXT,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Analysis statistics table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS analysis_stats (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date DATE,
                        total_analyses INTEGER DEFAULT 0,
                        authentic_count INTEGER DEFAULT 0,
                        counterfeit_count INTEGER DEFAULT 0,
                        uncertain_count INTEGER DEFAULT 0,
                        avg_confidence REAL DEFAULT 0.0
                    )
                ''')
                
                # Create indexes for better performance
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON analysis_history(timestamp)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_authenticity ON analysis_history(authenticity_status)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_brand ON analysis_history(brand)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_favorite ON analysis_history(is_favorite)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_flagged ON analysis_history(is_flagged)')
                
                conn.commit()
                self.logger.info("Database initialized successfully")
                
        except Exception as e:
            self.logger.error(f"Error initializing database: {str(e)}")
            raise
    
    def save_analysis(self, analysis_data: Dict[str, Any], image_data: bytes = None, 
                     image_filename: str = None) -> Optional[int]:
        """Save analysis result to database"""
        try:
            # Validate input data
            if not isinstance(analysis_data, dict):
                raise ValueError(f"analysis_data must be a dictionary, got {type(analysis_data)}")
            
            self.logger.info("Attempting to save analysis to database...")
            self.logger.info(f"Database path: {self.db_path}")
            
            with sqlite3.connect(self.db_path, timeout=20) as conn:
                cursor = conn.cursor()
                
                # Encode image data if provided
                encoded_image = None
                if image_data:
                    try:
                        encoded_image = base64.b64encode(image_data).decode('utf-8')
                        self.logger.info("Successfully encoded image data")
                    except Exception as e:
                        self.logger.error(f"Error encoding image data: {str(e)}")
                        raise
                
                # Extract data from analysis
                product_details = analysis_data.get('product_details', {})
                detailed_analysis = analysis_data.get('detailed_analysis', {})
                
                cursor.execute('''
                    INSERT INTO analysis_history (
                        image_data, image_filename, product_type, brand, model, color, price_range,
                        authenticity_status, confidence_score, logo_analysis, quality_analysis,
                        material_analysis, pricing_analysis, overall_verdict, recommendations,
                        risk_factors, verification_methods, full_analysis
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    encoded_image,
                    image_filename,
                    product_details.get('type', ''),
                    product_details.get('brand', ''),
                    product_details.get('model', ''),
                    product_details.get('color', ''),
                    product_details.get('estimated_price_range', ''),
                    analysis_data.get('authenticity_status', ''),
                    analysis_data.get('confidence_score', 0.0),
                    detailed_analysis.get('logo_analysis', ''),
                    detailed_analysis.get('quality_analysis', ''),
                    detailed_analysis.get('material_analysis', ''),
                    detailed_analysis.get('pricing_analysis', ''),
                    analysis_data.get('overall_verdict', ''),
                    json.dumps(analysis_data.get('recommendations', [])),
                    json.dumps(analysis_data.get('risk_factors', [])),
                    json.dumps(analysis_data.get('verification_methods', [])),
                    json.dumps(analysis_data)
                ))
                
                analysis_id = cursor.lastrowid
                conn.commit()
                
                # Update daily statistics
                self._update_daily_stats(analysis_data.get('authenticity_status', ''),
                                       analysis_data.get('confidence_score', 0.0))
                
                self.logger.info(f"Analysis saved with ID: {analysis_id}")
                return analysis_id
                
        except Exception as e:
            self.logger.error(f"Error saving analysis: {str(e)}")
            return None
    
    def get_analysis_history(self, limit: int = 100, offset: int = 0, 
                           filter_by: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get analysis history with optional filtering"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Build query with filters
                query = '''
                    SELECT id, timestamp, image_filename, product_type, brand, model, color,
                           authenticity_status, confidence_score, is_favorite, is_flagged,
                           notes, tags, full_analysis
                    FROM analysis_history
                '''
                params = []
                conditions = []
                
                if filter_by:
                    if filter_by.get('authenticity_status'):
                        conditions.append('authenticity_status = ?')
                        params.append(filter_by['authenticity_status'])
                    
                    if filter_by.get('brand'):
                        conditions.append('brand LIKE ?')
                        params.append(f"%{filter_by['brand']}%")
                    
                    if filter_by.get('is_favorite'):
                        conditions.append('is_favorite = ?')
                        params.append(1)
                    
                    if filter_by.get('is_flagged'):
                        conditions.append('is_flagged = ?')
                        params.append(1)
                    
                    if filter_by.get('date_from'):
                        conditions.append('DATE(timestamp) >= ?')
                        params.append(filter_by['date_from'])
                    
                    if filter_by.get('date_to'):
                        conditions.append('DATE(timestamp) <= ?')
                        params.append(filter_by['date_to'])
                
                if conditions:
                    query += ' WHERE ' + ' AND '.join(conditions)
                
                query += ' ORDER BY timestamp DESC LIMIT ? OFFSET ?'
                params.extend([limit, offset])
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                # Convert to list of dictionaries
                history = []
                for row in rows:
                    item = {
                        'id': row[0],
                        'timestamp': row[1],
                        'image_filename': row[2],
                        'product_type': row[3],
                        'brand': row[4],
                        'model': row[5],
                        'color': row[6],
                        'authenticity_status': row[7],
                        'confidence_score': row[8],
                        'is_favorite': bool(row[9]),
                        'is_flagged': bool(row[10]),
                        'notes': row[11],
                        'tags': row[12],
                        'full_analysis': json.loads(row[13]) if row[13] else {}
                    }
                    history.append(item)
                
                return history
                
        except Exception as e:
            self.logger.error(f"Error loading history: {str(e)}")
            return []
    
    def get_analysis_by_id(self, analysis_id: int) -> Optional[Dict[str, Any]]:
        """Get specific analysis by ID with full details including image"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM analysis_history WHERE id = ?
                ''', (analysis_id,))
                
                row = cursor.fetchone()
                if not row:
                    return None
                
                # Get column names
                columns = [description[0] for description in cursor.description]
                
                # Convert to dictionary
                analysis = dict(zip(columns, row))
                
                # Decode image data if present
                if analysis.get('image_data'):
                    analysis['image_bytes'] = base64.b64decode(analysis['image_data'])
                
                # Parse JSON fields
                if analysis.get('full_analysis'):
                    analysis['full_analysis'] = json.loads(analysis['full_analysis'])
                
                return analysis
                
        except Exception as e:
            self.logger.error(f"Error loading analysis by ID: {str(e)}")
            return None
    
    def update_analysis(self, analysis_id: int, updates: Dict[str, Any]) -> bool:
        """Update specific analysis fields"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Build update query
                set_clauses = []
                params = []
                
                for field, value in updates.items():
                    if field in ['is_favorite', 'is_flagged', 'notes', 'tags']:
                        set_clauses.append(f'{field} = ?')
                        params.append(value)
                
                if not set_clauses:
                    return False
                
                query = f'''
                    UPDATE analysis_history 
                    SET {', '.join(set_clauses)}
                    WHERE id = ?
                '''
                params.append(analysis_id)
                
                cursor.execute(query, params)
                conn.commit()
                
                return cursor.rowcount > 0
                
        except Exception as e:
            self.logger.error(f"Error updating analysis: {str(e)}")
            return False
    
    def delete_analysis(self, analysis_id: int) -> bool:
        """Delete analysis by ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('DELETE FROM analysis_history WHERE id = ?', (analysis_id,))
                conn.commit()
                
                return cursor.rowcount > 0
                
        except Exception as e:
            self.logger.error(f"Error deleting analysis: {str(e)}")
            return False
    
    def get_statistics(self, days: int = 30) -> Dict[str, Any]:
        """Get analysis statistics for the last N days"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Total analyses
                cursor.execute('''
                    SELECT COUNT(*) FROM analysis_history 
                    WHERE DATE(timestamp) >= DATE('now', '-{} days')
                '''.format(days))
                total_analyses = cursor.fetchone()[0]
                
                # Authenticity breakdown
                cursor.execute('''
                    SELECT authenticity_status, COUNT(*) 
                    FROM analysis_history 
                    WHERE DATE(timestamp) >= DATE('now', '-{} days')
                    GROUP BY authenticity_status
                '''.format(days))
                authenticity_counts = dict(cursor.fetchall())
                
                # Average confidence by authenticity status
                cursor.execute('''
                    SELECT authenticity_status, AVG(confidence_score) 
                    FROM analysis_history 
                    WHERE DATE(timestamp) >= DATE('now', '-{} days')
                    GROUP BY authenticity_status
                '''.format(days))
                avg_confidence = dict(cursor.fetchall())
                
                # Daily analysis counts for the last week
                cursor.execute('''
                    SELECT DATE(timestamp), COUNT(*) 
                    FROM analysis_history 
                    WHERE DATE(timestamp) >= DATE('now', '-7 days')
                    GROUP BY DATE(timestamp)
                    ORDER BY DATE(timestamp)
                ''')
                daily_counts = dict(cursor.fetchall())
                
                # Top brands analyzed
                cursor.execute('''
                    SELECT brand, COUNT(*) 
                    FROM analysis_history 
                    WHERE DATE(timestamp) >= DATE('now', '-{} days')
                    AND brand != ''
                    GROUP BY brand
                    ORDER BY COUNT(*) DESC
                    LIMIT 10
                '''.format(days))
                top_brands = dict(cursor.fetchall())
                
                return {
                    'total_analyses': total_analyses,
                    'authenticity_counts': authenticity_counts,
                    'avg_confidence': avg_confidence,
                    'daily_counts': daily_counts,
                    'top_brands': top_brands,
                    'period_days': days
                }
                
        except Exception as e:
            self.logger.error(f"Error getting statistics: {str(e)}")
            return {}
    
    def _update_daily_stats(self, authenticity_status: str, confidence_score: float):
        """Update daily statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                today = datetime.now().date()
                
                # Check if record exists for today
                cursor.execute('''
                    SELECT id, total_analyses, authentic_count, counterfeit_count, 
                           uncertain_count, avg_confidence
                    FROM analysis_stats WHERE date = ?
                ''', (today,))
                
                row = cursor.fetchone()
                
                if row:
                    # Update existing record
                    stats_id, total, authentic, counterfeit, uncertain, avg_conf = row
                    new_total = total + 1
                    
                    # Update counts based on authenticity status
                    if authenticity_status.lower() == 'authentic':
                        authentic += 1
                    elif authenticity_status.lower() == 'counterfeit':
                        counterfeit += 1
                    else:
                        uncertain += 1
                    
                    # Calculate new average confidence
                    new_avg_conf = ((avg_conf * total) + confidence_score) / new_total
                    
                    cursor.execute('''
                        UPDATE analysis_stats 
                        SET total_analyses = ?, authentic_count = ?, counterfeit_count = ?,
                            uncertain_count = ?, avg_confidence = ?
                        WHERE id = ?
                    ''', (new_total, authentic, counterfeit, uncertain, new_avg_conf, stats_id))
                else:
                    # Create new record
                    authentic = 1 if authenticity_status.lower() == 'authentic' else 0
                    counterfeit = 1 if authenticity_status.lower() == 'counterfeit' else 0
                    uncertain = 1 if authenticity_status.lower() not in ['authentic', 'counterfeit'] else 0
                    
                    cursor.execute('''
                        INSERT INTO analysis_stats 
                        (date, total_analyses, authentic_count, counterfeit_count, 
                         uncertain_count, avg_confidence)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (today, 1, authentic, counterfeit, uncertain, confidence_score))
                
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Error updating daily stats: {str(e)}")
    
    def export_data(self, format_type: str = 'json') -> Optional[str]:
        """Export all data to file"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get all data
                cursor.execute('SELECT * FROM analysis_history ORDER BY timestamp DESC')
                analyses = cursor.fetchall()
                
                cursor.execute('SELECT * FROM analysis_stats ORDER BY date DESC')
                stats = cursor.fetchall()
                
                # Convert to export format
                export_data = {
                    'export_timestamp': datetime.now().isoformat(),
                    'total_records': len(analyses),
                    'analyses': [],
                    'statistics': []
                }
                
                # Get column names
                cursor.execute('PRAGMA table_info(analysis_history)')
                analysis_columns = [row[1] for row in cursor.fetchall()]
                
                cursor.execute('PRAGMA table_info(analysis_stats)')
                stats_columns = [row[1] for row in cursor.fetchall()]
                
                # Convert analyses to dictionaries (excluding image_data for size)
                for row in analyses:
                    analysis = dict(zip(analysis_columns, row))
                    # Remove image_data to reduce file size
                    if 'image_data' in analysis:
                        del analysis['image_data']
                    export_data['analyses'].append(analysis)
                
                # Convert stats to dictionaries
                for row in stats:
                    stat = dict(zip(stats_columns, row))
                    export_data['statistics'].append(stat)
                
                # Save to file
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                export_file = f"product_history/export_{timestamp}.json"
                
                with open(export_file, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, default=str)
                
                return export_file
                
        except Exception as e:
            self.logger.error(f"Error exporting data: {str(e)}")
            return None
    
    def cleanup_old_data(self, days_to_keep: int = 365):
        """Clean up old analysis data"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Delete old analyses
                cursor.execute('''
                    DELETE FROM analysis_history 
                    WHERE DATE(timestamp) < DATE('now', '-{} days')
                '''.format(days_to_keep))
                
                deleted_count = cursor.rowcount
                
                # Delete old stats
                cursor.execute('''
                    DELETE FROM analysis_stats 
                    WHERE date < DATE('now', '-{} days')
                '''.format(days_to_keep))
                
                conn.commit()
                
                self.logger.info(f"Cleaned up {deleted_count} old analysis records")
                return deleted_count
                
        except Exception as e:
            self.logger.error(f"Error cleaning up data: {str(e)}")
            return 0
    
    def get_database_size(self) -> Dict[str, Any]:
        """Get database size information"""
        try:
            db_size = os.path.getsize(self.db_path) if self.db_path.exists() else 0
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Count records in each table
                cursor.execute('SELECT COUNT(*) FROM analysis_history')
                history_count = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(*) FROM analysis_stats')
                stats_count = cursor.fetchone()[0]
                
                return {
                    'database_size_bytes': db_size,
                    'database_size_mb': round(db_size / (1024 * 1024), 2),
                    'analysis_history_count': history_count,
                    'analysis_stats_count': stats_count
                }
                
        except Exception as e:
            self.logger.error(f"Error getting database size: {str(e)}")
            return {}