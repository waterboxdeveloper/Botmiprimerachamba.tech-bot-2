"""
Tests para bot/main.py

Propósito: Verificar que la Application se configura correctamente con handlers.
Framework: pytest
"""

import pytest
from unittest.mock import patch, MagicMock


class TestApplicationSetup:
    """Tests para la inicialización del bot"""

    def test_application_initializes_with_token(self):
        """
        RED TEST: La Application debe inicializarse con TELEGRAM_BOT_TOKEN

        Escenario:
        - bot/main.py crea una Application
        - Debe usar token de bot/config.py
        """
        # Importaremos de bot/main.py cuando lo creemos
        from bot.main import app

        # Verificar que app existe
        assert app is not None

    def test_application_has_start_handler(self):
        """
        RED TEST: La Application debe tener CommandHandler para /start

        Escenario:
        - bot/main.py registra handlers
        - Debe incluir CommandHandler('start', cmd_start)
        """
        from bot.main import app

        # Verificar que hay handlers registrados
        assert hasattr(app, "handlers")
        assert len(app.handlers) > 0

        # Verificar que existe handler para 'start'
        has_start_handler = any(
            hasattr(handler, "commands") and "start" in handler.commands
            for handlers_list in app.handlers.values()
            for handler in handlers_list
        )
        assert has_start_handler, "No se encontró CommandHandler para /start"

    def test_application_has_help_handler(self):
        """
        RED TEST: La Application debe tener CommandHandler para /help

        Escenario:
        - bot/main.py registra handlers
        - Debe incluir CommandHandler('help', cmd_help)
        """
        from bot.main import app

        # Verificar que existe handler para 'help'
        has_help_handler = any(
            hasattr(handler, "commands") and "help" in handler.commands
            for handlers_list in app.handlers.values()
            for handler in handlers_list
        )
        assert has_help_handler, "No se encontró CommandHandler para /help"

    def test_config_loads_telegram_token(self):
        """
        RED TEST: bot/config.py debe cargar TELEGRAM_BOT_TOKEN

        Escenario:
        - Cargar bot/config.py
        - Debe tener TELEGRAM_BOT_TOKEN
        """
        from bot.config import TELEGRAM_BOT_TOKEN

        # Verificar que token existe (no vacío)
        assert TELEGRAM_BOT_TOKEN
        assert isinstance(TELEGRAM_BOT_TOKEN, str)
        assert len(TELEGRAM_BOT_TOKEN) > 0

    def test_config_has_jobspy_url(self):
        """
        RED TEST: bot/config.py debe tener JOBSPY_API_URL
        """
        from bot.config import JOBSPY_API_URL

        assert JOBSPY_API_URL
        assert "http" in JOBSPY_API_URL or "localhost" in JOBSPY_API_URL


class TestHandlerRegistration:
    """Tests para registrar handlers en la Application"""

    def test_handlers_module_exists(self):
        """
        RED TEST: bot/handlers/ debe existir y ser importable
        """
        try:
            from bot.handlers import commands
            assert commands is not None
        except ImportError:
            pytest.fail("No se puede importar bot.handlers.commands")

    def test_cmd_start_function_exists(self):
        """
        RED TEST: bot/handlers/commands.py debe tener cmd_start
        """
        from bot.handlers.commands import cmd_start
        assert callable(cmd_start)

    def test_cmd_help_function_exists(self):
        """
        RED TEST: bot/handlers/commands.py debe tener cmd_help
        """
        from bot.handlers.commands import cmd_help
        assert callable(cmd_help)
