import streamlit as st
import pandas as pd
import json
import pickle
from datetime import datetime
import os
from typing import Dict, List, Optional

class CloudStorage:
    """Cloud-friendly storage system for Streamlit Cloud"""
    
    def __init__(self):
        self.session_state = st.session_state
    
    def _get_storage_key(self, key: str) -> str:
        """Get a namespaced storage key"""
        return f"polkadot_analyzer_{key}"
    
    def save_proposals(self, proposals_data):
        """Save proposals data to session state"""
        try:
            # Convert proposals to a format that can be stored in session state
            processed_data = []
            
            # Handle both dict and DataFrame input
            if isinstance(proposals_data, dict):
                # Original dict format
                for repo_key, proposals in proposals_data.items():
                    for proposal in proposals:
                        try:
                            processed_proposal = {
                                'id': proposal.get('id'),
                                'number': proposal.get('number'),
                                'title': proposal.get('title', ''),
                                'body': proposal.get('body', ''),
                                'state': proposal.get('state', ''),
                                'created_at': proposal.get('created_at'),
                                'updated_at': proposal.get('updated_at'),
                                'closed_at': proposal.get('closed_at'),
                                'merged_at': proposal.get('merged_at'),
                                'repository': repo_key,
                                'author': proposal.get('author', ''),
                                'author_id': proposal.get('author_id'),
                                'labels': proposal.get('labels', []),
                                'milestone': proposal.get('milestone', ''),
                                'comments_count': proposal.get('comments_count', 0),
                                'review_comments_count': proposal.get('review_comments_count', 0),
                                'commits_count': proposal.get('commits_count', 0),
                                'additions_count': proposal.get('additions_count', 0),
                                'deletions_count': proposal.get('deletions_count', 0),
                                'changed_files_count': proposal.get('changed_files_count', 0),
                                'curators': proposal.get('curators', []),
                                'comments': proposal.get('comments', []),
                                'reviews': proposal.get('reviews', []),
                                'category': proposal.get('category', 'PENDING'),  # Default to PENDING if not set
                                'approval_time_days': proposal.get('approval_time_days'),
                                'performance_score': proposal.get('performance_score', 0.0),
                                'is_stale': proposal.get('is_stale', False)
                            }
                            processed_data.append(processed_proposal)
                        except Exception as e:
                            print(f"Error processing proposal {proposal.get('id', 'unknown')}: {e}")
                            continue
            else:
                # DataFrame format - convert to list of dicts
                processed_data = proposals_data.to_dict('records')
            
            # Store in session state
            storage_key = self._get_storage_key('proposals')
            self.session_state[storage_key] = processed_data
            
            # Also save as JSON string for backup
            json_key = self._get_storage_key('proposals_json')
            self.session_state[json_key] = json.dumps(processed_data, default=str)
            
            # Save metadata
            metadata = {
                'count': len(processed_data),
                'repositories': list(set(p.get('repository', '') for p in processed_data)),
                'last_updated': datetime.now().isoformat(),
                'total_proposals': len(processed_data)
            }
            self.session_state[self._get_storage_key('metadata')] = metadata
            
            print(f"Saved {len(processed_data)} proposals to cloud storage")
            return True
            
        except Exception as e:
            print(f"Error saving proposals to cloud storage: {e}")
            return False
    
    def load_proposals(self) -> pd.DataFrame:
        """Load proposals from session state"""
        try:
            # Try to load from session state
            storage_key = self._get_storage_key('proposals')
            
            if storage_key in self.session_state:
                data = self.session_state[storage_key]
            else:
                # Try to load from JSON backup
                json_key = self._get_storage_key('proposals_json')
                if json_key in self.session_state:
                    data = json.loads(self.session_state[json_key])
                else:
                    # Return empty DataFrame
                    return pd.DataFrame()
            
            if not data:
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.DataFrame(data)
            
            if not df.empty:
                # Convert date columns
                date_columns = ['created_at', 'updated_at', 'closed_at', 'merged_at']
                for col in date_columns:
                    if col in df.columns:
                        df[col] = pd.to_datetime(df[col], errors='coerce')
            
            return df
            
        except Exception as e:
            print(f"Error loading proposals from cloud storage: {e}")
            return pd.DataFrame()
    
    def save_metrics(self, metrics: dict):
        """Save metrics to session state"""
        try:
            storage_key = self._get_storage_key('metrics')
            self.session_state[storage_key] = metrics
            
            # Also save as JSON
            json_key = self._get_storage_key('metrics_json')
            self.session_state[json_key] = json.dumps(metrics, default=str)
            
            print(f"Saved {len(metrics)} metrics to cloud storage")
            return True
            
        except Exception as e:
            print(f"Error saving metrics to cloud storage: {e}")
            return False
    
    def load_metrics(self) -> dict:
        """Load metrics from session state"""
        try:
            storage_key = self._get_storage_key('metrics')
            
            if storage_key in self.session_state:
                return self.session_state[storage_key]
            else:
                # Try to load from JSON backup
                json_key = self._get_storage_key('metrics_json')
                if json_key in self.session_state:
                    return json.loads(self.session_state[json_key])
                else:
                    return {}
                    
        except Exception as e:
            print(f"Error loading metrics from cloud storage: {e}")
            return {}
    
    def get_storage_info(self) -> dict:
        """Get information about stored data"""
        info = {
            'proposals_count': 0,
            'metrics_count': 0,
            'last_updated': None,
            'storage_type': 'session_state'
        }
        
        try:
            # Check proposals
            storage_key = self._get_storage_key('proposals')
            if storage_key in self.session_state:
                info['proposals_count'] = len(self.session_state[storage_key])
            
            # Check metrics
            metrics_key = self._get_storage_key('metrics')
            if metrics_key in self.session_state:
                info['metrics_count'] = len(self.session_state[metrics_key])
            
            # Check metadata
            metadata_key = self._get_storage_key('metadata')
            if metadata_key in self.session_state:
                metadata = self.session_state[metadata_key]
                info['last_updated'] = metadata.get('last_updated')
                info['repositories'] = metadata.get('repositories', [])
            
        except Exception as e:
            print(f"Error getting storage info: {e}")
        
        return info
    
    def clear_storage(self):
        """Clear all stored data"""
        try:
            keys_to_clear = [
                self._get_storage_key('proposals'),
                self._get_storage_key('proposals_json'),
                self._get_storage_key('metrics'),
                self._get_storage_key('metrics_json'),
                self._get_storage_key('metadata')
            ]
            
            for key in keys_to_clear:
                if key in self.session_state:
                    del self.session_state[key]
            
            print("Cleared all cloud storage data")
            return True
            
        except Exception as e:
            print(f"Error clearing cloud storage: {e}")
            return False
    
    def has_data(self) -> bool:
        """Check if there's any data stored"""
        storage_key = self._get_storage_key('proposals')
        return storage_key in self.session_state and len(self.session_state[storage_key]) > 0 