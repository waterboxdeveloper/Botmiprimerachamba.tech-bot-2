"""
Database initialization y connection management - SUPABASE VERSION

Propósito:
- Inicializar cliente Supabase
- Manejar conexión (pooling automático)
- Verificar que tablas existan

Framework: Supabase (PostgreSQL en la nube)
"""

import os
import logging
from supabase import create_client, Client
from dotenv import load_dotenv

# Cargar .env
load_dotenv()

logger = logging.getLogger(__name__)

# ============================================================================
# SUPABASE CLIENT
# ============================================================================

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    logger.error("❌ SUPABASE_URL y SUPABASE_KEY no están configurados en .env")
    raise ValueError(
        "Configura SUPABASE_URL y SUPABASE_KEY en .env\n"
        "Obtén los valores desde: https://app.supabase.com → Settings → API"
    )

# Crear cliente de Supabase (con connection pooling automático)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

logger.info(f"✅ Conectado a Supabase: {SUPABASE_URL.split('//')[1].split('.')[0]}")


def init_db() -> Client:
    """
    Inicializa la conexión a Supabase y verifica que las tablas existan

    Pasos:
    1. Verificar conexión a Supabase (health check)
    2. Verificar que tablas existan (usuarios, query_logs, jobs)
    3. Retornar cliente

    Returns:
        Client: Cliente de Supabase listo para usar

    Raises:
        Exception: Si no puede conectar o tablas no existen
    """
    try:
        # Paso 1: Verificar conexión (health check)
        # Hacer una query simple a usuarios (limit 0 para no traer datos, solo verificar que existe)
        response = supabase.table("usuarios").select("id").limit(0).execute()
        logger.info("✅ Conexión a Supabase verificada")

        # Paso 2: Verificar tablas existen
        tables_to_check = ["usuarios", "query_logs", "jobs"]
        for table_name in tables_to_check:
            try:
                supabase.table(table_name).select("id").limit(0).execute()
                logger.info(f"✅ Tabla '{table_name}' existe")
            except Exception as e:
                logger.error(f"❌ Tabla '{table_name}' no existe: {e}")
                logger.info(
                    f"⚠️ Crea las tablas manualmente en Supabase SQL Editor"
                )
                raise

        logger.info("✅ Base de datos Supabase lista")
        return supabase

    except Exception as e:
        logger.error(f"❌ Error inicializando Supabase: {e}")
        raise


def get_connection() -> Client:
    """
    Obtener cliente de Supabase

    En Supabase, no necesitas crear nuevas conexiones.
    El cliente usa connection pooling automático.

    Returns:
        Client: Cliente de Supabase global
    """
    return supabase


def close_connection(conn=None):
    """
    Cerrar conexión (no necesario con Supabase)

    Supabase maneja las conexiones automáticamente.
    Este método existe por compatibilidad con SQLite.

    Args:
        conn: Ignorado (para compatibilidad)
    """
    # Supabase no requiere cerrar conexiones explícitamente
    logger.debug("✅ Connection pooling manejado por Supabase")
    pass
