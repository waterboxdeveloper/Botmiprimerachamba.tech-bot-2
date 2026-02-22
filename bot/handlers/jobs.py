"""
Handler /vacantes - Búsqueda on-demand de empleos personalizados

Propósito:
- Usuario hace /vacantes
- Bot obtiene keywords guardadas del usuario
- Bot busca empleos en JobSpy API
- Bot personaliza TOP 5 con Gemini (JobMatcher)
- Bot envía TOP 5 empleos formateados a Telegram
- Bot genera CSV con TODOS los empleos para descargar

Flujo:
1. get_user_profile(telegram_id) → obtiene keywords, país
2. JobSpyClient.search_jobs(keywords, country) → 25+ empleos
3. JobMatcher.match_jobs_batch(jobs[:5], keywords) → personaliza solo TOP 5 (respeta límite Gemini)
4. Ordena por match_score DESC
5. Genera CSV con TODOS los empleos (para descargar si quiere más)
6. Envía TOP 5 con resultado.telegram_message
7. Envía CSV por Telegram (archivo descargable)

Tiempo estimado: 6-12 segundos (búsqueda + personalización TOP 5)

Nota sobre Gemini API:
- Free tier: 20 requests/día, 5 requests/minuto
- Solución: Procesar solo TOP 5 jobs con Gemini, resto en CSV
"""

import logging
import csv
from io import StringIO, BytesIO
from typing import Optional, List

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from database.queries import get_user_profile, can_make_query, add_query_log
from database.db import get_connection, close_connection
from bot.config import TELEGRAM_BOT_TOKEN
from backend.scrapers.jobspy_client import JobSpyClient
from backend.agents.job_matcher import JobMatcher

logger = logging.getLogger(__name__)

# Estados de conversación
WAITING_FOR_SEARCH = 1


def generate_jobs_csv(jobs: List) -> BytesIO:
    """
    Genera un archivo CSV con todos los empleos

    Args:
        jobs: Lista de objetos Job

    Returns:
        BytesIO: Buffer con CSV para enviar a Telegram
    """
    # Crear StringIO en memoria
    output = StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow([
        "Titulo",
        "Empresa",
        "Ubicacion",
        "Tipo Empleo",
        "Remoto",
        "URL",
        "Plataforma",
        "Fecha Publicado",
    ])

    # Rows
    for job in jobs:
        writer.writerow([
            job.title or "",
            job.company or "",
            job.location or "",
            job.job_type or "",
            "Sí" if job.is_remote else "No",
            job.job_url or "",
            job.source or "",
            job.date_posted or "",
        ])

    # Convertir StringIO a BytesIO
    output.seek(0)
    bytes_output = BytesIO(output.getvalue().encode("utf-8"))
    bytes_output.seek(0)

    return bytes_output


async def cmd_vacantes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handler para /vacantes

    Flujo:
    1. ⏱️ Verificar límite de rate limiting (3 queries/día)
    2. Verificar que usuario configuró /perfil
    3. Mostrar "Buscando empleos... espera un momento"
    4. Buscar empleos (JobSpyClient)
    5. Personalizar TOP 5 (JobMatcher)
    6. Enviar TOP 5 a Telegram
    7. Generar y enviar CSV con todos
    8. 📊 Registrar consulta en query_logs
    """
    telegram_id = str(update.effective_user.id)
    user_name = update.effective_user.first_name or "Usuario"

    try:
        # 0️⃣ Obtener el mensaje correcto (del callback o del mensaje directo)
        # Esto permite que el handler funcione tanto con /vacantes como con el botón clickeable
        message_obj = context.user_data.get('callback_message') or update.message

        # 0️⃣ Verificar rate limiting
        import os
        admin_chat_id = os.getenv("ADMIN_CHAT_ID")

        permitido, error_msg = can_make_query(
            telegram_id=telegram_id,
            admin_chat_id=admin_chat_id,
            max_queries_per_day=3,
        )

        if not permitido:
            logger.warning(f"⏱️ Usuario {telegram_id} bloqueado por rate limit")
            await message_obj.reply_text(error_msg)
            return ConversationHandler.END

        # 1️⃣ Obtener perfil del usuario
        logger.info(f"🔍 /vacantes solicitado por {telegram_id} (permitido)")

        user = get_user_profile(telegram_id)
        if not user:
            await message_obj.reply_text(
                "❌ No tienes perfil configurado.\n\n"
                "Primero haz /perfil para decirme:\n"
                "• Qué keywords buscas\n"
                "• En qué país\n"
                "• Qué tipo de empleo\n\n"
                "Luego vuelve a usar /vacantes"
            )
            return ConversationHandler.END

        # Validar que usuario tiene keywords
        if not user.keywords or len(user.keywords) == 0:
            await message_obj.reply_text(
                "❌ Tu perfil no tiene keywords.\n\n"
                "Usa /perfil para agregar: python, remote, contract, etc."
            )
            return ConversationHandler.END

        # 2️⃣ Mostrar mensaje de "buscando" (con progreso dinámico)
        import asyncio

        # Mensaje inicial
        searching_msg = await message_obj.reply_text(
            f"🔍 *{user_name}*, buscamos en todas las plataformas por ti\n"
            f"para encontrar el match ideal para tu perfil...\n\n"
            f"⏳ Un momento, por favor..."
        )

        # FLAG INTELIGENTE: Indica si ya se mandaron los resultados finales
        results_sent = False

        # Task para actualizar el mensaje después de 1 minuto
        async def update_message_1min():
            nonlocal results_sent
            await asyncio.sleep(60)
            # ✅ Chequear: ¿Ya se mandó la info final?
            if results_sent:
                logger.debug("✅ Resultados ya enviados, task 1min sale gracefully")
                return
            try:
                await searching_msg.edit_text(
                    f"⏳ *{user_name}*, casi listos!\n\n"
                    f"Estamos analizando Indeed, LinkedIn y Glassdoor\n"
                    f"para traerte los mejores matches..."
                )
            except Exception as e:
                logger.warning(f"No se pudo actualizar mensaje a 1min: {e}")

        # Task para actualizar el mensaje después de 3 minutos
        async def update_message_3min():
            nonlocal results_sent
            await asyncio.sleep(180)
            # ✅ Chequear: ¿Ya se mandó la info final?
            if results_sent:
                logger.debug("✅ Resultados ya enviados, task 3min sale gracefully")
                return
            try:
                await searching_msg.edit_text(
                    f"🚀 *{user_name}*, última verificación!\n\n"
                    f"Estamos armando tu lista personalizada\n"
                    f"con los mejores empleos que encontramos..."
                )
            except Exception as e:
                logger.warning(f"No se pudo actualizar mensaje a 3min: {e}")

        # Ejecutar updates en paralelo (sin esperar)
        asyncio.create_task(update_message_1min())
        asyncio.create_task(update_message_3min())

        # 3️⃣ Buscar empleos
        logger.info(
            f"📡 Buscando: keywords={user.keywords}, country={user.location_preference}"
        )

        search_term = " ".join(user.keywords)
        client = JobSpyClient()

        jobs = client.search_jobs(
            keywords=search_term,
            country=user.location_preference,
            job_type=None,  # Usuario no filtró por tipo
            platforms=["indeed", "linkedin", "glassdoor"],
        )

        if not jobs:
            results_sent = True  # ✅ Marcar que ya se mandó respuesta
            await message_obj.reply_text(
                "😞 No encontramos empleos con tus criterios.\n\n"
                "💡 Intenta:\n"
                "• /perfil con keywords más específicas\n"
                "• 'Senior Python Developer' en lugar de solo 'python'\n"
                "• Incluir ubicación: 'Remote USA'"
            )
            return ConversationHandler.END

        logger.info(f"✅ Encontrados {len(jobs)} empleos")

        # 4️⃣ Personalizar con Gemini (SOLO TOP 5 para respetar límite Gemini)
        logger.info("🤖 Personalizando TOP 5 con Gemini...")

        # Limitar a TOP 5 antes de pasar a Gemini (respeta límite de 20 requests/día free tier)
        jobs_to_match = jobs[:5]

        matcher = JobMatcher()
        results = matcher.match_jobs_batch(
            jobs=jobs_to_match,
            user_keywords=user.keywords,
            user_location=user.location_preference,
        )

        # 5️⃣ Ordenar por score DESC
        results_sorted = sorted(
            results, key=lambda r: r.match_score, reverse=True
        )
        top_results = results_sorted  # Ya son solo 5

        logger.info(
            f"✅ Top {len(top_results)} empleos personalizados. Enviando a Telegram..."
        )

        # 6️⃣ Enviar resultados a Telegram
        if top_results:
            await message_obj.reply_text(
                f"🎯 *TOP {len(top_results)} empleos personalizados*\n\n"
                f"Basado en: {', '.join(user.keywords)}\n"
                f"País: {user.location_preference}",
                parse_mode="Markdown",
            )

            for i, result in enumerate(top_results, 1):
                # Remover links de ejemplo del mensaje de Gemini (dejar solo el real)
                import re
                telegram_msg_clean = re.sub(r'\[.*?\]\(https?://.*?\)', '', result.telegram_message)

                # Agregar SOLO el link real de aplicación
                job_url = result.job.job_url or "https://www.ejemplo.com"
                message_with_link = (
                    f"*#{i}*\n"
                    f"{telegram_msg_clean}\n\n"
                    f"🔗 [*Aplicar Ahora →*]({job_url})"
                )

                # Enviar mensaje personalizado con link real
                await message_obj.reply_text(
                    message_with_link,
                    parse_mode="Markdown",
                    disable_web_page_preview=True,
                )

                # Pequeña pausa entre mensajes para no flood
                await asyncio.sleep(0.5)

            # ✅ BANDERA: Ya se mandó la información final
            # Las tareas de actualización verán esto y saldrán gracefully
            results_sent = True

            # 7️⃣ Generar y enviar CSV con TODOS los empleos
            logger.info(f"📊 Generando CSV con {len(jobs)} empleos...")

            csv_buffer = generate_jobs_csv(jobs)

            await message_obj.reply_text(
                f"✅ ¡Búsqueda completada!\n\n"
                f"📊 **Resumen:**\n"
                f"• TOP {len(top_results)} personalizados 👆 (mejor match)\n"
                f"• {len(jobs) - len(top_results)} más en el CSV 📥 (para análisis)\n\n"
                f"💡 **Cómo usar:**\n"
                f"1. Aplica a los TOP {len(top_results)} (ya están filtrados)\n"
                f"2. Descarga el CSV para hacer seguimiento\n"
                f"3. Analiza el mercado laboral offline\n"
                f"4. Estudia salarios y empresas",
                parse_mode="Markdown",
            )

            await message_obj.reply_document(
                document=csv_buffer,
                filename=f"empleos_{user.location_preference}_{len(jobs)}_total.csv",
                caption=f"📋 CSV con {len(jobs)} empleos | Descárgalo para hacer seguimiento"
            )

            await message_obj.reply_text(
                "📊 **Cómo usar el CSV:**\n\n"
                "1. Descárgalo en tu computadora\n"
                "2. Abrelo en Excel o Google Sheets\n"
                "3. Agrega una columna 'Aplicado' (Sí/No) para hacer seguimiento\n"
                "4. Filtra por empresa, tipo de empleo, ubicación\n"
                "5. Estudia el mercado: salarios, tendencias\n\n"
                "💡 Los TOP 5 de arriba son los que más matchean. Empieza por esos.\n"
                "💡 ¿Más búsquedas? Usa `/perfil` con otros keywords",
                parse_mode="Markdown"
            )
        else:
            results_sent = True  # ✅ Marcar que ya se mandó respuesta
            await message_obj.reply_text(
                "😞 No hay resultados después de personalizar.\n\n"
                "Intenta /perfil con keywords diferentes."
            )

        return ConversationHandler.END

    except Exception as e:
        logger.error(f"❌ Error en /vacantes: {e}")
        message_obj = context.user_data.get('callback_message') or update.message
        # ✅ Marcar que ya se mandó respuesta (aunque sea error)
        # Esto detiene las tareas de actualización gracefully
        results_sent = True
        await message_obj.reply_text(
            f"⚠️ Error buscando empleos.\n\n"
            f"Detalles: {str(e)[:100]}\n\n"
            f"Intenta más tarde o usa /help"
        )
        return ConversationHandler.END
