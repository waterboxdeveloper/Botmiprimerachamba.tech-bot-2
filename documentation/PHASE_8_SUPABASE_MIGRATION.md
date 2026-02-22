# FASE 8: Migración de BD - SQLite → Supabase

**Fecha**: 2026-02-22
**Estado**: ✅ COMPLETADA (En testing)
**Prioridad**: ALTA (Requerido para producción)

---

## 🎯 Objetivo

Migrar la base de datos de **SQLite local** a **Supabase (PostgreSQL en la nube)** para:
- ✅ Escalabilidad automática
- ✅ Backups automáticos
- ✅ Acceso desde múltiples servidores
- ✅ Cero mantenimiento de infraestructura
- ✅ Preparado para producción

---

## 📊 Antes vs Después

### ANTES (SQLite)
```
Bot en Servidor
  ↓
bot2mvp.db (archivo local)
  ↓
Limitado a 1 servidor
Sin backups automáticos
Sin acceso remoto
```

### DESPUÉS (Supabase)
```
Bot en Servidor (o múltiples)
  ↓
Supabase API (PostgreSQL en nube)
  ↓
Escalable, backups automáticos
Acceso desde cualquier servidor
```

---

## 🔧 Cambios Realizados

### 1️⃣ `database/db.py` - COMPLETAMENTE REESCRITO

**Antes (SQLite):**
```python
def init_db(db_path: str = "bot2mvp.db") -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE...")
    return conn
```

**Después (Supabase):**
```python
def init_db() -> Client:
    """Conecta a Supabase y verifica que tablas existan"""
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    # Verifica tablas: usuarios, query_logs, jobs
    return supabase

def get_connection() -> Client:
    """Retorna cliente global de Supabase (connection pooling automático)"""
    return supabase
```

**Ventajas:**
- ✅ No necesita parámetro `db_path`
- ✅ Connection pooling automático (Supabase lo maneja)
- ✅ No necesita cerrar conexiones explícitamente

---

### 2️⃣ `database/queries.py` - Todas las funciones actualizadas

**Antes (SQLite):**
```python
def create_user(conn: sqlite3.Connection, telegram_id: str, name: str, ...):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO usuarios...")
    conn.commit()
```

**Después (Supabase):**
```python
def create_user(user: User) -> Optional[User]:
    """Crea usuario usando cliente Supabase"""
    supabase = get_connection()
    user_data = {
        "telegram_id": user.telegram_id,
        "keywords": json.dumps(user.keywords),  # JSON
        ...
    }
    response = supabase.table("usuarios").insert(user_data).execute()
    return user if response.data else None
```

**Cambios clave:**
| Aspecto | SQLite | Supabase |
|--------|--------|---------|
| **Parámetro** | `conn` | No necesario |
| **Serialización** | Strings directos | JSON para listas |
| **Queries** | SQL raw | ORM REST API |
| **Conteo** | `COUNT(*)` | `.select("id", count="exact")` |

---

### 3️⃣ `bot/handlers/profile.py` - Actualizado

**Cambios:**
```python
# ANTES
conn = get_connection()
create_user(conn, telegram_id, name, keywords, ...)
conn.close()

# DESPUÉS
user = User(telegram_id=telegram_id, name=name, keywords=keywords, ...)
result = create_user(user)
# Sin conexión explícita, Supabase lo maneja
```

---

### 4️⃣ `bot/main.py` - Ajustado

```python
# ANTES
init_db("bot2mvp.db")

# DESPUÉS
try:
    init_db()  # Sin parámetros
    logger.info("✅ Base de datos Supabase inicializada")
except Exception as e:
    logger.error(f"❌ Error inicializando BD: {e}")
    raise
```

---

### 5️⃣ `.env` - Nuevas credenciales

**Agregado:**
```env
# Supabase (BD en la nube - PostgreSQL)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=sb_publishable_YOUR_ANON_KEY
SUPABASE_SERVICE_ROLE=sb_secret_YOUR_SERVICE_ROLE_KEY
```

**Removido:**
```env
# Google Sheets (ya no necesario)
GOOGLE_SHEETS_CREDENTIALS=./credentials.json
GOOGLE_SHEETS_ID=your_sheet_id_here
```

---

### 6️⃣ `pyproject.toml` - Nueva dependencia

```toml
supabase = "^2.28.0"  # Agregar a dependencies
```

**Instalada con:**
```bash
uv add supabase
```

---

## 📋 Tablas Creadas en Supabase

### Tabla: `usuarios`
```sql
CREATE TABLE usuarios (
  id BIGSERIAL PRIMARY KEY,
  telegram_id TEXT UNIQUE NOT NULL,
  name TEXT NOT NULL,
  email TEXT,
  phone TEXT,
  keywords JSONB DEFAULT '[]'::jsonb,        ← JSON para arrays
  location_preference TEXT,
  experience_level TEXT DEFAULT 'mid',
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_usuarios_telegram_id ON usuarios(telegram_id);
CREATE INDEX idx_usuarios_is_active ON usuarios(is_active);
```

### Tabla: `query_logs` (Rate Limiting)
```sql
CREATE TABLE query_logs (
  id BIGSERIAL PRIMARY KEY,
  telegram_id TEXT NOT NULL,
  query_type TEXT DEFAULT 'vacantes',
  timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  status TEXT DEFAULT 'success'
);

CREATE INDEX idx_query_logs_telegram_id ON query_logs(telegram_id);
CREATE INDEX idx_query_logs_timestamp ON query_logs(timestamp);
```

### Tabla: `jobs` (Opcional - para cache)
```sql
CREATE TABLE jobs (
  id BIGSERIAL PRIMARY KEY,
  job_id TEXT UNIQUE,
  title TEXT NOT NULL,
  company TEXT,
  job_url TEXT UNIQUE NOT NULL,
  location TEXT,
  is_remote BOOLEAN,
  job_type TEXT,
  source TEXT,
  description TEXT,
  date_posted TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_jobs_job_url ON jobs(job_url);
```

---

## ✅ Testing Completado

### Script de Prueba: `test_supabase_connection.py`

```bash
✅ TEST 1: Importar módulos
✅ TEST 2: Conectar a Supabase
✅ TEST 3: Obtener cliente
✅ TEST 4: Contar usuarios → 0 (BD vacía)
✅ TEST 5: Contar query logs → 0
✅ TEST 6: Crear usuario de prueba
   → Usuario: "999999999"
   → Keywords: ['python', 'remote']
   → País: USA
✅ TEST 7: Obtener usuario de BD
   → Usuario encontrado: "Test User"
   → Datos correctos
```

**Resultado:** ✅ TODOS LOS TESTS PASARON

---

## 🚀 Flujo de Uso (Post-Migración)

### Usuario configura perfil (/perfil)
```
User → Bot → Profile Handler → create_user(User)
                                    ↓
                            Supabase API
                                    ↓
                            INSERT usuarios
                                    ↓
                            ✅ Usuario guardado
```

### Usuario busca empleos (/vacantes)
```
User → Bot → Jobs Handler → can_make_query()
                                ↓
                        query_logs table (rate limit)
                                ↓
                    ✅ Permitido / ❌ Bloqueado
                                ↓
                        get_user_profile(id)
                                ↓
                        SELECT * FROM usuarios
                                ↓
                    Obtiene keywords + país
                                ↓
                        Busca employos normalmente
```

---

## ⚠️ Diferencias Importantes

### Sintaxis de Queries

| Operación | SQLite | Supabase |
|-----------|--------|---------|
| **SELECT** | `.fetchall()` | `.select("*").execute()` |
| **INSERT** | `.execute("INSERT...")` | `.insert(dict).execute()` |
| **UPDATE** | `.execute("UPDATE...")` | `.update(dict).eq(...).execute()` |
| **DELETE** | `.execute("DELETE...")` | `.update({"is_active": False})` |
| **COUNT** | `SELECT COUNT(*)` | `.select("id", count="exact")` |
| **WHERE** | `.where("x = ?")` | `.eq("x", value)` |
| **Conexión** | `conn.close()` | No necesario (pooling) |

### JSON Handling

**SQLite (texto):**
```python
keywords_json = json.dumps(["python", "remote"])
# Guardar como string
```

**Supabase (JSONB):**
```python
keywords_json = json.dumps(["python", "remote"])
# Supabase lo convierte a JSONB automáticamente
# Descargar: json.loads(user_data["keywords"])
```

---

## 🔐 Seguridad

### .env Protection
```bash
# ✅ CORRECTO
.env → .gitignore (NUNCA commitar)

# ❌ INCORRECTO
SUPABASE_KEY hardcodeado en código
```

### Row Level Security (RLS)
```sql
-- Habilitado pero permitiendo acceso desde bot
ALTER TABLE usuarios ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow service role" ON usuarios
  AS PERMISSIVE FOR ALL
  USING (true)
  WITH CHECK (true);
```

---

## 📈 Ventajas Post-Migración

| Feature | SQLite | Supabase |
|---------|--------|----------|
| **Escalabilidad** | ⚠️ Limitada | ✅ Automática |
| **Backups** | ❌ Manual | ✅ Automáticos (diarios) |
| **Acceso remoto** | ❌ Solo local | ✅ Desde cualquier lugar |
| **Múltiples servidores** | ❌ No | ✅ Sí |
| **Monitoreo** | ❌ Ninguno | ✅ Dashboard Supabase |
| **Costo** | ✅ Gratis | 🟡 Gratis (plan free) |
| **Mantenimiento** | ⚠️ Manual | ✅ Supabase lo hace |

---

## ⚡ Performance

### Latencia
- **SQLite (local):** ~0ms
- **Supabase (HTTP):** ~50-100ms

**Impacto:** Mínimo para este bot (queries no son críticas por latencia)

### Queries por segundo
- **Supabase Free:** 500,000/mes = ~278 RPS
- **Bot típico:** ~1-2 RPS
- **Capacidad:** ✅ Más que suficiente

---

## 🎯 Próximos Pasos

1. **Testing End-to-End** (próximo paso)
   - [ ] Levantar bot
   - [ ] /start command
   - [ ] /perfil command (crear usuario)
   - [ ] /vacantes command (verificar que lee de Supabase)
   - [ ] Verificar que datos se guardan en Supabase

2. **Rate Limiting** (verificar)
   - [ ] 1ª búsqueda: ✅ Permitida
   - [ ] 2ª búsqueda: ✅ Permitida
   - [ ] 3ª búsqueda: ✅ Permitida
   - [ ] 4ª búsqueda: ❌ Bloqueada

3. **Cleanup** (post-test)
   - [ ] Remover test_supabase_connection.py
   - [ ] Remover bot2mvp.db (no es necesario)
   - [ ] Hacer commit

4. **Documentación** (actualizar)
   - [ ] Actualizar README
   - [ ] Documentar credenciales Supabase
   - [ ] Guía para otros developers

---

## 📝 Checklist de Migración

- [x] Crear proyecto en Supabase
- [x] Crear tablas (usuarios, query_logs, jobs)
- [x] Actualizar `database/db.py`
- [x] Actualizar `database/queries.py`
- [x] Actualizar `bot/handlers/profile.py`
- [x] Actualizar `bot/main.py`
- [x] Actualizar `.env`
- [x] Instalar dependencia `supabase`
- [x] Crear tests
- [x] Testing básico (conexión OK)
- [ ] Testing end-to-end ← **PRÓXIMO PASO**
- [ ] Commit
- [ ] Deploy a producción

---

## 🔗 Referencias

- **Supabase Docs**: https://supabase.com/docs
- **Supabase Python SDK**: https://github.com/supabase/supabase-py
- **PostgREST API**: https://postgrest.org/
- **Project URL**: https://app.supabase.com/projects/neuqdvstcmvehewrmxfs

---

**Status**: ✅ Migración completada, testing end-to-end pendiente
