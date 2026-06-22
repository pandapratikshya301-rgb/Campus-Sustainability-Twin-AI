"""
Database Module
Handles user authentication and session management using SQLite
"""

import sqlite3
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict
import os

class Database:
    """Manages user authentication and sessions"""
    
    def __init__(self, db_path='campus_ai.db'):
        """Initialize database connection"""
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Create tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                phone TEXT UNIQUE,
                password_hash TEXT NOT NULL,
                full_name TEXT NOT NULL,
                user_type TEXT DEFAULT 'student',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        # Sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                session_token TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                ip_address TEXT,
                user_agent TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # User complaints table (to track user's complaints)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_complaints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                complaint_id TEXT NOT NULL,
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # Notifications table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                complaint_id TEXT,
                type TEXT NOT NULL,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                is_read BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        conn.commit()
        conn.close()
        print("[OK] Database initialized")
    
    def hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def generate_session_token(self) -> str:
        """Generate secure session token"""
        return secrets.token_urlsafe(32)
    
    def register_user(self, email: str, password: str, full_name: str, 
                     phone: Optional[str] = None, user_type: str = 'student') -> Dict:
        """
        Register a new user
        
        Args:
            email: User's email address
            password: User's password
            full_name: User's full name
            phone: Optional phone number
            user_type: Type of user (student, admin, staff)
            
        Returns:
            Dictionary with success status and message
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if user already exists
            cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
            if cursor.fetchone():
                return {'success': False, 'message': 'Email already registered'}
            
            if phone:
                cursor.execute('SELECT id FROM users WHERE phone = ?', (phone,))
                if cursor.fetchone():
                    return {'success': False, 'message': 'Phone number already registered'}
            
            # Hash password and insert user
            password_hash = self.hash_password(password)
            cursor.execute('''
                INSERT INTO users (email, phone, password_hash, full_name, user_type)
                VALUES (?, ?, ?, ?, ?)
            ''', (email, phone, password_hash, full_name, user_type))
            
            conn.commit()
            user_id = cursor.lastrowid
            conn.close()
            
            return {
                'success': True,
                'message': 'Registration successful',
                'user_id': user_id
            }
        except Exception as e:
            return {'success': False, 'message': f'Registration failed: {str(e)}'}
    
    def login_user(self, email_or_phone: str, password: str,
                  ip_address: Optional[str] = None, user_agent: Optional[str] = None) -> Dict:
        """
        Login user and create session
        
        Args:
            email_or_phone: User's email or phone number
            password: User's password
            ip_address: Client IP address
            user_agent: Client user agent
            
        Returns:
            Dictionary with success status, session token, and user info
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Find user by email or phone
            password_hash = self.hash_password(password)
            cursor.execute('''
                SELECT id, email, full_name, user_type, is_active
                FROM users
                WHERE (email = ? OR phone = ?) AND password_hash = ?
            ''', (email_or_phone, email_or_phone, password_hash))
            
            user = cursor.fetchone()
            
            if not user:
                conn.close()
                return {'success': False, 'message': 'Invalid credentials'}
            
            user_id, email, full_name, user_type, is_active = user
            
            if not is_active:
                conn.close()
                return {'success': False, 'message': 'Account is inactive'}
            
            # Create session
            session_token = self.generate_session_token()
            expires_at = datetime.now() + timedelta(days=7)  # 7 days session
            
            cursor.execute('''
                INSERT INTO sessions (user_id, session_token, expires_at, ip_address, user_agent)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, session_token, expires_at, ip_address, user_agent))
            
            # Update last login
            cursor.execute('''
                UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?
            ''', (user_id,))
            
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'message': 'Login successful',
                'session_token': session_token,
                'user': {
                    'id': user_id,
                    'email': email,
                    'full_name': full_name,
                    'user_type': user_type
                }
            }
        except Exception as e:
            return {'success': False, 'message': f'Login failed: {str(e)}'}
    
    def verify_session(self, session_token: str) -> Optional[Dict]:
        """
        Verify session token and return user info
        
        Args:
            session_token: Session token to verify
            
        Returns:
            User dictionary if valid, None otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT u.id, u.email, u.full_name, u.user_type, s.expires_at
                FROM sessions s
                JOIN users u ON s.user_id = u.id
                WHERE s.session_token = ? AND u.is_active = 1
            ''', (session_token,))
            
            result = cursor.fetchone()
            conn.close()
            
            if not result:
                return None
            
            user_id, email, full_name, user_type, expires_at = result
            
            # Check if session expired
            if datetime.fromisoformat(expires_at) < datetime.now():
                self.logout_user(session_token)
                return None
            
            return {
                'id': user_id,
                'email': email,
                'full_name': full_name,
                'user_type': user_type
            }
        except Exception as e:
            print(f"Session verification error: {e}")
            return None
    
    def logout_user(self, session_token: str) -> bool:
        """
        Logout user by deleting session
        
        Args:
            session_token: Session token to delete
            
        Returns:
            True if successful
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM sessions WHERE session_token = ?', (session_token,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Logout error: {e}")
            return False
    
    def link_complaint_to_user(self, user_id: int, complaint_id: str) -> bool:
        """Link a complaint to a user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO user_complaints (user_id, complaint_id)
                VALUES (?, ?)
            ''', (user_id, complaint_id))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error linking complaint: {e}")
            return False
    
    def get_user_complaints(self, user_id: int) -> list:
        """Get all complaints submitted by a user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT complaint_id, submitted_at
                FROM user_complaints
                WHERE user_id = ?
                ORDER BY submitted_at DESC
            ''', (user_id,))
            complaints = cursor.fetchall()
            conn.close()
            return [{'complaint_id': c[0], 'submitted_at': c[1]} for c in complaints]
        except Exception as e:
            print(f"Error getting user complaints: {e}")
            return []
    
    def get_user_complaints_by_complaint_id(self, complaint_id: str) -> list:
        """Get all users who submitted a specific complaint"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT user_id, submitted_at
                FROM user_complaints
                WHERE complaint_id = ?
            ''', (complaint_id,))
            results = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return results
        except Exception as e:
            print(f"Error getting users for complaint: {e}")
            return []
    
    def cleanup_expired_sessions(self):
        """Remove expired sessions from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM sessions WHERE expires_at < CURRENT_TIMESTAMP')
            conn.commit()
            deleted = cursor.rowcount
            conn.close()
            return deleted
        except Exception as e:
            print(f"Error cleaning sessions: {e}")
            return 0

# Made with Bob

    
    def create_notification(self, user_id: Optional[int], complaint_id: str, 
                          notification_type: str, title: str, message: str) -> bool:
        """
        Create a new notification
        
        Args:
            user_id: User ID (None for broadcast notifications)
            complaint_id: Related complaint ID
            notification_type: Type of notification (new_complaint, status_update, resolved)
            title: Notification title
            message: Notification message
            
        Returns:
            True if successful
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO notifications (user_id, complaint_id, type, title, message)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, complaint_id, notification_type, title, message))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error creating notification: {e}")
            return False
    
    def get_user_notifications(self, user_id: int, unread_only: bool = False) -> list:
        """
        Get notifications for a user
        
        Args:
            user_id: User ID
            unread_only: If True, only return unread notifications
            
        Returns:
            List of notifications
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = '''
                SELECT id, complaint_id, type, title, message, is_read, created_at
                FROM notifications
                WHERE user_id = ? OR user_id IS NULL
            '''
            
            if unread_only:
                query += ' AND is_read = 0'
            
            query += ' ORDER BY created_at DESC LIMIT 50'
            
            cursor.execute(query, (user_id,))
            notifications = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return notifications
        except Exception as e:
            print(f"Error getting notifications: {e}")
            return []
    
    def mark_notification_read(self, notification_id: int, user_id: int) -> bool:
        """Mark a notification as read"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE notifications
                SET is_read = 1
                WHERE id = ? AND (user_id = ? OR user_id IS NULL)
            ''', (notification_id, user_id))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error marking notification as read: {e}")
            return False
    
    def mark_all_notifications_read(self, user_id: int) -> bool:
        """Mark all notifications as read for a user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE notifications
                SET is_read = 1
                WHERE user_id = ? OR user_id IS NULL
            ''', (user_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error marking all notifications as read: {e}")
            return False
    
    def get_unread_count(self, user_id: int) -> int:
        """Get count of unread notifications"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT COUNT(*)
                FROM notifications
                WHERE (user_id = ? OR user_id IS NULL) AND is_read = 0
            ''', (user_id,))
            count = cursor.fetchone()[0]
            conn.close()
            return count
        except Exception as e:
            print(f"Error getting unread count: {e}")
            return 0
