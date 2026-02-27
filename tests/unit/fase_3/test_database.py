"""
Tests para database/db.py y database/queries.py

Propósito: Probar operaciones CRUD en SQLite
Framework: pytest con fixture para BD de test en memoria
Complejidad: ALTA (transacciones, validaciones, edge cases)
"""

import pytest
from datetime import datetime
from database.models import User


class TestDatabaseConnection:
    """Tests para inicialización de la base de datos"""

    def test_database_initializes(self):
        """
        RED TEST: database/db.py debe poder importarse y conexión funciona
        """
        from database.db import init_db

        # Debe retornar una conexión válida
        conn = init_db(":memory:")  # SQLite en memoria para tests
        assert conn is not None

    def test_database_creates_tables(self):
        """
        RED TEST: init_db debe crear tabla 'usuarios' automáticamente
        """
        from database.db import init_db

        conn = init_db(":memory:")
        cursor = conn.cursor()

        # Verificar que la tabla existe
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='usuarios'"
        )
        result = cursor.fetchone()
        assert result is not None, "Tabla 'usuarios' no existe"

    def test_database_creates_correct_schema(self):
        """
        RED TEST: Tabla 'usuarios' debe tener columnas correctas
        """
        from database.db import init_db

        conn = init_db(":memory:")
        cursor = conn.cursor()

        # Obtener info de columnas
        cursor.execute("PRAGMA table_info(usuarios)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}  # nombre: tipo

        # Verificar columnas requeridas
        required_columns = ["telegram_id", "name", "keywords", "experience_level"]
        for col in required_columns:
            assert col in columns, f"Columna '{col}' no existe"


class TestUserCRUD:
    """Tests para CRUD operations de usuarios"""

    @pytest.fixture
    def db_connection(self):
        """Fixture: crear BD en memoria para cada test"""
        from database.db import init_db

        conn = init_db(":memory:")
        yield conn
        conn.close()

    def test_create_user(self, db_connection):
        """
        RED TEST: Crear usuario debe insertarse correctamente

        Escenario:
        - Llamar create_user con datos válidos
        - Usuario debe guardarse en BD
        - Debe retornar success
        """
        from database.queries import create_user

        result = create_user(
            db_connection,
            telegram_id="123456789",
            name="Juan Pérez",
            keywords=["python", "remote"],
            location_preference="Remote",
            experience_level="senior"
        )

        assert result is True, "create_user debe retornar True"

    def test_create_user_duplicate_telegram_id(self, db_connection):
        """
        RED TEST: No se puede crear dos usuarios con mismo telegram_id

        Escenario:
        - Crear usuario con ID "123"
        - Intentar crear otro con ID "123"
        - Debe fallar (raise exception o retornar False)
        """
        from database.queries import create_user

        # Crear primer usuario
        create_user(
            db_connection,
            telegram_id="123",
            name="User 1",
            keywords=["python"],
            experience_level="mid"
        )

        # Intentar crear duplicate
        with pytest.raises(Exception):  # IntegrityError o similar
            create_user(
                db_connection,
                telegram_id="123",
                name="User 2",
                keywords=["java"],
                experience_level="mid"
            )

    def test_get_user_by_telegram_id(self, db_connection):
        """
        RED TEST: get_user debe retornar usuario correcto

        Escenario:
        - Crear usuario
        - Recuperar por telegram_id
        - Verificar que los datos coinciden
        """
        from database.queries import create_user, get_user

        # Crear usuario
        create_user(
            db_connection,
            telegram_id="999",
            name="María García",
            keywords=["ui/ux", "design"],
            experience_level="junior"
        )

        # Recuperar
        user = get_user(db_connection, "999")

        assert user is not None
        assert user.telegram_id == "999"
        assert user.name == "María García"
        assert "ui/ux" in user.keywords

    def test_get_user_not_found(self, db_connection):
        """
        RED TEST: get_user con ID inexistente debe retornar None
        """
        from database.queries import get_user

        user = get_user(db_connection, "nonexistent")
        assert user is None

    def test_update_user_keywords(self, db_connection):
        """
        RED TEST: update_user debe actualizar keywords

        Escenario:
        - Crear usuario con keywords ["python"]
        - Actualizar a ["python", "javascript"]
        - Verificar que se actualizó
        """
        from database.queries import create_user, get_user, update_user

        # Crear usuario
        create_user(
            db_connection,
            telegram_id="555",
            name="Test User",
            keywords=["python"],
            experience_level="mid"
        )

        # Actualizar keywords
        update_user(
            db_connection,
            telegram_id="555",
            keywords=["python", "javascript", "react"]
        )

        # Verificar
        user = get_user(db_connection, "555")
        assert len(user.keywords) == 3
        assert "javascript" in user.keywords

    def test_update_user_location(self, db_connection):
        """
        RED TEST: update_user debe actualizar location_preference
        """
        from database.queries import create_user, get_user, update_user

        create_user(
            db_connection,
            telegram_id="666",
            name="User",
            keywords=["python"],
            location_preference="USA",
            experience_level="mid"
        )

        update_user(db_connection, telegram_id="666", location_preference="Colombia")

        user = get_user(db_connection, "666")
        assert user.location_preference == "Colombia"

    def test_delete_user(self, db_connection):
        """
        RED TEST: delete_user debe eliminar usuario de BD

        Escenario:
        - Crear usuario
        - Eliminar usuario
        - Intentar recuperar (debe ser None)
        """
        from database.queries import create_user, get_user, delete_user

        create_user(
            db_connection,
            telegram_id="777",
            name="To Delete",
            keywords=["python"],
            experience_level="mid"
        )

        # Eliminar
        delete_user(db_connection, "777")

        # Verificar que no existe
        user = get_user(db_connection, "777")
        assert user is None


class TestUserValidation:
    """Tests para validación de datos de usuario"""

    @pytest.fixture
    def db_connection(self):
        """Fixture: BD en memoria"""
        from database.db import init_db

        conn = init_db(":memory:")
        yield conn
        conn.close()

    def test_create_user_invalid_telegram_id(self, db_connection):
        """
        RED TEST: telegram_id vacío debe fallar
        """
        from database.queries import create_user

        with pytest.raises(Exception):  # ValueError o ValidationError
            create_user(
                db_connection,
                telegram_id="",
                name="Test",
                keywords=["python"],
                experience_level="mid"
            )

    def test_create_user_invalid_experience_level(self, db_connection):
        """
        RED TEST: experience_level debe ser junior/mid/senior
        """
        from database.queries import create_user

        with pytest.raises(Exception):  # ValueError o ValidationError
            create_user(
                db_connection,
                telegram_id="111",
                name="Test",
                keywords=["python"],
                experience_level="invalid_level"  # ❌ Inválido
            )

    def test_keywords_stored_as_json(self, db_connection):
        """
        RED TEST: keywords (lista) debe almacenarse como JSON en SQLite

        Escenario:
        - Guardar usuario con keywords ["python", "javascript"]
        - Recuperar de BD
        - Debe desserializarse correctamente a lista
        """
        from database.queries import create_user, get_user

        keywords = ["python", "javascript", "react", "remote"]
        create_user(
            db_connection,
            telegram_id="888",
            name="Test",
            keywords=keywords,
            experience_level="mid"
        )

        user = get_user(db_connection, "888")
        assert isinstance(user.keywords, list)
        assert user.keywords == keywords


class TestPydanticIntegration:
    """Tests para integración con Pydantic models"""

    @pytest.fixture
    def db_connection(self):
        """Fixture: BD en memoria"""
        from database.db import init_db

        conn = init_db(":memory:")
        yield conn
        conn.close()

    def test_get_user_returns_pydantic_model(self, db_connection):
        """
        RED TEST: get_user debe retornar modelo Pydantic User (no dict)
        """
        from database.queries import create_user, get_user

        create_user(
            db_connection,
            telegram_id="999",
            name="Test",
            keywords=["python"],
            experience_level="mid"
        )

        user = get_user(db_connection, "999")

        # Debe ser instancia de User (Pydantic model)
        assert isinstance(user, User)
        assert hasattr(user, "telegram_id")
        assert hasattr(user, "name")
        assert hasattr(user, "keywords")
