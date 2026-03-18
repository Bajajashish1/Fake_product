import sqlite3
import hashlib
import os
import streamlit as st
from datetime import datetime

class UserAuth:
    def __init__(self, db_path="users.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize the users database"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Create users table if it doesn't exist
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                company_name TEXT,
                role TEXT,
                is_email_verified BOOLEAN DEFAULT 0,
                remember_token TEXT,
                remember_token_expires TIMESTAMP,
                reset_token TEXT,
                reset_token_expires TIMESTAMP,
                social_login_provider TEXT,
                social_login_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                terms_accepted BOOLEAN DEFAULT 0
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _hash_password(self, password):
        """Hash a password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register_user(self, username, email, password, full_name):
        """Register a new user"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            # Check if username already exists
            c.execute('SELECT * FROM users WHERE username = ?', (username,))
            if c.fetchone() is not None:
                return False, "Username already exists"
            
            # Check if email already exists
            c.execute('SELECT * FROM users WHERE email = ?', (email,))
            if c.fetchone() is not None:
                return False, "Email already exists"
            
            # Hash password and insert user
            password_hash = self._hash_password(password)
            c.execute('''
                INSERT INTO users (username, email, password_hash, full_name, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (username, email, password_hash, full_name, datetime.now()))
            
            conn.commit()
            return True, "Registration successful"
        
        except Exception as e:
            return False, f"Error during registration: {str(e)}"
        finally:
            conn.close()
    
    def login_user(self, username, password):
        """Authenticate a user"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            # Get user by username
            c.execute('SELECT * FROM users WHERE username = ?', (username,))
            user = c.fetchone()
            
            if user is None:
                return False, "Invalid username"
            
            # Verify password
            stored_password_hash = user[3]  # Index 3 is password_hash
            if self._hash_password(password) != stored_password_hash:
                return False, "Invalid password"
            
            # Update last login
            c.execute('UPDATE users SET last_login = ? WHERE username = ?',
                     (datetime.now(), username))
            conn.commit()
            
            return True, {
                "id": user[0],
                "username": user[1],
                "email": user[2],
                "full_name": user[4]
            }
        
        except Exception as e:
            return False, f"Error during login: {str(e)}"
        finally:
            conn.close()
    
    def get_user_info(self, user_id):
        """Get user information by ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            c.execute('SELECT * FROM users WHERE id = ?', (user_id,))
            user = c.fetchone()
            
            if user is None:
                return None
            
            return {
                "id": user[0],
                "username": user[1],
                "email": user[2],
                "full_name": user[4],
                "created_at": user[5],
                "last_login": user[6]
            }
        
        except Exception:
            return None
        finally:
            conn.close()
    
    def update_user(self, user_id, updates):
        """Update user information"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            update_fields = []
            values = []
            
            for field, value in updates.items():
                if field == 'password':
                    update_fields.append('password_hash = ?')
                    values.append(self._hash_password(value))
                elif field in ['email', 'first_name', 'last_name', 'company_name', 'role']:
                    update_fields.append(f'{field} = ?')
                    values.append(value)
            
            if not update_fields:
                return False, "No valid fields to update"
            
            values.append(user_id)
            query = f'''
                UPDATE users 
                SET {', '.join(update_fields)}
                WHERE id = ?
            '''
            
            c.execute(query, values)
            conn.commit()
            
            return True, "User information updated successfully"
        
        except Exception as e:
            return False, f"Error updating user: {str(e)}"
        finally:
            conn.close()

    def set_remember_me(self, user_id, days=30):
        """Set remember me token for a user"""
        try:
            token = hashlib.sha256(os.urandom(32)).hexdigest()
            expires = datetime.now().timestamp() + (days * 24 * 60 * 60)
            
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute('''
                UPDATE users 
                SET remember_token = ?, remember_token_expires = ?
                WHERE id = ?
            ''', (token, expires, user_id))
            conn.commit()
            
            return True, token
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()

    def check_remember_token(self, token):
        """Validate remember me token"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute('''
                SELECT * FROM users 
                WHERE remember_token = ? AND remember_token_expires > ?
            ''', (token, datetime.now().timestamp()))
            user = c.fetchone()
            
            if user:
                return True, {
                    "id": user[0],
                    "first_name": user[1],
                    "last_name": user[2],
                    "email": user[3]
                }
            return False, "Invalid or expired token"
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()

    def initiate_password_reset(self, email):
        """Generate password reset token"""
        try:
            token = hashlib.sha256(os.urandom(32)).hexdigest()
            expires = datetime.now().timestamp() + (24 * 60 * 60)  # 24 hours
            
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            c.execute('SELECT id FROM users WHERE email = ?', (email,))
            user = c.fetchone()
            
            if not user:
                return False, "Email not found"
            
            c.execute('''
                UPDATE users 
                SET reset_token = ?, reset_token_expires = ?
                WHERE email = ?
            ''', (token, expires, email))
            conn.commit()
            
            return True, token
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()

    def reset_password(self, token, new_password):
        """Reset password using token"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            c.execute('''
                SELECT id FROM users 
                WHERE reset_token = ? AND reset_token_expires > ?
            ''', (token, datetime.now().timestamp()))
            user = c.fetchone()
            
            if not user:
                return False, "Invalid or expired reset token"
            
            password_hash = self._hash_password(new_password)
            c.execute('''
                UPDATE users 
                SET password_hash = ?, reset_token = NULL, reset_token_expires = NULL
                WHERE id = ?
            ''', (password_hash, user[0]))
            conn.commit()
            
            return True, "Password reset successful"
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()

    def verify_email(self, email):
        """Mark email as verified"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute('''
                UPDATE users 
                SET is_email_verified = 1
                WHERE email = ?
            ''', (email,))
            conn.commit()
            return True, "Email verified successfully"
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()

    def social_login(self, provider, social_id, email, first_name, last_name):
        """Handle social login (Google/Microsoft)"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            # Check if user exists
            c.execute('SELECT * FROM users WHERE email = ?', (email,))
            user = c.fetchone()
            
            if user:
                # Update social login info
                c.execute('''
                    UPDATE users 
                    SET social_login_provider = ?, social_login_id = ?, last_login = ?
                    WHERE email = ?
                ''', (provider, social_id, datetime.now(), email))
                conn.commit()
                return True, {
                    "id": user[0],
                    "first_name": user[1],
                    "last_name": user[2],
                    "email": user[3]
                }
            else:
                # Create new user
                c.execute('''
                    INSERT INTO users (
                        first_name, last_name, email, password_hash,
                        social_login_provider, social_login_id,
                        is_email_verified, created_at, last_login
                    ) VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?)
                ''', (
                    first_name, last_name, email, 'SOCIAL_LOGIN',
                    provider, social_id, datetime.now(), datetime.now()
                ))
                conn.commit()
                return True, {
                    "id": c.lastrowid,
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": email
                }
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()