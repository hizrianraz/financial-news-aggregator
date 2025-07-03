# News Source Credentials Guide

## Overview

The aggregator works with both free RSS feeds and authenticated premium content. Here's how to set up credentials for each news source if you have subscriptions.

## Credential Types by Source

### 1. Bloomberg
- **Without credentials**: Limited/no RSS access (currently blocked)
- **With credentials**: 
  - Bloomberg Terminal API access
  - Or Bloomberg.com login credentials
  - Format: `username:password` or API key

### 2. CNBC
- **Without credentials**: Some RSS feeds blocked
- **With credentials**:
  - CNBC Pro subscription
  - Format: `email:password`

### 3. Financial Times
- **Without credentials**: Limited RSS feeds (working)
- **With credentials**:
  - FT.com subscription
  - Format: `email:password`
  - Enables full article content

### 4. Wall Street Journal
- **Without credentials**: Public RSS feeds (working)
- **With credentials**:
  - WSJ subscription
  - Format: `email:password`
  - Access to full articles

### 5. Forbes
- **Without credentials**: Public RSS feeds (working)
- **With credentials**: Not typically needed

## How to Add Credentials

### Option 1: Local Testing (.env file)
```bash
# Add to your .env file
BLOOMBERG_CREDENTIALS=your_username:your_password
CNBC_CREDENTIALS=your_email:your_password
FT_CREDENTIALS=your_email:your_password
WSJ_CREDENTIALS=your_email:your_password
```

### Option 2: GitHub Secrets (Production)
Add these as repository secrets:
- `BLOOMBERG_CREDENTIALS`
- `CNBC_CREDENTIALS`
- `FT_CREDENTIALS`
- `WSJ_CREDENTIALS`

## Important Notes

1. **Credentials are OPTIONAL** - The aggregator works without them, just with limited content
2. **Security**: Never commit credentials to your repository
3. **Format**: Most use `email:password` format
4. **API Keys**: Bloomberg might provide API keys instead of login credentials

## Current Implementation Status

⚠️ **Note**: The current scrapers have placeholder code for authentication but don't fully implement login flows yet. To use credentials effectively, you would need to enhance the scrapers with:

1. Session management
2. Login flows
3. Cookie handling
4. API integration (for Bloomberg)

The RSS feeds provide good coverage for most use cases without needing credentials. 