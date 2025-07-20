import sqlite3
import json
import pandas as pd
from datetime import datetime
import os

# Try to import config, with fallbacks
try:
    from config import DATABASE_PATH
except ImportError:
    # Fallback values if config module is not available
    DATABASE_PATH = "grants_database.db"

# Try to import cloud storage
try:
    from cloud_storage import CloudStorage
    CLOUD_STORAGE_AVAILABLE = True
except ImportError:
    CLOUD_STORAGE_AVAILABLE = False

class GrantDatabase:
    def __init__(self, db_path: str = None):
        self.db_path = db_path or DATABASE_PATH
        self.cloud_storage = None
        
        # Initialize cloud storage if available
        if CLOUD_STORAGE_AVAILABLE:
            try:
                self.cloud_storage = CloudStorage()
            except Exception as e:
                print(f"Cloud storage initialization failed: {e}")
                self.cloud_storage = None
        
        # Initialize SQLite database for local development
        if not self.cloud_storage:
            self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create proposals table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS proposals (
                    id INTEGER PRIMARY KEY,
                    number INTEGER,
                    title TEXT,
                    body TEXT,
                    state TEXT,
                    created_at TEXT,
                    updated_at TEXT,
                    closed_at TEXT,
                    merged_at TEXT,
                    repository TEXT,
                    author TEXT,
                    author_id INTEGER,
                    labels TEXT,
                    milestone TEXT,
                    comments_count INTEGER,
                    review_comments_count INTEGER,
                    commits_count INTEGER,
                    additions_count INTEGER,
                    deletions_count INTEGER,
                    changed_files_count INTEGER,
                    curators TEXT,
                    comments TEXT,
                    reviews TEXT,
                    category TEXT,
                    approval_time_days REAL,
                    performance_score REAL,
                    is_stale BOOLEAN,
                    created_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create metrics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_name TEXT UNIQUE,
                    metric_value TEXT,
                    created_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
    
    def save_proposals(self, proposals_data: dict):
        """Save proposals data to storage (cloud or local)"""
        if self.cloud_storage:
            # Use cloud storage
            return self.cloud_storage.save_proposals(proposals_data)
        else:
            # Use local SQLite database
            return self._save_proposals_sqlite(proposals_data)
    
    def _save_proposals_sqlite(self, proposals_data: dict):
        """Save proposals data to SQLite database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Clear existing data
            cursor.execute('DELETE FROM proposals')
            
            # Insert new data
            for repo_key, proposals in proposals_data.items():
                for proposal in proposals:
                    try:
                        # Prepare data for insertion
                        curators_json = json.dumps(proposal.get('curators', []))
                        comments_json = json.dumps(proposal.get('comments', []))
                        reviews_json = json.dumps(proposal.get('reviews', []))
                        labels_json = json.dumps(proposal.get('labels', []))
                        
                        cursor.execute('''
                            INSERT INTO proposals (
                                id, number, title, body, state, created_at, updated_at,
                                closed_at, merged_at, repository, author, author_id,
                                labels, milestone, comments_count, review_comments_count,
                                commits_count, additions_count, deletions_count,
                                changed_files_count, curators, comments, reviews,
                                category, approval_time_days, performance_score, is_stale
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            proposal.get('id'),
                            proposal.get('number'),
                            proposal.get('title', ''),
                            proposal.get('body', ''),
                            proposal.get('state', ''),
                            proposal.get('created_at'),
                            proposal.get('updated_at'),
                            proposal.get('closed_at'),
                            proposal.get('merged_at'),
                            repo_key,
                            proposal.get('author', ''),
                            proposal.get('author_id'),
                            labels_json,
                            proposal.get('milestone', ''),
                            proposal.get('comments_count', 0),
                            proposal.get('review_comments_count', 0),
                            proposal.get('commits_count', 0),
                            proposal.get('additions_count', 0),
                            proposal.get('deletions_count', 0),
                            proposal.get('changed_files_count', 0),
                            curators_json,
                            comments_json,
                            reviews_json,
                            proposal.get('category', ''),
                            proposal.get('approval_time_days'),
                            proposal.get('performance_score', 0.0),
                            proposal.get('is_stale', False)
                        ))
                    except Exception as e:
                        print(f"Error saving proposal {proposal.get('id', 'unknown')}: {e}")
                        continue
            
            conn.commit()
            return True
    
    def load_proposals(self) -> pd.DataFrame:
        """Load proposals from storage (cloud or local)"""
        if self.cloud_storage:
            # Use cloud storage
            return self.cloud_storage.load_proposals()
        else:
            # Use local SQLite database
            return self._load_proposals_sqlite()
    
    def _load_proposals_sqlite(self) -> pd.DataFrame:
        """Load proposals from SQLite database"""
        with sqlite3.connect(self.db_path) as conn:
            query = '''
                SELECT * FROM proposals ORDER BY created_at DESC
            '''
            df = pd.read_sql_query(query, conn)
            
            if not df.empty:
                # Parse JSON columns
                json_columns = ['labels', 'curators', 'comments', 'reviews']
                for col in json_columns:
                    if col in df.columns:
                        df[col] = df[col].apply(lambda x: json.loads(x) if x else [])
                
                # Convert date columns
                date_columns = ['created_at', 'updated_at', 'closed_at', 'merged_at']
                for col in date_columns:
                    if col in df.columns:
                        df[col] = pd.to_datetime(df[col], errors='coerce')
            
            return df
    
    def save_metrics(self, metrics: dict):
        """Save metrics to storage (cloud or local)"""
        if self.cloud_storage:
            # Use cloud storage
            return self.cloud_storage.save_metrics(metrics)
        else:
            # Use local SQLite database
            return self._save_metrics_sqlite(metrics)
    
    def _save_metrics_sqlite(self, metrics: dict):
        """Save metrics to SQLite database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            for metric_name, metric_value in metrics.items():
                # Convert to JSON if it's a complex object
                if isinstance(metric_value, (dict, list)):
                    metric_value = json.dumps(metric_value)
                else:
                    metric_value = str(metric_value)
                
                cursor.execute('''
                    INSERT OR REPLACE INTO metrics (metric_name, metric_value)
                    VALUES (?, ?)
                ''', (metric_name, metric_value))
            
            conn.commit()
            return True
    
    def load_metrics(self) -> dict:
        """Load metrics from storage (cloud or local)"""
        if self.cloud_storage:
            # Use cloud storage
            return self.cloud_storage.load_metrics()
        else:
            # Use local SQLite database
            return self._load_metrics_sqlite()
    
    def _load_metrics_sqlite(self) -> dict:
        """Load metrics from SQLite database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT metric_name, metric_value FROM metrics')
            rows = cursor.fetchall()
            
            metrics = {}
            for metric_name, metric_value in rows:
                try:
                    # Try to parse as JSON first
                    metrics[metric_name] = json.loads(metric_value)
                except (json.JSONDecodeError, TypeError):
                    # If not JSON, keep as string
                    metrics[metric_name] = metric_value
            
            return metrics
    
    def get_database_info(self) -> dict:
        """Get information about the storage"""
        if self.cloud_storage:
            # Get cloud storage info
            info = self.cloud_storage.get_storage_info()
            info['storage_type'] = 'cloud_session_state'
            return info
        else:
            # Get SQLite database info
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get table info
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                
                # Get row counts
                info = {'tables': tables, 'storage_type': 'sqlite'}
                for table in tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    info[f'{table}_count'] = count
                
                # Get database size
                if os.path.exists(self.db_path):
                    info['database_size_mb'] = os.path.getsize(self.db_path) / (1024 * 1024)
                else:
                    info['database_size_mb'] = 0
                
                return info
    
    def clear_database(self):
        """Clear all stored data"""
        if self.cloud_storage:
            # Clear cloud storage
            return self.cloud_storage.clear_storage()
        else:
            # Clear SQLite database
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM proposals')
                cursor.execute('DELETE FROM metrics')
                conn.commit()
            return True
    
    def has_data(self) -> bool:
        """Check if there's any data stored"""
        if self.cloud_storage:
            return self.cloud_storage.has_data()
        else:
            # Check SQLite database
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM proposals')
                count = cursor.fetchone()[0]
                return count > 0
    
    def backup_database(self, backup_path: str):
        """Create a backup of the database (SQLite only)"""
        if not self.cloud_storage:
            import shutil
            shutil.copy2(self.db_path, backup_path)
    
    def restore_database(self, backup_path: str):
        """Restore database from backup (SQLite only)"""
        if not self.cloud_storage:
            import shutil
            shutil.copy2(backup_path, self.db_path) 