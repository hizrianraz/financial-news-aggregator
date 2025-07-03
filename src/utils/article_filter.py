"""
Article filtering utilities
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class ArticleFilter:
    """Filter and deduplicate articles"""
    
    def __init__(self, config: Dict[str, Any], storage):
        """Initialize article filter"""
        self.config = config
        self.storage = storage
        self.filters = config.get('filters', {})
        
    def filter_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply all filters to articles"""
        filtered = []
        
        for article in articles:
            # Check if already processed
            if self._is_duplicate(article):
                logger.debug(f"Skipping duplicate article: {article['title']}")
                continue
                
            # Check exclude keywords
            if self._contains_excluded_keywords(article):
                logger.debug(f"Skipping excluded article: {article['title']}")
                continue
                
            # Check if article is recent enough
            if not self._is_recent(article):
                logger.debug(f"Skipping old article: {article['title']}")
                continue
                
            # Apply priority keywords
            self._apply_priority_keywords(article)
            
            filtered.append(article)
            
        return filtered
        
    def _is_duplicate(self, article: Dict[str, Any]) -> bool:
        """Check if article has been processed recently"""
        article_id = article.get('id')
        if not article_id:
            return False
            
        return self.storage.is_processed(article_id)
        
    def _contains_excluded_keywords(self, article: Dict[str, Any]) -> bool:
        """Check if article contains excluded keywords"""
        exclude_keywords = self.filters.get('exclude_keywords', [])
        if not exclude_keywords:
            return False
            
        text = (article.get('title', '') + ' ' + article.get('description', '')).lower()
        
        for keyword in exclude_keywords:
            if keyword.lower() in text:
                return True
                
        return False
        
    def _is_recent(self, article: Dict[str, Any]) -> bool:
        """Check if article is recent enough"""
        duplicate_threshold = self.filters.get('duplicate_threshold_hours', 24)
        
        try:
            # Parse article timestamp
            timestamp_str = article.get('timestamp')
            if not timestamp_str:
                return True  # Assume recent if no timestamp
                
            article_time = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            # Make cutoff_time timezone-aware
            cutoff_time = datetime.utcnow().replace(tzinfo=None)
            
            # Convert both to naive for comparison if needed
            if article_time.tzinfo:
                article_time = article_time.replace(tzinfo=None)
                
            return article_time > cutoff_time - timedelta(hours=duplicate_threshold)
            
        except Exception as e:
            logger.error(f"Error parsing timestamp: {e}")
            return True  # Assume recent on error
            
    def _apply_priority_keywords(self, article: Dict[str, Any]):
        """Apply priority based on keywords"""
        priority_keywords = self.filters.get('priority_keywords', [])
        if not priority_keywords:
            return
            
        text = (article.get('title', '') + ' ' + article.get('description', '')).lower()
        
        for keyword in priority_keywords:
            if keyword.lower() in text:
                article['priority'] = article.get('priority', 0) + 10 