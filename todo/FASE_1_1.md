# FASE 1.1: Crear pyproject.toml

## Objetivo
Archivo central con todas las dependencias del proyecto (uv las maneja).

## Qué hacer
Crear `/bot2mvp/pyproject.toml` con:
- **Metadata**: nombre, versión, descripción, autor
- **Dependencies**: Todas las librerías necesarias
- **Dev dependencies**: Para testing y desarrollo

## Dependencias necesarias

```
Core Bot & Telegram:
- python-telegram-bot>=20.0

Database & Data:
- google-api-python-client>=2.0
- google-auth-oauthlib>=1.0
- pydantic>=2.0
- sqlalchemy>=2.0  (opcional, pero útil para SQLite)

AI & LLM:
- langchain>=0.1
- langchain-google-genai>=0.0.15
- google-generativeai>=0.3

Task Scheduling:
- apscheduler>=3.10

Utils:
- requests>=2.31
- python-dotenv>=1.0
- aiohttp>=3.8

Dev:
- pytest>=7.0
- pytest-asyncio>=0.21.0
```

## Tareas
- [ ] Crear `pyproject.toml` en el root del proyecto
- [ ] Incluir todas las dependencias listadas arriba
- [ ] Ejecutar `uv sync` para verificar
- [ ] Commit cambios

## Verificación
```bash
uv sync
# Debe instalar todo sin errores

python -c "import telegram; print(telegram.__version__)"
# Debe mostrar la versión
```

## Notas
- No uses `uv pip install`, usa `uv sync` que es más rápido
- Si agregas deps luego, siempre actualiza `pyproject.toml` primero, luego `uv sync`
