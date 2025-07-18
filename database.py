import sqlite3
import pandas as pd
import json
from typing import Dict, List, Optional
import logging
from config import DATABASE_PATH

logger = logging.getLogger(__name__)

class GrantDatabase:
    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create proposals table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS proposals (
                id INTEGER PRIMARY KEY,
                number INTEGER,
                title TEXT,
                description TEXT,
                author TEXT,
                repository TEXT,
                repository_info TEXT,
                state TEXT,
                merged BOOLEAN,
                created_at TIMESTAMP,
                updated_at TIMESTAMP,
                closed_at TIMESTAMP,
                merged_at TIMESTAMP,
                milestones INTEGER,
                curators TEXT,
                category TEXT,
                approval_time_days REAL,
                rejection_reason TEXT,
                bounty_amount REAL,
                labels TEXT,
                comments_count INTEGER,
                reviews_count INTEGER,
                additions INTEGER,
                deletions INTEGER,
                changed_files INTEGER,
                created_date DATE,
                updated_date DATE
            )
        ''')
        
        # Create metrics table for caching performance metrics
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT UNIQUE,
                metric_value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_proposals_repository ON proposals(repository)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_proposals_category ON proposals(category)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_proposals_author ON proposals(author)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_proposals_created_at ON proposals(created_at)')
        
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully")
    
    def save_proposals(self, df: pd.DataFrame):
        """Save proposals DataFrame to database"""
        conn = sqlite3.connect(self.db_path)
        
        # Convert complex columns to JSON strings
        df_to_save = df.copy()
        
        # Convert list columns to JSON strings
        if 'curators' in df_to_save.columns:
            df_to_save['curators'] = df_to_save['curators'].apply(json.dumps)
        
        if 'labels' in df_to_save.columns:
            df_to_save['labels'] = df_to_save['labels'].apply(json.dumps)
        
        if 'repository_info' in df_to_save.columns:
            df_to_save['repository_info'] = df_to_save['repository_info'].apply(json.dumps)
        
        # Add date columns for easier querying
        df_to_save['created_date'] = pd.to_datetime(df_to_save['created_at']).dt.date
        df_to_save['updated_date'] = pd.to_datetime(df_to_save['updated_at']).dt.date
        
        # Save to database
        df_to_save.to_sql('proposals', conn, if_exists='replace', index=False)
        
        conn.close()
        logger.info(f"Saved {len(df)} proposals to database")
    
    def load_proposals(self) -> pd.DataFrame:
        """Load proposals from database"""
        conn = sqlite3.connect(self.db_path)
        
        query = "SELECT * FROM proposals"
        df = pd.read_sql_query(query, conn)
        
        # Convert JSON strings back to Python objects
        if 'curators' in df.columns:
            df['curators'] = df['curators'].apply(lambda x: json.loads(x) if x else [])
        
        if 'labels' in df.columns:
            df['labels'] = df['labels'].apply(lambda x: json.loads(x) if x else [])
        
        if 'repository_info' in df.columns:
            df['repository_info'] = df['repository_info'].apply(lambda x: json.loads(x) if x else {})
        
        # Convert date columns
        date_columns = ['created_at', 'updated_at', 'closed_at', 'merged_at']
        for col in date_columns:
            if col in df.columns:
                try:
                    df[col] = pd.to_datetime(df[col], format='mixed')
                except:
                    # If parsing fails, try with ISO format
                    try:
                        df[col] = pd.to_datetime(df[col], format='ISO8601')
                    except:
                        # If all parsing fails, keep as string
                        pass
        
        conn.close()
        return df
    
    def save_metrics(self, metrics: Dict):
        """Save performance metrics to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for metric_name, metric_value in metrics.items():
            # Convert complex objects to JSON
            if isinstance(metric_value, (dict, list)):
                metric_value = json.dumps(metric_value)
            else:
                metric_value = str(metric_value)
            
            cursor.execute('''
                INSERT OR REPLACE INTO metrics (metric_name, metric_value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            ''', (metric_name, metric_value))
        
        conn.commit()
        conn.close()
        logger.info(f"Saved {len(metrics)} metrics to database")
    
    def load_metrics(self) -> Dict:
        """Load performance metrics from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT metric_name, metric_value FROM metrics")
        rows = cursor.fetchall()
        
        metrics = {}
        for metric_name, metric_value in rows:
            try:
                # Try to parse as JSON first
                metrics[metric_name] = json.loads(metric_value)
            except json.JSONDecodeError:
                # If not JSON, try to convert to appropriate type
                try:
                    metrics[metric_name] = float(metric_value)
                except ValueError:
                    metrics[metric_name] = metric_value
        
        conn.close()
        return metrics
    
    def get_proposals_by_repository(self, repository: str) -> pd.DataFrame:
        """Get proposals for a specific repository"""
        conn = sqlite3.connect(self.db_path)
        query = "SELECT * FROM proposals WHERE repository = ?"
        df = pd.read_sql_query(query, conn, params=(repository,))
        conn.close()
        return df
    
    def get_proposals_by_category(self, category: str) -> pd.DataFrame:
        """Get proposals by category"""
        conn = sqlite3.connect(self.db_path)
        query = "SELECT * FROM proposals WHERE category = ?"
        df = pd.read_sql_query(query, conn, params=(category,))
        conn.close()
        return df
    
    def get_proposals_by_author(self, author: str) -> pd.DataFrame:
        """Get proposals by author"""
        conn = sqlite3.connect(self.db_path)
        query = "SELECT * FROM proposals WHERE author = ?"
        df = pd.read_sql_query(query, conn, params=(author,))
        conn.close()
        return df
    
    def get_proposals_by_date_range(self, start_date: str, end_date: str) -> pd.DataFrame:
        """Get proposals within a date range"""
        conn = sqlite3.connect(self.db_path)
        query = "SELECT * FROM proposals WHERE created_at BETWEEN ? AND ?"
        df = pd.read_sql_query(query, conn, params=(start_date, end_date))
        conn.close()
        return df
    
    def get_statistics(self) -> Dict:
        """Get basic statistics from the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # Total proposals
        cursor.execute("SELECT COUNT(*) FROM proposals")
        stats['total_proposals'] = cursor.fetchone()[0]
        
        # Approved proposals
        cursor.execute("SELECT COUNT(*) FROM proposals WHERE merged = 1")
        stats['approved_proposals'] = cursor.fetchone()[0]
        
        # Rejected proposals
        cursor.execute("SELECT COUNT(*) FROM proposals WHERE category = 'REJECTED'")
        stats['rejected_proposals'] = cursor.fetchone()[0]
        
        # Unique authors
        cursor.execute("SELECT COUNT(DISTINCT author) FROM proposals")
        stats['unique_authors'] = cursor.fetchone()[0]
        
        # Average approval time
        cursor.execute("SELECT AVG(approval_time_days) FROM proposals WHERE approval_time_days IS NOT NULL")
        result = cursor.fetchone()[0]
        stats['avg_approval_time_days'] = result if result else 0
        
        conn.close()
        return stats
    
    def clear_database(self):
        """Clear all data from the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM proposals")
        cursor.execute("DELETE FROM metrics")
        
        conn.commit()
        conn.close()
        logger.info("Database cleared") 