"""
MySQL Database Manager for Counterfeit Product Detection System
"""

import mysql.connector
from mysql.connector import Error
import json
import base64
from datetime import datetime
import os
from pathlib import Path
import logging
from typing import List, Dict, Any, Optional, Tuple

class MySQLDatabaseManager:
    def __init__(self, host="localhost", user="root", password="", database="counterfeit_detection"):
        """Initialize database manager with MySQL database"""
        self.db_config = {
            'host': host,
            'user': user,
            'password': password,
            'database': database
        }
        
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Initialize database
        self._init_database()
    
    def _init_database(self):
        """Initialize database tables"""
        try:
            # First connect without database to create it if it doesn't exist
            conn = mysql.connector.connect(
                host=self.db_config['host'],
                user=self.db_config['user'],
                password=self.db_config['password']
            )
            cursor = conn.cursor()
            
            # Create database if it doesn't exist
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.db_config['database']}")
            conn.close()
            
            # Now connect with the database
            with mysql.connector.connect(**self.db_config) as conn:
                cursor = conn.cursor()
                
                # Create analysis_history table
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS analysis_history (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    image_data LONGTEXT,
                    image_filename VARCHAR(255),
                    product_type VARCHAR(100),
                    brand VARCHAR(100),
                    model VARCHAR(100),
                    color VARCHAR(50),
                    price_range VARCHAR(50),
                    authenticity_status VARCHAR(50),
                    confidence_score FLOAT,
                    logo_analysis TEXT,
                    quality_analysis TEXT,
                    material_analysis TEXT,
                    pricing_analysis TEXT,
                    overall_verdict TEXT,
                    recommendations TEXT,
                    risk_factors TEXT,
                    verification_methods TEXT,
                    full_analysis TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_favorite BOOLEAN DEFAULT FALSE,
                    is_flagged BOOLEAN DEFAULT FALSE
                )
                ''')
                
                conn.commit()
                self.logger.info("Database tables created successfully")
                
        except Error as e:
            self.logger.error(f"Error initializing database: {str(e)}")
            raise

    def save_analysis(self, analysis_data: Dict[str, Any], image_data: bytes = None, 
                     image_filename: str = None) -> Optional[int]:
        """Save analysis result to database"""
        try:
            with mysql.connector.connect(**self.db_config) as conn:
                cursor = conn.cursor()
                
                # Encode image data if provided
                encoded_image = None
                if image_data:
                    encoded_image = base64.b64encode(image_data).decode('utf-8')
                
                # Extract data from analysis
                product_details = analysis_data.get('product_details', {})
                detailed_analysis = analysis_data.get('detailed_analysis', {})
                
                # Insert analysis
                cursor.execute('''
                    INSERT INTO analysis_history (
                        image_data, image_filename, product_type, brand, model, color, price_range,
                        authenticity_status, confidence_score, logo_analysis, quality_analysis,
                        material_analysis, pricing_analysis, overall_verdict, recommendations,
                        risk_factors, verification_methods, full_analysis
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''', (
                    encoded_image,
                    image_filename,
                    product_details.get('type', ''),
                    product_details.get('brand', ''),
                    product_details.get('model', ''),
                    product_details.get('color', ''),
                    product_details.get('price_range', ''),
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
                return analysis_id
                
        except Error as e:
            self.logger.error(f"Error saving analysis: {str(e)}")
            return None

    def get_analysis_history(self) -> List[Dict[str, Any]]:
        """Get all analysis history"""
        try:
            with mysql.connector.connect(**self.db_config) as conn:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT * FROM analysis_history ORDER BY timestamp DESC")
                return cursor.fetchall()
        except Error as e:
            self.logger.error(f"Error getting analysis history: {str(e)}")
            return []