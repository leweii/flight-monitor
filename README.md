# Flight Monitor

Flight price monitoring system with multi-source data aggregation and multi-channel notifications.

## Features

- **Multi-source data aggregation**: Amadeus (pricing), AviationStack (tracking), Kiwi, Skyscanner
- **Multi-channel notifications**: Console, WeChat (Server酱), Email, Telegram
- **Flexible alert rules**: Price threshold, percentage drop, historical low
- **Docker deployment**: App + PostgreSQL database
- **Configurable routes**: Monitor multiple routes with custom intervals

## Quick Start

1. Clone the repository
2. Copy `.env.example` to `.env` and fill in your API keys
3. Run with Docker:
   ```bash
   docker-compose up -d
   ```

Or run locally:
```bash
pip install -r requirements.txt
export AMADEUS_CLIENT_ID=your_id
export AMADEUS_CLIENT_SECRET=your_secret
python -m src.cli start
```

## CLI Commands

```bash
# Start monitoring service
python -m src.cli start

# List configured routes
python -m src.cli list-routes

# Manual check for a route
python -m src.cli check XMN SIN
```

## Configuration

Edit `config.yaml` to configure:
- Data sources (Amadeus, Kiwi, AviationStack)
- Notification channels
- Routes to monitor
- Alert rules

## API Keys

- **Amadeus**: https://developers.amadeus.com/ (free tier available)
- **Kiwi**: https://tequila.kiwi.com/
- **AviationStack**: https://aviationstack.com/

## License

MIT
