# Financial News Aggregator Setup Guide

This guide will walk you through setting up the Financial News Aggregator with GitHub Actions, Telegram, and Slack integration.

## Prerequisites

1. GitHub account with a repository for this project
2. Telegram Bot (for Telegram notifications)
3. Slack Workspace with incoming webhooks enabled
4. Subscriptions to news sources (Bloomberg, CNBC, FT, WSJ, Forbes)

## Step 1: Set up Telegram Bot

1. Open Telegram and search for `@BotFather`
2. Send `/newbot` command
3. Choose a name for your bot (e.g., "Financial News Bot")
4. Choose a username for your bot (must end in 'bot')
5. Save the bot token provided by BotFather

### Get Telegram Chat ID

1. Add your bot to a channel or group (or message it directly)
2. Send a test message
3. Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
4. Find the `chat_id` in the response

## Step 2: Set up Slack Webhook

1. Go to your Slack workspace
2. Navigate to: Apps → Custom Integrations → Incoming Webhooks
3. Click "Add to Slack"
4. Choose a channel for notifications
5. Copy the Webhook URL

## Step 3: Configure GitHub Secrets

In your GitHub repository:

1. Go to Settings → Secrets and variables → Actions
2. Add the following secrets:

   - `TELEGRAM_BOT_TOKEN`: Your Telegram bot token
   - `TELEGRAM_CHAT_ID`: Your Telegram chat/channel ID
   - `SLACK_WEBHOOK_URL`: Your Slack webhook URL

### Optional: News Source Credentials

If you have API access or credentials for the news sources:

   - `BLOOMBERG_CREDENTIALS`: Bloomberg API credentials
   - `CNBC_CREDENTIALS`: CNBC Pro credentials
   - `FT_CREDENTIALS`: Financial Times credentials
   - `WSJ_CREDENTIALS`: Wall Street Journal credentials
   - `FORBES_CREDENTIALS`: Forbes credentials

## Step 4: Customize Configuration

Edit `config.yaml` to customize:

- **News sources**: Enable/disable specific sources
- **Categories**: Choose which news categories to track
- **Schedule**: Modify run times in `.github/workflows/news-aggregator.yml`
- **Filters**: Add keywords to prioritize or exclude
- **Display settings**: Adjust notification format and length

## Step 5: Test the Setup

### Local Testing

```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file with your credentials
cat > .env << EOF
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
SLACK_WEBHOOK_URL=your_slack_webhook_url
EOF

# Run the aggregator
python src/main.py
```

### GitHub Actions Testing

1. Push your changes to GitHub
2. Go to Actions tab in your repository
3. Select "Financial News Aggregator" workflow
4. Click "Run workflow" → "Run workflow"
5. Monitor the workflow execution

## Step 6: Monitor and Maintain

- Check GitHub Actions logs for any errors
- Monitor the `data/processed_articles.json` file for duplicate tracking
- Adjust `config.yaml` based on your needs
- Update RSS feeds if they change

## Troubleshooting

### No notifications received

1. Check GitHub Actions logs for errors
2. Verify all secrets are set correctly
3. Test bot/webhook manually
4. Check `aggregator.log` for detailed errors

### Duplicate articles

- Increase `duplicate_threshold_hours` in config
- Check if article IDs are being generated correctly

### Rate limiting

- Reduce `max_articles_per_run` for each source
- Add delays between notifications
- Use fewer RSS feeds

## Advanced Configuration

### Custom News Sources

To add a new news source:

1. Create a new scraper in `src/scrapers/`
2. Inherit from `BaseScraper`
3. Implement the `scrape()` method
4. Add configuration in `config.yaml`
5. Import and initialize in `src/main.py`

### Authentication for Premium Content

For sources requiring authentication:

1. Implement login logic in the scraper
2. Store credentials as GitHub secrets
3. Use session management for authenticated requests
4. Consider using Selenium for JavaScript-heavy sites

### Custom Notification Formats

Modify notification formatting in:
- `src/notifiers/telegram_notifier.py` for Telegram
- `src/notifiers/slack_notifier.py` for Slack

## Security Best Practices

1. Never commit credentials to the repository
2. Use GitHub Secrets for all sensitive data
3. Regularly rotate API keys and tokens
4. Monitor access logs for suspicious activity
5. Use read-only credentials where possible

## Support

For issues or questions:
1. Check the GitHub Actions logs
2. Review this setup guide
3. Check the configuration in `config.yaml`
4. Open an issue in the repository 