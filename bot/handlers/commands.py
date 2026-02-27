"""
Command handlers para el bot

Propósito: Manejar comandos del usuario (/start, /help, etc)
Cada handler es una función async que recibe Update y ContextTypes
"""

from telegram import Update
from telegram.ext import ContextTypes


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler para /start

    Propósito:
    - Mensaje de bienvenida cuando el usuario inicia el bot
    - Explicar qué puede hacer

    Flujo:
    1. Usuario hace /start
    2. Bot responde con "¡Bienvenido!"
    3. Muestra comandos disponibles
    """
    user = update.effective_user
    welcome_message = (
        f"¡Hola {user.first_name}! 👋\n\n"
        "Bievenido a *MiPrimeraChZamba.tech.*\n\n"
        "Con `/perfil` configuras tus preferencias de búsqueda.\n"
        "Con `/vacantes` obtienes vacantes personalizadas (configura tu perfil primero).\n\n"
        "Usa `/help` para más información."
    )


    await update.message.reply_text(welcome_message)


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler para /help

    Propósito:
    - Mostrar lista de comandos disponibles
    - Explicar qué hace cada uno
    - Explicar el workflow: TOP 5 personalizados + CSV completo

    Flujo:
    1. Usuario hace /help
    2. Bot responde con lista de comandos y workflow detallado
    """
    help_message = (
        "📋 **Comandos disponibles:**\n\n"
        "`/start` - Inicia el bot\n"
        "`/help` - Muestra esta ayuda\n"
        "`/perfil` - Configura tu perfil (keywords, país)\n"
        "`/vacantes` - Busca vacantes personalizadas\n\n"
        "**Cómo funciona el flujo:**\n\n"
        "*1️⃣ Paso 1 - Configurar perfil:*\n"
        "• Usa `/perfil`\n"
        "• Escribe tus keywords (ej: python, remote, contract)\n"
        "• Elige país\n\n"
        "*2️⃣ Paso 2 - Buscar empleos:*\n"
        "• Usa `/vacantes`\n"
        "• Espera 6-10 segundos\n\n"
        "*3️⃣ Paso 3 - Recibe resultados:*\n"
        "• 🎯 *TOP 5 empleos personalizados* (mejor match según tu perfil)\n"
        "• 📊 *CSV con TODOS los empleos* (para seguimiento y análisis)\n\n"
        "**Cómo usar los resultados:**\n"
        "• Aplica primero a los TOP 5 (ya están filtrados para ti)\n"
        "• Descarga el CSV para hacer seguimiento de tus aplicaciones\n"
        "• Analiza el mercado laboral: salarios, empresas, tendencias\n\n"
        "💡 *Pro tip:* Cambia keywords en `/perfil` para nuevas búsquedas"
    )

    await update.message.reply_text(help_message, parse_mode="Markdown")
