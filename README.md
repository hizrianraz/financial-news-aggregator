# Financial News Aggregator

An automated news aggregator that collects articles from major financial news sources and delivers them to Telegram and Slack channels using GitHub Actions.

## Features

- Aggregates news from:
  - Bloomberg
  - CNBC
  - Financial Times (FT)
  - Wall Street Journal (WSJ)
  - Forbes
- Automated scheduling via GitHub Actions
- Delivers to Telegram and Slack
- Filters duplicate articles
- Customizable news categories

## Setup

### Prerequisites

1. Active subscriptions to all news sources
2. Telegram Bot Token
3. Slack Webhook URL
4. GitHub repository with Actions enabled

### Environment Variables

Set these secrets in your GitHub repository:

- `TELEGRAM_BOT_TOKEN`: Your Telegram bot token
- `TELEGRAM_CHAT_ID`: Your Telegram channel/chat ID
- `SLACK_WEBHOOK_URL`: Your Slack webhook URL
- `BLOOMBERG_CREDENTIALS`: Bloomberg login credentials (if needed)
- `CNBC_CREDENTIALS`: CNBC Pro credentials (if needed)
- `FT_CREDENTIALS`: Financial Times credentials
- `WSJ_CREDENTIALS`: Wall Street Journal credentials
- `FORBES_CREDENTIALS`: Forbes credentials (if needed)

### Installation

```bash
pip install -r requirements.txt
```

## Usage

The aggregator runs automatically via GitHub Actions on a schedule. You can also run it manually:

```bash
python src/main.py
```

## Configuration

Edit `config.yaml` to customize:
- News categories
- Update frequency
- Article limits
- Notification preferences

## License

MIT License 