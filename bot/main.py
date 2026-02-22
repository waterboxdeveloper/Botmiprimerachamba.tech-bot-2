"""
Entry point del bot - Configuración de la Application

Propósito:
- Inicializar la Application de Telegram
- Registrar handlers de comandos
- Configurar error handling
- Punto de entrada para ejecutar el bot

Arquitectura (python-telegram-bot v20+):
- Application: Clase principal que orquesta el bot
- CommandHandler: Maneja comandos (/start, /help, etc)
- MessageHandler: Maneja mensajes normales
- Application.run_polling(): Inicia el bot en polling mode
"""

import logging
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
)
from telegram import Update

from bot.config import TELEGRAM_BOT_TOKEN
from bot.handlers.commands import cmd_start, cmd_help
from bot.handlers.profile import get_profile_handler
from bot.handlers.jobs import cmd_vacantes
from database.db import init_db

# Configurar logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def handle_vacantes_button(update: Update, context) -> int:
    """
    Bridge para manejar el botón clickeable /vacantes desde el callback

    Cuando el usuario clickea el botón "🔍 Buscar ahora /vacantes",
    este handler lo captura y llama a cmd_vacantes

    Nota: Usamos callback_query.message en lugar de update.message (que es read-only)
    """
    # Confirmar el callback (muestra checkmark en Telegram)
    await update.callback_query.answer()

    # Copiar el mensaje del callback al update para que cmd_vacantes funcione
    # (sin intentar asignar, que falla porque Update es immutable)
    # En su lugar, pasamos context con el mensaje correcto
    context.user_data['callback_message'] = update.callback_query.message

    # Llamar al handler /vacantes normal
    return await cmd_vacantes(update, context)


def setup_application() -> Application:
    """
    Configura y retorna la Application del bot

    Pasos:
    1. Inicializar BD (crear tablas si no existen)
    2. Crear Application con token
    3. Registrar handlers de comandos
    4. Retornar Application lista para usar

    Returns:
        Application: Instancia configurada del bot
    """
    # Paso 0: Inicializar BD (Supabase)
    try:
        init_db()
        logger.info("✅ Base de datos Supabase inicializada")
    except Exception as e:
        logger.error(f"❌ Error inicializando BD: {e}")
        raise

    # Paso 1: Crear Application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Paso 2: Registrar CommandHandlers
    application.add_handler(CommandHandler("start", cmd_start))
    application.add_handler(CommandHandler("help", cmd_help))
    application.add_handler(CommandHandler("vacantes", cmd_vacantes))

    # Paso 2b: Registrar CallbackQueryHandler ANTES de ConversationHandler
    # (El orden importa: se procesan secuencialmente)
    application.add_handler(CallbackQueryHandler(handle_vacantes_button, pattern="^/vacantes$"))

    # Paso 2c: Registrar ConversationHandler para /perfil (después del callback)
    profile_handler = get_profile_handler()
    application.add_handler(profile_handler)

    logger.info("✅ Application configurada correctamente")

    return application


# Crear instancia global de la Application
app = setup_application()


def run_bot():
    """
    Ejecuta el bot en polling mode

    Polling mode: El bot pregunta constantemente al servidor de Telegram
    si hay mensajes nuevos (alternativa a webhooks)

    Para usar:
    ```python
    from bot.main import run_bot
    run_bot()
    ```
    """
    logger.info("🚀 Iniciando bot...")
    app.run_polling()
    logger.info("✅ Bot detenido")


if __name__ == "__main__":
    run_bot()
