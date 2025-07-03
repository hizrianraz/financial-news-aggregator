# Financial News Aggregator

An automated news aggregator that collects articles from major financial news sources and delivers them to Telegram and Slack channels using GitHub Actions.

## Features

- **Aggregates news from 6 major sources:**
  - Bloomberg
  - CNBC
  - Financial Times (FT)
  - Wall Street Journal (WSJ)
  - Forbes
  - The Economist
  
- **Focused on specific categories:**
  - 💹 Market & Finance (stocks, bonds, trading, investments)
  - 🏛️ Politics (elections, policy, regulation)
  - 🪙 Crypto (Bitcoin, blockchain, DeFi, Web3)
  - 🤖 Tech & AI (artificial intelligence, startups, innovation)
  - 🚀 Aerospace & Defence (space, military, satellites)
  - 💼 Private Equity (VC, PE, buyouts, funds)

- **Smart filtering system:**
  - Required keyword matching for relevance
  - Duplicate article detection
  - Priority scoring for breaking news
  - Excludes lifestyle, entertainment, and off-topic content

- **Automated scheduling:**
  - Runs 6 times daily aligned with market hours
  - 5 AM UTC (Pre-market US)
  - 8 AM UTC (European markets)
  - 1 PM UTC (US market open)
  - 4 PM UTC (Mid US trading)
  - 8 PM UTC (US market close)
  - 11 PM UTC (Asia pre-market)

- **Multi-channel delivery:**
  - Telegram with rich formatting
  - Slack with block formatting
  - Up to 25 articles per notification

## Quick Start

### Prerequisites

1. Active GitHub repository
2. Telegram Bot Token (create via @BotFather)
3. Slack Webhook URL (optional)
4. News source subscriptions (optional for enhanced content)

### Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/financial-news-aggregator.git
   cd financial-news-aggregator
   ```

2. **Configure GitHub Secrets:**
   - `TELEGRAM_BOT_TOKEN`: Your Telegram bot token
   - `TELEGRAM_CHAT_ID`: Your Telegram channel/chat ID
   - `SLACK_WEBHOOK_URL`: Your Slack webhook URL (optional)

3. **Test locally:**
   ```bash
   pip install -r requirements.txt
   python test_setup.py
   ```

4. **Deploy:**
   - Push to GitHub
   - GitHub Actions will run automatically on schedule

## Configuration

Edit `config.yaml` to customize:

- **News sources**: Enable/disable specific sources
- **Categories**: Adjust RSS feeds per source
- **Filters**: 
  - `priority_keywords`: Keywords that boost article ranking
  - `exclude_keywords`: Keywords that filter out articles
  - `required_keywords`: At least one must be present
- **Schedule**: Modify run times in `.github/workflows/news-aggregator.yml`
- **Display**: Article limits and preview settings

### Current Configuration

The aggregator is configured to focus on:
- Financial markets and trading
- Political developments affecting markets
- Cryptocurrency and blockchain
- AI and technology innovation
- Aerospace, defense, and space industry
- Private equity and venture capital

## Architecture

```
financial-news-aggregator/
├── src/
│   ├── main.py                 # Main entry point
│   ├── scrapers/               # News source scrapers
│   │   ├── base_scraper.py     # Base scraper class
│   │   ├── bloomberg_scraper.py
│   │   ├── cnbc_scraper.py
│   │   ├── economist_scraper.py
│   │   ├── forbes_scraper.py
│   │   ├── ft_scraper.py
│   │   └── wsj_scraper.py
│   ├── notifiers/              # Notification handlers
│   │   ├── telegram_notifier.py
│   │   └── slack_notifier.py
│   └── utils/                  # Utility modules
│       ├── article_filter.py   # Filtering logic
│       └── storage.py          # Duplicate tracking
├── .github/workflows/          # GitHub Actions
├── config.yaml                 # Main configuration
├── requirements.txt            # Python dependencies
└── test_setup.py              # Setup verification script
```

## Testing

Run the test script to verify your setup:
```bash
python test_setup.py
```

To test the full aggregation:
```bash
python src/main.py
```

## Troubleshooting

### No articles found
- Check if RSS feeds are accessible
- Verify your filtering keywords aren't too restrictive
- Some sources may require authentication

### Duplicate articles
- The system tracks processed articles in `data/processed_articles.json`
- Adjust `duplicate_threshold_hours` in config

### GitHub Actions failures
- Ensure all secrets are properly set
- Check repository permissions for Actions
- Review workflow logs for specific errors

## Advanced Usage

### Adding Custom Sources
1. Create a new scraper in `src/scrapers/`
2. Inherit from `BaseScraper`
3. Add configuration in `config.yaml`
4. Import in `src/main.py`

### Using Credentials
For full article content, add credentials as GitHub Secrets:
- `BLOOMBERG_CREDENTIALS`
- `CNBC_CREDENTIALS`
- `FT_CREDENTIALS`
- `WSJ_CREDENTIALS`
- `FORBES_CREDENTIALS`

See `CREDENTIALS_GUIDE.md` for details.

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## Support

For issues or questions:
- Check the [Setup Guide](SETUP_GUIDE.md)
- Review GitHub Actions logs
- Open an issue in the repository 