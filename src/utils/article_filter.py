"""
Article filtering utilities with enhanced duplicate detection
"""

import logging
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Set
from difflib import SequenceMatcher
from .duplicate_stats import DuplicateStats

logger = logging.getLogger(__name__)


class ArticleFilter:
    """Filter and deduplicate articles"""
    
    def __init__(self, config: Dict[str, Any], storage):
        """Initialize article filter"""
        self.config = config
        self.storage = storage
        self.filters = config.get('filters', {})
        self.similarity_threshold = self.filters.get('similarity_threshold', 0.75)
        
    def filter_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply all filters to articles"""
        stats = DuplicateStats()
        stats.total_articles = len(articles)
        
        filtered = []
        seen_titles = []  # Track titles we've already seen
        
        # Sort articles by priority and timestamp to keep the best version
        sorted_articles = sorted(
            articles, 
            key=lambda x: (x.get('priority', 0), x.get('timestamp', '')), 
            reverse=True
        )
        
        for article in sorted_articles:
            # Check if already processed
            if self._is_duplicate(article):
                logger.debug(f"Skipping duplicate article: {article['title']}")
                stats.duplicates_by_id += 1
                continue
                
            # Check for similar articles already in filtered list
            if self._is_similar_to_existing(article, seen_titles):
                logger.debug(f"Skipping similar article: {article['title']}")
                stats.duplicates_by_similarity += 1
                continue
                
            # Check exclude keywords
            if self._contains_excluded_keywords(article):
                logger.debug(f"Skipping excluded article: {article['title']}")
                stats.excluded_by_keywords += 1
                continue
                
            # Check required keywords
            if not self._contains_required_keywords(article):
                logger.debug(f"Skipping article without required keywords: {article['title']}")
                stats.excluded_by_requirements += 1
                continue
                
            # Check if article is recent enough
            if not self._is_recent(article):
                logger.debug(f"Skipping old article: {article['title']}")
                stats.excluded_by_age += 1
                continue
                
            # Apply priority keywords
            self._apply_priority_keywords(article)
            
            # Add to filtered list and track title
            filtered.append(article)
            seen_titles.append({
                'title': article.get('title', ''),
                'description': article.get('description', '')
            })
            
        stats.final_count = len(filtered)
        stats.log_stats()
        
        return filtered
        
    def _is_duplicate(self, article: Dict[str, Any]) -> bool:
        """Check if article has been processed recently"""
        article_id = article.get('id')
        if not article_id:
            return False
            
        return self.storage.is_processed(article_id)
        
    def _is_similar_to_existing(self, article: Dict[str, Any], seen_titles: List[Dict[str, str]]) -> bool:
        """Check if article is similar to already filtered articles"""
        article_title = self._normalize_text(article.get('title', ''))
        article_desc = self._normalize_text(article.get('description', ''))
        
        for seen in seen_titles:
            seen_title = self._normalize_text(seen['title'])
            seen_desc = self._normalize_text(seen['description'])
            
            # Check title similarity
            title_similarity = self._calculate_similarity(article_title, seen_title)
            if title_similarity > self.similarity_threshold:
                return True
                
            # Check if titles contain same key information
            if self._contains_same_key_info(article_title, seen_title):
                return True
                
            # Check description similarity if both are substantial
            if len(article_desc) > 50 and len(seen_desc) > 50:
                desc_similarity = self._calculate_similarity(article_desc[:200], seen_desc[:200])
                if desc_similarity > 0.8:  # Higher threshold for descriptions
                    return True
                    
        return False
        
    def _normalize_text(self, text: str) -> str:
        """Normalize text for comparison"""
        if not text:
            return ''
            
        # Convert to lowercase
        text = text.lower()
        
        # Remove source prefixes like "Bloomberg: " or "WSJ - "
        text = re.sub(r'^[^:]+:\s*', '', text)
        text = re.sub(r'^[^-]+-\s*', '', text)
        
        # Remove common news phrases
        remove_phrases = [
            'breaking:', 'exclusive:', 'update:', 'alert:', 'just in:',
            'sources say', 'report says', 'according to'
        ]
        for phrase in remove_phrases:
            text = text.replace(phrase, '')
            
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text.strip()
        
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts"""
        if not text1 or not text2:
            return 0.0
        return SequenceMatcher(None, text1, text2).ratio()
        
    def _contains_same_key_info(self, title1: str, title2: str) -> bool:
        """Check if titles contain the same key information (companies, numbers, etc.)"""
        # Extract key entities (companies, large numbers, percentages)
        pattern = r'\b(?:[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*|(?:\d+\.?\d*)[%$]?(?:\s*(?:billion|million|trillion|bn|mn))?)\b'
        
        entities1 = set(re.findall(pattern, title1))
        entities2 = set(re.findall(pattern, title2))
        
        # Remove common words that might be falsely detected as entities
        common_words = {'The', 'This', 'That', 'These', 'Those', 'After', 'Before', 'During'}
        entities1 = entities1 - common_words
        entities2 = entities2 - common_words
        
        # If both titles have substantial entities and share most of them, they're likely duplicates
        if len(entities1) >= 2 and len(entities2) >= 2:
            intersection = entities1 & entities2
            if len(intersection) >= min(len(entities1), len(entities2)) * 0.6:
                return True
                
        return False
        
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
        
    def _contains_required_keywords(self, article: Dict[str, Any]) -> bool:
        """Check if article contains at least one required keyword"""
        required_keywords = self.filters.get('required_keywords', [])
        if not required_keywords:
            return True  # If no required keywords configured, accept all
            
        text = (article.get('title', '') + ' ' + article.get('description', '')).lower()
        
        # Check if at least one required keyword is present
        for keyword in required_keywords:
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
        
        priority = 0
        for keyword in priority_keywords:
            if keyword.lower() in text:
                priority += 10
                
        article['priority'] = article.get('priority', 0) + priority 