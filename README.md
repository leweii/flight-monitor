# Flight Monitor

A Python-based flight price monitoring system that aggregates data from multiple sources and sends alerts through various notification channels when prices meet your criteria.

## Features

- **Multi-Source Data Aggregation**
  - Amadeus API (real-time pricing)
  - Kiwi.com API
  - AviationStack API (flight tracking)
  - Skyscanner API

- **Multi-Channel Notifications**
  - Console output
  - WeChat (via Server酱)
  - Email (SMTP)
  - Telegram Bot

- **Flexible Alert Rules**
  - Price threshold (alert when price drops below X)
  - Percentage drop (alert when price drops by X%)
  - Historical low (alert when price is lowest in X days)

- **Easy Deployment**
  - Docker Compose support
  - PostgreSQL for price history
  - Configurable via YAML

## Quick Start

### Prerequisites

- Python 3.11+
- API key from [Amadeus](https://developers.amadeus.com/) (free tier available)

### Installation

```bash
git clone https://github.com/leweii/flight-monitor.git
cd flight-monitor
pip install -r requirements.txt
```

### Configuration

1. Set your API keys as environment variables:

```bash
export AMADEUS_CLIENT_ID=your_client_id
export AMADEUS_CLIENT_SECRET=your_client_secret
```

2. Edit `config.yaml` to configure your routes:

```yaml
routes:
  - name: 厦门-新加坡
    origin: XMN          # IATA airport code
    destination: SIN
    check_interval: 1h   # Check every hour
    date_range:
      start: 2026-02-01
      end: 2026-02-28
    alerts:
      - type: threshold
        max_price: 1500
        currency: CNY
```

### Usage

```bash
# Manual price check
python -m src.cli check XMN SIN

# List configured routes
python -m src.cli list-routes

# Start continuous monitoring
python -m src.cli start
```

## Docker Deployment

```bash
# Create .env file with your API keys
cat > .env << EOF
AMADEUS_CLIENT_ID=your_client_id
AMADEUS_CLIENT_SECRET=your_client_secret
EOF

# Start services
docker-compose up -d

# View logs
docker-compose logs -f app
```

## Configuration Reference

### Data Sources

| Source | Description | Sign Up |
|--------|-------------|---------|
| Amadeus | Real-time flight pricing | [developers.amadeus.com](https://developers.amadeus.com/) |
| Kiwi | Flight search API | [tequila.kiwi.com](https://tequila.kiwi.com/) |
| AviationStack | Flight tracking (no pricing) | [aviationstack.com](https://aviationstack.com/) |

### Alert Types

```yaml
alerts:
  # Alert when price is below threshold
  - type: threshold
    max_price: 1500
    currency: CNY

  # Alert when price drops by percentage
  - type: drop_percent
    percent: 10

  # Alert when price is historical low
  - type: historical_low
    lookback_days: 7
```

### Notification Channels

```yaml
notifiers:
  # Console output (always recommended for debugging)
  console:
    enabled: true
    level: INFO

  # WeChat via Server酱 (https://sct.ftqq.com/)
  wechat:
    enabled: true
    push_key: ${WECHAT_PUSH_KEY}

  # Email via SMTP
  email:
    enabled: true
    smtp_host: smtp.gmail.com
    smtp_port: 587
    username: ${EMAIL_USER}
    password: ${EMAIL_PASSWORD}
    recipients:
      - your@email.com

  # Telegram Bot
  telegram:
    enabled: true
    bot_token: ${TELEGRAM_BOT_TOKEN}
    chat_id: ${TELEGRAM_CHAT_ID}
```

## Project Structure

```
flight-monitor/
├── src/
│   ├── fetchers/          # Data source integrations
│   │   ├── amadeus.py
│   │   ├── kiwi.py
│   │   ├── aviationstack.py
│   │   └── aggregator.py
│   ├── analyzers/         # Alert rule engine
│   │   ├── alert_rules.py
│   │   └── engine.py
│   ├── notifiers/         # Notification channels
│   │   ├── console.py
│   │   ├── wechat.py
│   │   └── manager.py
│   ├── cli.py             # Command-line interface
│   ├── scheduler.py       # APScheduler integration
│   └── models.py          # Data models
├── tests/                 # 49 unit tests
├── config.yaml            # Configuration file
├── docker-compose.yaml    # Docker deployment
└── requirements.txt
```

## Adding New Routes

Edit `config.yaml` and add a new route:

```yaml
routes:
  - name: 北京-东京
    origin: PEK
    destination: NRT
    check_interval: 2h
    date_range:
      start: 2026-03-01
      end: 2026-03-15
    alerts:
      - type: threshold
        max_price: 2000
        currency: CNY
```

Common IATA codes:
- PEK (Beijing), PVG (Shanghai), CAN (Guangzhou), SZX (Shenzhen), XMN (Xiamen)
- NRT/HND (Tokyo), ICN (Seoul), SIN (Singapore), BKK (Bangkok), KUL (Kuala Lumpur)

## Development

```bash
# Run tests
pytest tests/ -v

# Run specific test file
pytest tests/test_fetchers_amadeus.py -v
```

## License

MIT
