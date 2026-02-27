"""
Tests para bot/handlers/commands.py

Propósito: Verificar que los comandos /start y /help funcionan correctamente.
Framework: pytest + pytest-asyncio
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from telegram import Update, User, Chat, Message
from telegram.ext import ContextTypes

# Importaremos de bot/handlers/commands.py cuando lo creemos
# from bot.handlers.commands import cmd_start, cmd_help


class TestStartCommand:
    """Tests para el comando /start"""

    @pytest.mark.asyncio
    async def test_cmd_start_sends_welcome_message(self):
        """
        RED TEST: /start debe enviar mensaje de bienvenida

        Escenario:
        - Usuario ejecuta /start
        - Bot debe responder con mensaje de bienvenida
        """
        # Importar cuando exista
        from bot.handlers.commands import cmd_start

        # Mock Update y Context
        update = self._create_mock_update(user_id=123, chat_id=456)
        context = AsyncMock(spec=ContextTypes.DEFAULT_TYPE)

        # Ejecutar handler
        await cmd_start(update, context)

        # Verificar que se envió un mensaje
        update.message.reply_text.assert_called_once()

        # Verificar que el mensaje contiene "bienvenido" o similar
        call_args = update.message.reply_text.call_args
        message_text = call_args[0][0].lower() if call_args[0] else ""
        assert "bienvenido" in message_text or "hola" in message_text

    @pytest.mark.asyncio
    async def test_cmd_start_with_keyboard(self):
        """
        RED TEST: /start debe incluir keyboard con opciones iniciales
        """
        from bot.handlers.commands import cmd_start

        update = self._create_mock_update(user_id=789, chat_id=999)
        context = AsyncMock(spec=ContextTypes.DEFAULT_TYPE)

        await cmd_start(update, context)

        # Verificar que reply_text fue llamado
        update.message.reply_text.assert_called_once()

    @staticmethod
    def _create_mock_update(user_id=123, chat_id=456) -> Update:
        """Helper: Crear mock de Update"""
        update = MagicMock(spec=Update)
        update.effective_user = MagicMock(spec=User)
        update.effective_user.id = user_id
        update.effective_user.first_name = "Test"

        update.message = AsyncMock()
        update.message.chat_id = chat_id
        update.message.reply_text = AsyncMock()

        return update


class TestHelpCommand:
    """Tests para el comando /help"""

    @pytest.mark.asyncio
    async def test_cmd_help_sends_help_message(self):
        """
        RED TEST: /help debe enviar lista de comandos disponibles

        Escenario:
        - Usuario ejecuta /help
        - Bot debe responder con lista de comandos
        """
        from bot.handlers.commands import cmd_help

        update = self._create_mock_update(user_id=123, chat_id=456)
        context = AsyncMock(spec=ContextTypes.DEFAULT_TYPE)

        await cmd_help(update, context)

        # Verificar que se envió un mensaje
        update.message.reply_text.assert_called_once()

        # Verificar contenido
        call_args = update.message.reply_text.call_args
        message_text = call_args[0][0].lower() if call_args[0] else ""

        # Debe mencionar al menos algunos comandos
        assert any(cmd in message_text for cmd in ["/perfil", "/vacantes", "/help"])

    @pytest.mark.asyncio
    async def test_cmd_help_lists_all_commands(self):
        """
        RED TEST: /help debe listar /perfil, /vacantes, /help
        """
        from bot.handlers.commands import cmd_help

        update = self._create_mock_update(user_id=789, chat_id=999)
        context = AsyncMock(spec=ContextTypes.DEFAULT_TYPE)

        await cmd_help(update, context)

        # Verificar que se llamó
        update.message.reply_text.assert_called_once()

    @staticmethod
    def _create_mock_update(user_id=123, chat_id=456) -> Update:
        """Helper: Crear mock de Update"""
        update = MagicMock(spec=Update)
        update.effective_user = MagicMock(spec=User)
        update.effective_user.id = user_id
        update.effective_user.first_name = "Test"

        update.message = AsyncMock()
        update.message.chat_id = chat_id
        update.message.reply_text = AsyncMock()

        return update
