# FASE 3: Database (SQLite + Modelos) - ✅ COMPLETADA

**Fecha**: 2026-02-16
**Estado**: ✅ COMPLETADA - 14/14 TESTS PASSED
**Tests**: 14 (MUCHO MÁS ROBUSTOS que FASE 2)

---

## 📋 Qué se hizo

### FASE 3.1 ✅ Pydantic Models (`database/models.py`)

**Modificaciones**:
- Agregado `field_validator` para validar `telegram_id` (no vacío)
- Agregado `field_validator` para validar `experience_level` (junior/mid/senior)
- Modelo `User` ahora valida datos automáticamente

**Validaciones**:
```python
@field_validator('telegram_id')
def validate_telegram_id(cls, v):
    if not v or not v.strip():
        raise ValueError('telegram_id no puede estar vacío')
    return v

@field_validator('experience_level')
def validate_experience_level(cls, v):
    valid_levels = ['junior', 'mid', 'senior']
    if v not in valid_levels:
        raise ValueError(f'experience_level debe ser uno de {valid_levels}')
    return v
```

---

### FASE 3.2 ✅ SQLite Database (`database/db.py`)

**Archivo**: `database/db.py` (120 líneas)

**Funciones**:
- `init_db(db_path)` - Inicializar BD, crear tablas
- `get_connection(db_path)` - Obtener conexión existente
- `close_connection(conn)` - Cerrar conexión

**Tablas creadas**:
1. **usuarios**
   - `telegram_id` (PRIMARY KEY)
   - `name`, `email`, `phone`
   - `keywords` (JSON)
   - `location_preference`, `experience_level`
   - `is_active`, `created_at`, `updated_at`

2. **jobs** (para guardar vacantes)
   - `id` (PRIMARY KEY)
   - Campos de trabajo (title, company, url, etc)
   - `sent_to` (JSON list de telegram_ids)

**Features**:
- ✅ Soporte para `:memory:` (tests)
- ✅ `row_factory = sqlite3.Row` (retorna rows como dict-like)
- ✅ Logging automático

---

### FASE 3.3 ✅ CRUD Operations (`database/queries.py`)

**Archivo**: `database/queries.py` (330 líneas)

**Funciones CRUD**:

#### CREATE
```python
create_user(
    conn, telegram_id, name, keywords,
    experience_level="mid",
    location_preference=None, email=None, phone=None
) → bool
```
- Valida con Pydantic
- Serializa keywords a JSON
- Maneja IntegrityError (duplicate telegram_id)

#### READ
```python
get_user(conn, telegram_id) → Optional[User]
get_all_users(conn) → List[User]
```
- Retorna solo usuarios activos (is_active=1)
- Deserializa keywords de JSON
- Retorna modelos Pydantic

#### UPDATE
```python
update_user(
    conn, telegram_id,
    name=None, keywords=None, experience_level=None,
    location_preference=None, email=None, phone=None, is_active=None
) → bool
```
- Actualiza solo campos no-None
- Actualiza `updated_at` automáticamente
- Serializa keywords a JSON

#### DELETE
```python
delete_user(conn, telegram_id) → bool
```
- Soft delete (marca `is_active=False`)
- Mantiene historial en BD

#### UTILITIES
```python
user_exists(conn, telegram_id) → bool
count_active_users(conn) → int
```

---

### FASE 3.4 ✅ Tests Unitarios (`tests/unit/fase_3/test_database.py`)

**Archivo**: `tests/unit/fase_3/test_database.py` (330 líneas)

**14 Tests robustos**:

#### TestDatabaseConnection (3 tests)
- ✅ `test_database_initializes` - Conexión funciona
- ✅ `test_database_creates_tables` - Tabla existe
- ✅ `test_database_creates_correct_schema` - Columnas correctas

#### TestUserCRUD (7 tests)
- ✅ `test_create_user` - Crear usuario
- ✅ `test_create_user_duplicate_telegram_id` - No permite duplicates
- ✅ `test_get_user_by_telegram_id` - Obtener usuario
- ✅ `test_get_user_not_found` - Retorna None si no existe
- ✅ `test_update_user_keywords` - Actualizar keywords
- ✅ `test_update_user_location` - Actualizar ubicación
- ✅ `test_delete_user` - Soft delete

#### TestUserValidation (3 tests)
- ✅ `test_create_user_invalid_telegram_id` - Valida telegram_id no vacío
- ✅ `test_create_user_invalid_experience_level` - Valida experience_level
- ✅ `test_keywords_stored_as_json` - Keywords se serializan correctamente

#### TestPydanticIntegration (1 test)
- ✅ `test_get_user_returns_pydantic_model` - get_user retorna User model

---

## 🏗️ Estructura creada

```
database/
├── __init__.py
├── models.py             # ✏️ ACTUALIZADO (validadores)
├── db.py                 # ✨ NUEVO (init_db, conexión)
└── queries.py            # ✨ NUEVO (CRUD operations)

tests/unit/fase_3/
├── __init__.py
└── test_database.py      # ✨ NUEVO (14 tests)

documentation/
└── PHASE_3_DONE.md       # ✨ NUEVO (este archivo)
```

---

## 📊 Resultados

```bash
uv run pytest tests/unit/fase_3/ -v
```

**Output**:
```
14 passed in 0.01s ✅
```

---

## 🔑 Decisiones técnicas

| Decisión | Razón |
|----------|-------|
| **SQLite** | Simple, sin dependencias externas, perfecto para MVP |
| **Soft delete** | Mantiene historial, reversible |
| **JSON para keywords** | Flexible, permite cambios dinámicos |
| **Pydantic models** | Validación automática, type hints |
| **Fixtures en memoria** | Tests rápidos, sin efectos secundarios |
| **14 tests robustos** | Cubre CRUD, validaciones, edge cases |

---

## 🧪 Features de los tests

✅ **Fixtures**: BD en memoria para cada test
✅ **Validaciones**: Test de datos inválidos
✅ **Edge cases**: Duplicates, not found, soft delete
✅ **Integración**: Pydantic ↔ SQLite
✅ **JSON serialization**: keywords como JSON
✅ **Transacciones**: Commit automático

---

## 📈 Comparación con FASE 2

| Métrica | FASE 2 | FASE 3 |
|---------|--------|--------|
| Tests | 12 | 14 |
| Complejidad | Baja | Alta |
| Cobertura | Básica | Robusta |
| Fixtures | No | Sí |
| Edge cases | No | Sí |
| Validaciones | Mocks | Reales |

---

## 🚀 Próximo paso: FASE 4

**FASE 4: Handler `/perfil`**

Lo que viene:
- [ ] Crear conversation handler para `/perfil`
- [ ] Ask keywords (conversación interactiva)
- [ ] Ask location preference
- [ ] Ask experience level
- [ ] Guardar usuario en DB
- [ ] Tests para conversation flow

---

**Versión**: 1.0
**Completado**: 2026-02-16
**Estado**: ✅ LISTO PARA FASE 4
**Tests**: 14/14 PASSED 🎉
