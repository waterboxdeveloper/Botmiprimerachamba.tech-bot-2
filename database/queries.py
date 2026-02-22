"""
CRUD operations y queries - SUPABASE VERSION

Propósito:
- Leer/escribir usuarios
- Registrar queries para rate limiting
- Validar con Pydantic models

Framework: Supabase (PostgreSQL)
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Tuple

from database.db import get_connection
from database.models import User
from dotenv import load_dotenv
import os

logger = logging.getLogger(__name__)
load_dotenv()

# ============================================================================
# USER OPERATIONS
# ============================================================================


def create_user(user: User) -> Optional[User]:
    """
    Crear nuevo usuario en Supabase

    Args:
        user: Usuario a crear (con validation Pydantic)

    Returns:
        User: Usuario creado, o None si error
    """
    try:
        supabase = get_connection()

        # Preparar datos para Supabase
        user_data = {
            "telegram_id": user.telegram_id,
            "name": user.name,
            "email": user.email,
            "phone": user.phone,
            "keywords": json.dumps(user.keywords),  # JSON en Supabase
            "location_preference": user.location_preference,
            "experience_level": user.experience_level,
            "is_active": user.is_active,
            "created_at": datetime.utcnow().isoformat(),
        }

        # Insert en Supabase
        response = supabase.table("usuarios").insert(user_data).execute()

        if response.data:
            logger.info(f"✅ Usuario creado: {user.telegram_id}")
            return user
        else:
            logger.error(f"❌ Error creando usuario: {response}")
            return None

    except Exception as e:
        logger.error(f"❌ Error en create_user: {e}")
        return None


def get_user(telegram_id: str) -> Optional[User]:
    """
    Obtener usuario por telegram_id

    Args:
        telegram_id: ID de Telegram del usuario

    Returns:
        User: Usuario encontrado, o None
    """
    try:
        supabase = get_connection()

        response = (
            supabase.table("usuarios")
            .select("*")
            .eq("telegram_id", str(telegram_id))
            .single()
            .execute()
        )

        if response.data:
            user_data = response.data

            # Deserializar JSON
            if isinstance(user_data.get("keywords"), str):
                user_data["keywords"] = json.loads(user_data["keywords"])

            user = User(**user_data)
            logger.debug(f"✅ Usuario encontrado: {telegram_id}")
            return user
        else:
            logger.debug(f"⚠️ Usuario no encontrado: {telegram_id}")
            return None

    except Exception as e:
        logger.debug(f"⚠️ Error en get_user: {e}")
        return None


def get_user_profile(telegram_id: str) -> Optional[User]:
    """
    Obtener perfil de usuario (usuarios activos solo)

    Args:
        telegram_id: ID de Telegram

    Returns:
        User: Usuario si existe y está activo, None si no
    """
    try:
        supabase = get_connection()

        response = (
            supabase.table("usuarios")
            .select("*")
            .eq("telegram_id", str(telegram_id))
            .eq("is_active", True)
            .single()
            .execute()
        )

        if response.data:
            user_data = response.data

            # Deserializar keywords
            if isinstance(user_data.get("keywords"), str):
                user_data["keywords"] = json.loads(user_data["keywords"])

            user = User(**user_data)
            return user
        else:
            return None

    except Exception as e:
        logger.debug(f"⚠️ Usuario no encontrado o inactivo: {e}")
        return None


def update_user(telegram_id: str, **kwargs) -> bool:
    """
    Actualizar usuario (solo campos no-None)

    Args:
        telegram_id: ID del usuario
        **kwargs: Campos a actualizar (ej: keywords=[...], location_preference="...")

    Returns:
        bool: True si éxito, False si error
    """
    try:
        supabase = get_connection()

        # Preparar datos para actualizar
        update_data = {}

        for key, value in kwargs.items():
            if value is not None:
                if key == "keywords":
                    # Serializar keywords a JSON
                    update_data[key] = json.dumps(value)
                else:
                    update_data[key] = value

        update_data["updated_at"] = datetime.utcnow().isoformat()

        # Update
        response = (
            supabase.table("usuarios")
            .update(update_data)
            .eq("telegram_id", str(telegram_id))
            .execute()
        )

        if response.data:
            logger.info(f"✅ Usuario actualizado: {telegram_id}")
            return True
        else:
            logger.error(f"❌ Error actualizando usuario: {response}")
            return False

    except Exception as e:
        logger.error(f"❌ Error en update_user: {e}")
        return False


def delete_user(telegram_id: str) -> bool:
    """
    Soft delete de usuario (is_active = False)

    Args:
        telegram_id: ID del usuario

    Returns:
        bool: True si éxito
    """
    try:
        supabase = get_connection()

        response = (
            supabase.table("usuarios")
            .update({"is_active": False})
            .eq("telegram_id", str(telegram_id))
            .execute()
        )

        if response.data:
            logger.info(f"✅ Usuario eliminado (soft): {telegram_id}")
            return True
        else:
            return False

    except Exception as e:
        logger.error(f"❌ Error en delete_user: {e}")
        return False


def user_exists(telegram_id: str) -> bool:
    """
    Verificar si usuario existe

    Args:
        telegram_id: ID del usuario

    Returns:
        bool: True si existe y está activo
    """
    try:
        user = get_user_profile(telegram_id)
        return user is not None
    except:
        return False


def count_active_users() -> int:
    """
    Contar usuarios activos

    Returns:
        int: Número de usuarios activos
    """
    try:
        supabase = get_connection()

        # Usar count="exact" sin SELECT específico
        response = (
            supabase.table("usuarios")
            .select("id", count="exact")
            .eq("is_active", True)
            .execute()
        )

        return response.count or 0

    except Exception as e:
        logger.error(f"❌ Error contando usuarios: {e}")
        return 0


# ============================================================================
# RATE LIMITING
# ============================================================================


def add_query_log(
    telegram_id: str, query_type: str = "vacantes", status: str = "success"
) -> bool:
    """
    Registrar una query (búsqueda) para rate limiting

    Args:
        telegram_id: Usuario que hizo la búsqueda
        query_type: Tipo de query ('vacantes', 'perfil', etc)
        status: Estado ('success', 'error', etc)

    Returns:
        bool: True si se registró
    """
    try:
        supabase = get_connection()

        log_data = {
            "telegram_id": str(telegram_id),
            "query_type": query_type,
            "timestamp": datetime.utcnow().isoformat(),
            "status": status,
        }

        response = supabase.table("query_logs").insert(log_data).execute()

        if response.data:
            logger.debug(f"✅ Query registrada: {telegram_id}")
            return True
        else:
            logger.error(f"❌ Error registrando query: {response}")
            return False

    except Exception as e:
        logger.error(f"❌ Error en add_query_log: {e}")
        return False


def count_queries_today(
    telegram_id: str, query_type: str = "vacantes"
) -> int:
    """
    Contar queries que el usuario hizo HOY

    Args:
        telegram_id: Usuario
        query_type: Tipo de query

    Returns:
        int: Número de queries hoy
    """
    try:
        supabase = get_connection()

        # Hoy a las 00:00:00 UTC
        today_start = (
            datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        )

        response = (
            supabase.table("query_logs")
            .select("id", count="exact")
            .eq("telegram_id", str(telegram_id))
            .eq("query_type", query_type)
            .gte("timestamp", today_start.isoformat())
            .execute()
        )

        count = response.count or 0
        logger.debug(f"Queries hoy para {telegram_id}: {count}")
        return count

    except Exception as e:
        logger.error(f"❌ Error en count_queries_today: {e}")
        return 0


def can_make_query(
    telegram_id: str,
    admin_chat_id: Optional[str] = None,
    max_queries_per_day: int = 3,
) -> Tuple[bool, Optional[str]]:
    """
    Verificar si usuario puede hacer query (rate limiting)

    Args:
        telegram_id: Usuario
        admin_chat_id: ID de admin (bypass de límite)
        max_queries_per_day: Máximo queries por día

    Returns:
        Tuple[bool, Optional[str]]: (permitido, error_message)
            - True, None: Permitido
            - False, mensaje: Denegado + razón
    """
    try:
        # Admin bypass
        if admin_chat_id and str(telegram_id) == str(admin_chat_id):
            logger.debug(f"✅ Admin bypass: {telegram_id}")
            return True, None

        # Contar queries hoy
        count = count_queries_today(telegram_id)

        if count >= max_queries_per_day:
            error_msg = (
                f"⏱️ Ya alcanzaste {max_queries_per_day} búsquedas hoy.\n\n"
                f"Vuelve mañana para más empleos. 😴"
            )
            logger.warning(f"⏱️ Rate limit alcanzado: {telegram_id}")
            return False, error_msg

        return True, None

    except Exception as e:
        logger.error(f"❌ Error en can_make_query: {e}")
        # En caso de error, permitir (fail-open)
        return True, None
