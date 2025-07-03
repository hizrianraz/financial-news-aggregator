"""
The Economist news scraper
"""

import logging
from typing import List, Dict, Any
from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class EconomistScraper(BaseScraper):
    """Scraper for The Economist news"""
    
    async def scrape(self) -> List[Dict[str, Any]]:
        """Scrape articles from The Economist"""
        async with self:
            articles = []
            
            # The Economist provides RSS feeds for various sections
            if 'rss_feeds' in self.config:
                rss_articles = await self.fetch_rss_feeds(self.config['rss_feeds'])
                articles.extend(rss_articles)
            
            logger.info(f"Scraped {len(articles)} articles from The Economist")
            return articles 