"""
Base scraper class for all news sources
"""

import logging
import hashlib
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict, Any
import aiohttp
import feedparser
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """Abstract base class for news scrapers"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the scraper with configuration"""
        self.config = config
        self.source_name = self.__class__.__name__.replace('Scraper', '').lower()
        self.session = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
            
    @abstractmethod
    async def scrape(self) -> List[Dict[str, Any]]:
        """Scrape articles from the news source"""
        pass
        
    async def fetch_rss_feeds(self, feed_urls: List[str]) -> List[Dict[str, Any]]:
        """Fetch and parse RSS feeds"""
        articles = []
        
        for feed_url in feed_urls:
            try:
                async with self.session.get(feed_url) as response:
                    if response.status == 200:
                        content = await response.text()
                        feed = feedparser.parse(content)
                        
                        for entry in feed.entries[:self.config.get('max_articles_per_run', 10)]:
                            article = self._parse_rss_entry(entry)
                            if article:
                                articles.append(article)
                    else:
                        logger.warning(f"Failed to fetch RSS feed {feed_url}: {response.status}")
                        
            except Exception as e:
                logger.error(f"Error fetching RSS feed {feed_url}: {e}")
                
        return articles
        
    def _parse_rss_entry(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        """Parse RSS feed entry into article format"""
        try:
            # Generate unique ID
            article_id = self._generate_article_id(entry.get('link', ''))
            
            # Extract basic information
            article = {
                'id': article_id,
                'source': self.source_name,
                'title': entry.get('title', ''),
                'url': entry.get('link', ''),
                'description': self._clean_html(entry.get('summary', '')),
                'timestamp': self._parse_date(entry.get('published', entry.get('updated', ''))),
                'categories': [tag.term for tag in entry.get('tags', [])],
                'author': entry.get('author', ''),
                'scraped_at': datetime.utcnow().isoformat()
            }
            
            # Check for priority keywords
            article['priority'] = self._calculate_priority(article)
            
            return article
            
        except Exception as e:
            logger.error(f"Error parsing RSS entry: {e}")
            return None
            
    def _generate_article_id(self, url: str) -> str:
        """Generate unique article ID from URL"""
        return hashlib.md5(url.encode()).hexdigest()
        
    def _clean_html(self, html_text: str) -> str:
        """Remove HTML tags from text"""
        if not html_text:
            return ''
        soup = BeautifulSoup(html_text, 'html.parser')
        return soup.get_text().strip()
        
    def _parse_date(self, date_str: str) -> str:
        """Parse date string to ISO format"""
        if not date_str:
            return datetime.utcnow().isoformat()
            
        try:
            # feedparser returns a time struct
            if hasattr(date_str, 'tm_year'):
                return datetime(*date_str[:6]).isoformat()
            else:
                # Try parsing string date
                from dateutil import parser
                return parser.parse(date_str).isoformat()
        except:
            return datetime.utcnow().isoformat()
            
    def _calculate_priority(self, article: Dict[str, Any]) -> int:
        """Calculate article priority based on keywords"""
        priority = 0
        
        # Priority keywords from config
        priority_keywords = ['breaking', 'urgent', 'exclusive', 'alert']
        
        text = (article.get('title', '') + ' ' + article.get('description', '')).lower()
        
        for keyword in priority_keywords:
            if keyword in text:
                priority += 10
                
        return priority 