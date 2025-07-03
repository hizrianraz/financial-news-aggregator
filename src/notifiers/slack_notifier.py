"""
Slack notifier for sending news updates
"""

import logging
from typing import List, Dict, Any
import aiohttp
import json

logger = logging.getLogger(__name__)


class SlackNotifier:
    """Send notifications to Slack"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize Slack notifier"""
        self.config = config
        self.webhook_url = config['webhook_url']
        
    async def send_notification(self, articles: List[Dict[str, Any]]):
        """Send articles to Slack"""
        try:
            if not articles:
                return
                
            # Format message for Slack
            payload = self._format_slack_message(articles)
            
            # Send to Slack webhook
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.webhook_url,
                    json=payload,
                    headers={'Content-Type': 'application/json'}
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"Slack webhook failed: {response.status} - {error_text}")
                        
            logger.info(f"Sent {len(articles)} articles to Slack")
            
        except Exception as e:
            logger.error(f"Error sending Slack notification: {e}")
            raise
            
    def _format_slack_message(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Format articles for Slack blocks"""
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "📰 Financial News Update",
                    "emoji": True
                }
            }
        ]
        
        for article in articles:
            # Create article block
            article_text = f"*{article['source'].upper()}*: <{article['url']}|{article['title']}>"
            
            # Add priority indicator
            if article.get('priority', 0) > 0:
                article_text = "🔴 " + article_text
                
            block = {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": article_text
                }
            }
            
            # Add description if configured
            if self.config.get('include_summary') and article.get('description'):
                description = article['description'][:200]
                if len(article['description']) > 200:
                    description += "..."
                    
                block["text"]["text"] += f"\n_{description}_"
                
            blocks.append(block)
            
            # Add divider between articles
            blocks.append({"type": "divider"})
            
        # Remove last divider
        if blocks and blocks[-1]["type"] == "divider":
            blocks.pop()
            
        # Ensure we don't exceed Slack's block limit (50 blocks)
        if len(blocks) > 50:
            blocks = blocks[:49]
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "_... and more articles_"
                }
            })
            
        return {
            "blocks": blocks,
            "text": f"Financial News Update - {len(articles)} new articles"
        } 