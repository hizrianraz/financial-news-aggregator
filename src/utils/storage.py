"""
Storage utilities for tracking processed articles
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Set, Dict, Any

logger = logging.getLogger(__name__)


class Storage:
    """Store and manage processed article IDs"""
    
    def __init__(self, history_file: str):
        """Initialize storage"""
        self.history_file = history_file
        self._ensure_directory()
        self.processed_articles = self._load_history()
        
    def _ensure_directory(self):
        """Ensure data directory exists"""
        directory = os.path.dirname(self.history_file)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
            
    def _load_history(self) -> Dict[str, Any]:
        """Load processed articles history"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading history: {e}")
                return {}
        return {}
        
    def _save_history(self):
        """Save processed articles history"""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.processed_articles, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving history: {e}")
            
    def is_processed(self, article_id: str) -> bool:
        """Check if article has been processed"""
        return article_id in self.processed_articles
        
    def add_processed_article(self, article_id: str):
        """Add article to processed history"""
        self.processed_articles[article_id] = {
            'processed_at': datetime.utcnow().isoformat()
        }
        self._save_history()
        
    def cleanup_old_entries(self, retention_days: int):
        """Remove old entries from history"""
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
        
        # Find entries to remove
        to_remove = []
        for article_id, data in self.processed_articles.items():
            try:
                processed_at = datetime.fromisoformat(data['processed_at'])
                if processed_at < cutoff_date:
                    to_remove.append(article_id)
            except Exception as e:
                logger.error(f"Error parsing date for {article_id}: {e}")
                
        # Remove old entries
        for article_id in to_remove:
            del self.processed_articles[article_id]
            
        if to_remove:
            logger.info(f"Cleaned up {len(to_remove)} old entries")
            self._save_history()