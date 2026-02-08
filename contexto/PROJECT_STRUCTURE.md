# Project Structure

```
bot2mvp/
├── .claude.md                        # Claude Code - guía de respuesta
├── README.md                         # Project documentation
│
├── bot/                              # Telegram Bot
│   ├── __init__.py
│   ├── config.py                     # Bot configuration
│   └── handlers/                     # Command handlers (TODO)
│       └── __init__.py
│
├── backend/                          # Backend Services
│   ├── __init__.py
│   ├── agents/                       # AI agents (TODO)
│   │   └── __init__.py
│   └── scrapers/                     # JobSpy API calls (TODO)
│       └── __init__.py
│
├── database/                         # Data Layer
│   ├── __init__.py
│   └── models.py                     # Pydantic models (User, Job)
│
├── contexto/                         # Project Context & Documentation
│   ├── CLAUDE.md                     # Guía de cómo trabajar en el proyecto
│   ├── GEMINI.md                     # Info sobre Gemini API
│   ├── JOBSPY_API_ANALYSIS.md        # Análisis detallado de JobSpy
│   ├── PROJECT_STRUCTURE.md          # This file
│   ├── idea.md                       # Problema + Solución del proyecto
│   ├── scrapersdoc.md                # JobSpy API (rainmanjam/jobspy-api)
│   └── stack.md                      # Tech stack del proyecto
│
├── tests/                            # Tests & API Testing
│   ├── __init__.py
│   ├── conftest.py                   # Pytest configuration
│   ├── unit/                         # Unit tests (TODO)
│   │   └── __init__.py
│   └── pruebasApi/                   # JobSpy API testing
│       ├── HALLAZGOS_CONSOLIDADOS.md # Resultados de todas las pruebas
│       └── scripts/                  # Test scripts
│           ├── test_basico.py
│           ├── test_filtros.py
│           ├── test_multiples.py
│           └── test_rate_limit.py
│
└── todo/                             # Implementation phases
    └── README.md                     # Roadmap
```

## Directorios Clave

### `contexto/` - Contexto del Proyecto
Aquí vive toda la información que necesitas para entender el proyecto:
- **idea.md**: Problema, solución, workflow
- **stack.md**: Tech stack (Python, uv, Telegram, etc)
- **scrapersdoc.md**: Cómo funciona rainmanjam/jobspy-api
- **CLAUDE.md**: Cómo debe responder Claude Code

### `bot/` - Bot de Telegram
Interfaz con el usuario. Maneja:
- Comandos (`/perfil`, `/vacantes`, etc)
- Mensajes
- Notificaciones (TODO)

### `backend/` - Servicios Backend
Automatización y lógica:
- **scrapers/**: Llamar a JobSpy API (TODO)
- **agents/**: AI para matching de vacantes (TODO)

### `database/` - Capa de Datos
Modelos de datos:
- **models.py**: Pydantic models (User, Job, etc)

### `tests/` - Tests
- **pruebasApi/**: Scripts de prueba de la API JobSpy
- **HALLAZGOS_CONSOLIDADOS.md**: Todos los hallazgos en un documento
- **unit/**: Tests unitarios (TODO)

## Cómo Funciona

1. Usuario envía `/perfil` en Telegram
2. Bot guarda preferencias
3. Scheduler (TODO) corre periódicamente
4. Llama a JobSpy API (rainmanjam/jobspy-api)
5. Filtra/personaliza con AI (TODO)
6. Envía resultados al usuario (TODO)
