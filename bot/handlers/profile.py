"""
Handler para /perfil - Conversación interactiva para configurar perfil de usuario

Propósito:
- Pedir keywords de búsqueda (ej: "python remote contract")
- Pedir país (ej: "Colombia", "USA", "UK")
- Pedir job_type opcional (ej: "contract", "fulltime")
- Guardar usuario en BD usando database/queries.create_user()

Arquitectura:
- ConversationHandler: Maneja conversación multi-paso
- Estados: KEYWORDS, COUNTRY, JOB_TYPE
- database/queries: Guarda en SQLite
"""

import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler

from database.queries import create_user, update_user, user_exists
from database.models import User

logger = logging.getLogger(__name__)

# Estados de la conversación
KEYWORDS, COUNTRY, JOB_TYPE = range(3)

# Países válidos - LATAM PRIMERO, luego otros
VALID_COUNTRIES = {
    # Latam (prioridad)
    "mexico": "Mexico",
    "colombia": "Colombia",
    "argentina": "Argentina",
    "perú": "Peru",
    "peru": "Peru",
    "chile": "Chile",
    "brasil": "Brazil",
    "brazil": "Brazil",
    # USA/Canadá
    "usa": "USA",
    "canada": "Canada",
    # Europa
    "uk": "UK",
    "españa": "Spain",
    "spain": "Spain",
    "germany": "Germany",
    "france": "France",
}

# Orden de países para botones (Latam primero)
COUNTRIES_BUTTONS = [
    ["🇲🇽 Mexico", "🇨🇴 Colombia"],
    ["🇦🇷 Argentina", "🇵🇪 Peru"],
    ["🇨🇱 Chile", "🇧🇷 Brazil"],
    ["🇺🇸 USA", "🇨🇦 Canada"],
    ["🇬🇧 UK", "🇪🇸 Spain"],
]

# Tipos de trabajo válidos
VALID_JOB_TYPES = ["contract", "fulltime", "parttime", "internship"]

# Ejemplos por industria (1 por área, descriptivos)
KEYWORD_EXAMPLES = """
📚 *Ejemplos:*

🖥️ Tecnología: `Desarrollador Python, Django, remoto`
💼 Negocios: `Contador, impuestos, México`
🏥 Salud: `Enfermero, hospitales, fulltime`
🎨 Creatividad: `Diseñador gráfico, Adobe, freelance`
📊 Datos: `Analista de datos, Python, looker`
🏗️ Ingeniería: `Ingeniero civil, proyectos, presencial`
"""


async def cmd_profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Inicia la conversación /perfil

    Flujo:
    1. Usuario ejecuta /perfil
    2. Bot pide keywords
    3. Usuario responde
    4. Continúa con next state (KEYWORDS)

    Returns:
        int: Siguiente estado (KEYWORDS)
    """
    user = update.effective_user
    welcome = (
        f"¡Hola {user.first_name}! 👋\n\n"
        "Voy a configurar tu perfil para buscar **vacantes personalizadas**.\n\n"
        "**Paso 1/3: ¿Qué keywords buscas?**\n\n"
        "Escribe **palabras clave separadas por comas**.\n\n"
        "**Formato recomendado:**\n"
        "1️⃣ *Puesto/Rol* (ej: Desarrollador, Contador, Enfermero)\n"
        "2️⃣ *Skill/Especialidad* (ej: Python, impuestos, hospitales)\n"
        "3️⃣ *Modalidad* (ej: remoto, fulltime, contract)\n\n"
        f"{KEYWORD_EXAMPLES}\n\n"
        "**Tu turno:** Escribe tus keywords (mínimo 1, máximo 5)"
    )
    await update.message.reply_text(welcome, parse_mode="Markdown")
    return KEYWORDS


async def get_keywords(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Procesa keywords del usuario

    Validaciones:
    - No vacío
    - Separados por comas
    - Máximo 5 keywords

    Returns:
        int: Siguiente estado (COUNTRY)
    """
    keywords_text = update.message.text.strip()

    if not keywords_text:
        await update.message.reply_text(
            "❌ Por favor escribe al menos una palabra clave.\n\n"
            "Ejemplo: `Python, remoto, contract`"
        )
        return KEYWORDS

    # Separar por comas y limpiar espacios
    keywords = [k.strip() for k in keywords_text.split(",")]
    keywords = [k for k in keywords if k]  # Remover vacíos

    if len(keywords) > 5:
        await update.message.reply_text(
            f"❌ Máximo 5 keywords. Escribiste {len(keywords)}.\n\n"
            "Intenta con menos palabras."
        )
        return KEYWORDS

    # Guardar en context para después
    context.user_data["keywords"] = keywords

    logger.info(f"✅ Keywords guardadas: {keywords}")

    # Pasar a siguiente estado
    country_msg = (
        "✅ Perfecto!\n\n"
        "**Paso 2/3: ¿En qué país buscas?**\n\n"
        "Selecciona uno de los botones."
    )

    # Crear keyboard con países
    reply_markup = ReplyKeyboardMarkup(
        COUNTRIES_BUTTONS,
        one_time_keyboard=True,
        input_field_placeholder="Selecciona un país"
    )

    await update.message.reply_text(country_msg, reply_markup=reply_markup, parse_mode="Markdown")
    return COUNTRY


async def get_country(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Procesa país del usuario

    Validaciones:
    - Debe ser país válido (case-insensitive)
    - Convertir a formato API (Mexico, Colombia, etc)

    Returns:
        int: Siguiente estado (JOB_TYPE)
    """
    country_input = update.message.text.strip()

    # Limpiar emojis y espacios
    country_clean = country_input.replace("🇲🇽", "").replace("🇨🇴", "").replace("🇦🇷", "").replace("🇵🇪", "").replace("🇨🇱", "").replace("🇧🇷", "").replace("🇺🇸", "").replace("🇨🇦", "").replace("🇬🇧", "").replace("🇪🇸", "").strip()

    country_lower = country_clean.lower()

    if country_lower not in VALID_COUNTRIES:
        available = ", ".join(set(VALID_COUNTRIES.values()))
        await update.message.reply_text(
            f"❌ País no válido: {country_input}\n\n"
            f"Válidos: {available}"
        )
        return COUNTRY

    # Convertir a formato API
    country = VALID_COUNTRIES[country_lower]
    context.user_data["country"] = country

    logger.info(f"✅ País guardado: {country}")

    # Pasar a siguiente estado
    job_type_msg = (
        "✅ Excelente!\n\n"
        "**Paso 3/3: ¿Qué tipo de empleo? (Opcional)**\n\n"
        "Si no tienes preferencia, presiona \"Cualquiera ➡️\""
    )

    job_type_buttons = [
        ["🤝 Contract", "💼 Fulltime"],
        ["⏰ Parttime", "🎓 Internship"],
        ["➡️ Cualquiera"],
    ]

    reply_markup = ReplyKeyboardMarkup(
        job_type_buttons,
        one_time_keyboard=True,
        input_field_placeholder="Selecciona tipo de empleo"
    )

    await update.message.reply_text(job_type_msg, reply_markup=reply_markup, parse_mode="Markdown")
    return JOB_TYPE


async def get_job_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Procesa tipo de trabajo (opcional)

    Si es "Cualquiera" → None

    Returns:
        int: ConversationHandler.END (guarda usuario)
    """
    job_type_input = update.message.text.strip()

    # Limpiar emojis
    job_type_clean = job_type_input.replace("🤝 ", "").replace("💼 ", "").replace("⏰ ", "").replace("🎓 ", "").replace("➡️ ", "").strip().lower()

    # Si dice "Cualquiera", dejar como None
    if "cualquiera" in job_type_clean or "➡️" in job_type_input:
        job_type = None
    elif job_type_clean in VALID_JOB_TYPES:
        job_type = job_type_clean
    else:
        await update.message.reply_text(
            f"❌ Tipo inválido: {job_type_input}\n\n"
            f"Válidos: {', '.join(VALID_JOB_TYPES)}"
        )
        return JOB_TYPE

    context.user_data["job_type"] = job_type

    logger.info(f"✅ Job type guardado: {job_type}")

    # Guardar usuario en BD
    telegram_id = str(update.effective_user.id)
    user_name = update.effective_user.first_name or "Usuario"
    keywords = context.user_data.get("keywords", [])
    country = context.user_data.get("country")

    try:
        if user_exists(telegram_id):
            # Actualizar usuario existente
            success = update_user(
                telegram_id,
                keywords=keywords,
                location_preference=country,
            )
            if success:
                logger.info(f"✅ Usuario actualizado: {telegram_id}")
            else:
                raise Exception("Error actualizando usuario")
        else:
            # Crear usuario nuevo
            user = User(
                telegram_id=telegram_id,
                name=user_name,
                keywords=keywords,
                location_preference=country,
                experience_level="mid",
                is_active=True,
            )
            result = create_user(user)
            if not result:
                raise Exception("Error creando usuario")
            logger.info(f"✅ Usuario creado: {telegram_id}")

        # Mensaje de éxito
        job_type_display = job_type.capitalize() if job_type else "Cualquiera"
        success_msg = (
            "✅ *¡Perfil guardado exitosamente!*\n\n"
            "📌 **Keywords:** " + ", ".join(keywords) + "\n"
            "🌍 **País:** " + country + "\n"
            "💼 **Tipo:** " + job_type_display + "\n\n"
            "🚀 Ahora usa /vacantes para buscar empleos personalizados para ti."
        )

        # Crear botón clickeable para /vacantes
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔍 Buscar ahora /vacantes", callback_data="/vacantes")]
        ])

        await update.message.reply_text(
            success_msg,
            parse_mode="Markdown",
            reply_markup=keyboard
        )

        logger.info(f"User {telegram_id} profile saved")

        return ConversationHandler.END

    except Exception as e:
        logger.error(f"❌ Error guardando usuario: {e}")
        await update.message.reply_text(
            f"❌ Error al guardar perfil.\n\nDetalles: {str(e)[:100]}"
        )
        return ConversationHandler.END


def get_profile_handler():
    """
    Retorna ConversationHandler configurado para /perfil

    Estados:
    - KEYWORDS: Pedir keywords
    - COUNTRY: Pedir país
    - JOB_TYPE: Pedir tipo (opcional)
    """
    from telegram.ext import MessageHandler, filters

    return ConversationHandler(
        entry_points=[
            # Comando /perfil
            MessageHandler(filters.Command() & filters.Regex("^/perfil$"), cmd_profile)
        ],
        states={
            KEYWORDS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_keywords)
            ],
            COUNTRY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_country)
            ],
            JOB_TYPE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_job_type)
            ],
        },
        fallbacks=[],
    )
