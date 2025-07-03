#!/usr/bin/env python3
"""
Test script to verify the news aggregator setup
"""

import os
import sys
import asyncio
import aiohttp
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


async def test_telegram():
    """Test Telegram bot configuration"""
    print("\n🔍 Testing Telegram configuration...")
    
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if not bot_token:
        print("❌ TELEGRAM_BOT_TOKEN not found in environment")
        return False
        
    if not chat_id:
        print("❌ TELEGRAM_CHAT_ID not found in environment")
        return False
        
    # Test bot token validity
    try:
        async with aiohttp.ClientSession() as session:
            url = f"https://api.telegram.org/bot{bot_token}/getMe"
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Telegram bot valid: @{data['result']['username']}")
                    
                    # Test sending a message
                    send_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
                    payload = {
                        'chat_id': chat_id,
                        'text': '✅ News Aggregator test message - Setup successful!'
                    }
                    async with session.post(send_url, json=payload) as send_response:
                        if send_response.status == 200:
                            print(f"✅ Test message sent to Telegram chat {chat_id}")
                            return True
                        else:
                            error = await send_response.text()
                            print(f"❌ Failed to send test message: {error}")
                            return False
                else:
                    print(f"❌ Invalid Telegram bot token")
                    return False
    except Exception as e:
        print(f"❌ Telegram test failed: {e}")
        return False


async def test_slack():
    """Test Slack webhook configuration"""
    print("\n🔍 Testing Slack configuration...")
    
    webhook_url = os.getenv('SLACK_WEBHOOK_URL')
    
    if not webhook_url:
        print("❌ SLACK_WEBHOOK_URL not found in environment")
        return False
        
    # Test webhook
    try:
        async with aiohttp.ClientSession() as session:
            payload = {
                'text': '✅ News Aggregator test message - Setup successful!'
            }
            async with session.post(webhook_url, json=payload) as response:
                if response.status == 200:
                    print("✅ Test message sent to Slack")
                    return True
                else:
                    error = await response.text()
                    print(f"❌ Slack webhook failed: {error}")
                    return False
    except Exception as e:
        print(f"❌ Slack test failed: {e}")
        return False


def test_config_file():
    """Test configuration file"""
    print("\n🔍 Testing configuration file...")
    
    if not os.path.exists('config.yaml'):
        print("❌ config.yaml not found")
        return False
        
    try:
        import yaml
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
            
        # Check essential config sections
        required_sections = ['sources', 'notifications', 'filters', 'storage']
        for section in required_sections:
            if section not in config:
                print(f"❌ Missing '{section}' section in config.yaml")
                return False
                
        print("✅ config.yaml is valid")
        return True
        
    except Exception as e:
        print(f"❌ Error reading config.yaml: {e}")
        return False


def test_dependencies():
    """Test if all dependencies are installed"""
    print("\n🔍 Testing dependencies...")
    
    required_packages = [
        'requests', 'beautifulsoup4', 'feedparser', 
        'aiohttp', 'pyyaml', 'python-dotenv'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing.append(package)
            
    if missing:
        print(f"❌ Missing packages: {', '.join(missing)}")
        print(f"   Run: pip install -r requirements.txt")
        return False
    else:
        print("✅ All required packages installed")
        return True


async def main():
    """Run all tests"""
    print("🚀 Financial News Aggregator Setup Test")
    print("=" * 40)
    
    results = []
    
    # Test dependencies
    results.append(test_dependencies())
    
    # Test config file
    results.append(test_config_file())
    
    # Test Telegram
    results.append(await test_telegram())
    
    # Test Slack
    results.append(await test_slack())
    
    # Summary
    print("\n" + "=" * 40)
    print("📊 Test Summary:")
    
    if all(results):
        print("✅ All tests passed! Your setup is ready.")
        print("\nNext steps:")
        print("1. Push your code to GitHub")
        print("2. Add secrets to your GitHub repository")
        print("3. Enable GitHub Actions")
        print("4. The aggregator will run on schedule or manually")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        print("\nRefer to SETUP_GUIDE.md for detailed instructions.")


if __name__ == "__main__":
    asyncio.run(main()) 