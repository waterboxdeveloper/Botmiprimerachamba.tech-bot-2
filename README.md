# Bot MVP - Telegram Job Alerts (On-Demand)

Telegram bot que entrega búsquedas personalizadas de vacantes freelance on-demand.

## Stack

- **Language**: Python 3.10+
- **Bot**: python-telegram-bot (on-demand, siempre escuchando)
- **Database**: Google Sheets (tabla USUARIOS solamente)
- **AI**: LangChain + Gemini 2.5 Flash (personalización on-demand)
- **Job Scraping**: JobSpy API (rainmanjam/jobspy-api) - on-demand

## Quick Start

```bash
# Setup
uv venv .venv
source .venv/bin/activate
uv sync

# Run tests
pytest tests/

# Run bot
python -m bot.main
```

## Project Structure

```
bot2mvp/
├── bot/              # Bot handlers and main
├── backend/          # Scrapers, agents, scheduler
├── database/         # Models and data operations
├── tests/            # Tests (unit, integration, API exploration)
└── contexto/         # Project documentation
```

## Documentation

See `contexto/` for:
- `idea.md` - Project requirements
- `stack.md` - Tech stack details
- `JOBSPY_API_ANALYSIS.md` - API documentation
- `CLAUDE.md` - Development guidelines
