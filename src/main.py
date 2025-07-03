#!/usr/bin/env python3
"""
Financial News Aggregator Main Entry Point
"""

import os
import sys
import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any
import yaml
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scrapers.bloomberg_scraper import BloombergScraper
from scrapers.cnbc_scraper import CNBCScraper
from scrapers.ft_scraper import FTScraper
from scrapers.wsj_scraper import WSJScraper
from scrapers.forbes_scraper import ForbesScraper
from scrapers.economist_scraper import EconomistScraper
from notifiers.telegram_notifier import TelegramNotifier
from notifiers.slack_notifier import SlackNotifier
from utils.article_filter import ArticleFilter
from utils.storage import Storage

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('aggregator.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class NewsAggregator:
    """Main news aggregator class"""
    
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize the news aggregator"""
        self.config = self._load_config(config_path)
        self.storage = Storage(self.config['storage']['history_file'])
        self.filter = ArticleFilter(self.config, self.storage)
        self.scrapers = self._initialize_scrapers()
        self.notifiers = self._initialize_notifiers()
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            raise
            
    def _initialize_scrapers(self) -> List:
        """Initialize all enabled news scrapers"""
        scrapers = []
        
        if self.config['sources']['bloomberg']['enabled']:
            scrapers.append(BloombergScraper(self.config['sources']['bloomberg']))
            
        if self.config['sources']['cnbc']['enabled']:
            scrapers.append(CNBCScraper(self.config['sources']['cnbc']))
            
        if self.config['sources']['ft']['enabled']:
            scrapers.append(FTScraper(self.config['sources']['ft']))
            
        if self.config['sources']['wsj']['enabled']:
            scrapers.append(WSJScraper(self.config['sources']['wsj']))
            
        if self.config['sources']['forbes']['enabled']:
            scrapers.append(ForbesScraper(self.config['sources']['forbes']))
            
        if self.config['sources']['economist']['enabled']:
            scrapers.append(EconomistScraper(self.config['sources']['economist']))
            
        return scrapers
        
    def _initialize_notifiers(self) -> List:
        """Initialize all enabled notifiers"""
        notifiers = []
        
        if self.config['notifications']['telegram']['enabled']:
            telegram_config = self.config['notifications']['telegram']
            telegram_config['bot_token'] = os.getenv('TELEGRAM_BOT_TOKEN')
            telegram_config['chat_id'] = os.getenv('TELEGRAM_CHAT_ID')
            if telegram_config['bot_token'] and telegram_config['chat_id']:
                notifiers.append(TelegramNotifier(telegram_config))
            else:
                logger.warning("Telegram credentials not found in environment")
                
        if self.config['notifications']['slack']['enabled']:
            slack_config = self.config['notifications']['slack']
            slack_config['webhook_url'] = os.getenv('SLACK_WEBHOOK_URL')
            if slack_config['webhook_url']:
                notifiers.append(SlackNotifier(slack_config))
            else:
                logger.warning("Slack webhook URL not found in environment")
                
        return notifiers
        
    async def aggregate_news(self) -> List[Dict[str, Any]]:
        """Aggregate news from all sources"""
        all_articles = []
        
        # Run all scrapers concurrently
        tasks = []
        for scraper in self.scrapers:
            tasks.append(scraper.scrape())
            
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Scraper {self.scrapers[i].__class__.__name__} failed: {result}")
            else:
                all_articles.extend(result)
                
        logger.info(f"Collected {len(all_articles)} articles total")
        
        # Filter articles
        filtered_articles = self.filter.filter_articles(all_articles)
        logger.info(f"Filtered to {len(filtered_articles)} articles")
        
        # Sort by priority and timestamp
        filtered_articles.sort(key=lambda x: (x.get('priority', 0), x.get('timestamp', '')), reverse=True)
        
        # Limit to max articles per notification
        max_articles = self.config['display']['max_articles_per_notification']
        if len(filtered_articles) > max_articles:
            filtered_articles = filtered_articles[:max_articles]
            
        return filtered_articles
        
    async def notify(self, articles: List[Dict[str, Any]]):
        """Send notifications to all configured channels"""
        if not articles:
            logger.info("No new articles to notify")
            return
            
        # Notify all channels concurrently
        tasks = []
        for notifier in self.notifiers:
            tasks.append(notifier.send_notification(articles))
            
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Notifier {self.notifiers[i].__class__.__name__} failed: {result}")
                
    async def run(self):
        """Main execution method"""
        logger.info("Starting news aggregation...")
        
        try:
            # Aggregate news
            articles = await self.aggregate_news()
            
            # Send notifications
            await self.notify(articles)
            
            # Update storage with processed articles
            for article in articles:
                self.storage.add_processed_article(article['id'])
                
            # Clean up old history
            self.storage.cleanup_old_entries(self.config['storage']['history_retention_days'])
            
            logger.info("News aggregation completed successfully")
            
        except Exception as e:
            logger.error(f"Error during news aggregation: {e}")
            raise


async def main():
    """Main entry point"""
    aggregator = NewsAggregator()
    await aggregator.run()


if __name__ == "__main__":
    asyncio.run(main()) 