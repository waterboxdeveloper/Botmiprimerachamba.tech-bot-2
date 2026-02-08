# Bot MVP - Telegram Job Alerts

Telegram bot que envía alertas personalizadas de vacantes freelance a usuarios.

## Stack

- **Language**: Python 3.10+
- **Bot**: python-telegram-bot
- **Database**: Google Sheets
- **AI**: LangChain + Gemini 2.5 Flash
- **Job Scraping**: JobSpy API (rainmanjam/jobspy-api)
- **Scheduling**: APScheduler

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
