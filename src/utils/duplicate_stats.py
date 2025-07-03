"""
Duplicate detection statistics tracker
"""

from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)


class DuplicateStats:
    """Track statistics about duplicate detection"""
    
    def __init__(self):
        self.total_articles = 0
        self.duplicates_by_id = 0
        self.duplicates_by_similarity = 0
        self.excluded_by_keywords = 0
        self.excluded_by_requirements = 0
        self.excluded_by_age = 0
        self.final_count = 0
        
    def log_stats(self):
        """Log the duplicate detection statistics"""
        logger.info("=" * 50)
        logger.info("DUPLICATE DETECTION STATISTICS")
        logger.info("=" * 50)
        logger.info(f"Total articles collected: {self.total_articles}")
        logger.info(f"Removed by duplicate ID: {self.duplicates_by_id}")
        logger.info(f"Removed by similarity: {self.duplicates_by_similarity}")
        logger.info(f"Removed by excluded keywords: {self.excluded_by_keywords}")
        logger.info(f"Removed by missing requirements: {self.excluded_by_requirements}")
        logger.info(f"Removed by age: {self.excluded_by_age}")
        logger.info(f"Final articles: {self.final_count}")
        
        total_removed = (
            self.duplicates_by_id + 
            self.duplicates_by_similarity + 
            self.excluded_by_keywords + 
            self.excluded_by_requirements + 
            self.excluded_by_age
        )
        
        if self.total_articles > 0:
            removal_rate = (total_removed / self.total_articles) * 100
            logger.info(f"Total removal rate: {removal_rate:.1f}%")
            
            if self.duplicates_by_similarity > 0:
                logger.info(f"Cross-source duplicates found: {self.duplicates_by_similarity}")
                
        logger.info("=" * 50) 