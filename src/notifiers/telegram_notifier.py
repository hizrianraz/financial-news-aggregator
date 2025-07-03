"""
Telegram notifier for sending news updates
"""

import logging
from typing import List, Dict, Any
import asyncio
from telegram import Bot
from telegram.constants import ParseMode

logger = logging.getLogger(__name__)


class TelegramNotifier:
    """Send notifications to Telegram"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize Telegram notifier"""
        self.config = config
        self.bot = Bot(token=config['bot_token'])
        self.chat_id = config['chat_id']
        
    async def send_notification(self, articles: List[Dict[str, Any]]):
        """Send articles to Telegram"""
        try:
            if not articles:
                return
                
            # Format message
            message = self._format_message(articles)
            
            # Split message if too long
            max_length = self.config.get('max_message_length', 4096)
            
            if len(message) <= max_length:
                await self.bot.send_message(
                    chat_id=self.chat_id,
                    text=message,
                    parse_mode=ParseMode.MARKDOWN_V2,
                    disable_web_page_preview=True
                )
            else:
                # Split into multiple messages
                chunks = self._split_message(message, max_length)
                for chunk in chunks:
                    await self.bot.send_message(
                        chat_id=self.chat_id,
                        text=chunk,
                        parse_mode=ParseMode.MARKDOWN_V2,
                        disable_web_page_preview=True
                    )
                    await asyncio.sleep(0.5)  # Avoid rate limiting
                    
            logger.info(f"Sent {len(articles)} articles to Telegram")
            
        except Exception as e:
            logger.error(f"Error sending Telegram notification: {e}")
            raise
            
    def _format_message(self, articles: List[Dict[str, Any]]) -> str:
        """Format articles for Telegram"""
        lines = ["📰 *Financial News Update*\n"]
        
        for article in articles:
            # Escape special characters for Markdown V2
            title = self._escape_markdown(article['title'])
            source = self._escape_markdown(article['source'].upper())
            url = article['url']
            
            # Add priority indicator
            if article.get('priority', 0) > 0:
                lines.append(f"🔴 *{source}*: [{title}]({url})")
            else:
                lines.append(f"▫️ *{source}*: [{title}]({url})")
                
            if self.config.get('include_summary') and article.get('description'):
                description = self._escape_markdown(article['description'][:200])
                lines.append(f"   _{description}_\n")
            else:
                lines.append("")
                
        return "\n".join(lines)
        
    def _escape_markdown(self, text: str) -> str:
        """Escape special characters for Telegram Markdown V2"""
        escape_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
        for char in escape_chars:
            text = text.replace(char, f'\\{char}')
        return text
        
    def _split_message(self, message: str, max_length: int) -> List[str]:
        """Split long message into chunks"""
        chunks = []
        lines = message.split('\n')
        current_chunk = []
        current_length = 0
        
        for line in lines:
            line_length = len(line) + 1  # +1 for newline
            
            if current_length + line_length > max_length:
                # Start new chunk
                chunks.append('\n'.join(current_chunk))
                current_chunk = [line]
                current_length = line_length
            else:
                current_chunk.append(line)
                current_length += line_length
                
        if current_chunk:
            chunks.append('\n'.join(current_chunk))
            
        return chunks 