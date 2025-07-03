"""
Forbes news scraper
"""

import logging
from typing import List, Dict, Any
from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class ForbesScraper(BaseScraper):
    """Scraper for Forbes news"""
    
    async def scrape(self) -> List[Dict[str, Any]]:
        """Scrape articles from Forbes"""
        async with self:
            articles = []
            
            # Forbes provides RSS feeds
            if 'rss_feeds' in self.config:
                rss_articles = await self.fetch_rss_feeds(self.config['rss_feeds'])
                articles.extend(rss_articles)
            
            logger.info(f"Scraped {len(articles)} articles from Forbes")
            return articles 