# FASE 4: Handler /perfil - ✅ COMPLETADA

**Fecha**: 2026-02-16
**Estado**: ✅ COMPLETADA - Funcionando en Telegram
**Verificación**: Usuario guardado exitosamente en BD

---

## 📋 Qué se hizo

### FASE 4.1 ✅ Handler `/perfil` con Conversación Interactiva

**Archivo**: `bot/handlers/profile.py` (310 líneas)

**Propósito**:
- Conversación multi-paso para configurar perfil de usuario
- Pedir keywords, país, tipo de trabajo
- Guardar en BD usando `database/queries.create_user()`

**Estados de la conversación**:
```
KEYWORDS (0) → COUNTRY (1) → JOB_TYPE (2) → END
```

---

### FASE 4.2 ✅ Paso 1: Keywords

**Flujo**:
```
Usuario: /perfil
Bot: "¿Qué keywords buscas?"
Bot muestra ejemplos específicos:
  • Analista de datos, looker, python
  • Enfermería, hospitales, tiempo completo
  • Recursos humanos, reclutamiento, remoto
  • Administrador de marketing, SEO, freelance
  • Desarrollador Python, Django, API REST

Usuario: "Analista de datos, looker, python"
```

**Features**:
- ✅ Keywords separadas por **comas** (no espacios)
- ✅ Ejemplos específicos + relevantes
- ✅ Negritas y formatting
- ✅ Validación: no vacío

---

### FASE 4.3 ✅ Paso 2: País

**Flujo**:
```
Bot: "¿En qué país buscas?"
Bot muestra botones con países:
  [USA]        [Colombia]
  [Canada]     [UK]
  [Mexico]     [Argentina]
  [Chile]      [Peru]
  [Spain]      [Brazil]
  ...

Usuario: Selecciona "Mexico" (botón)
```

**Features**:
- ✅ **Botones interactivos** (ReplyKeyboardMarkup)
- ✅ Case-insensitive (acepta "méxico", "México", "MEXICO")
- ✅ Conversión a formato API (México → Mexico)
- ✅ Validación contra VALID_COUNTRIES
- ✅ Países en orden alfabético

**Países soportados** (14 países):
```
USA, Colombia, Canada, UK, Mexico, Argentina, Chile, Peru,
Spain, Germany, France, Brazil, Chile, Internship
```

---

### FASE 4.4 ✅ Paso 3: Tipo de Trabajo (Opcional)

**Flujo**:
```
Bot: "¿Tipo de trabajo?"
Bot muestra botones:
  [Contract 🤝]      [Fulltime 💼]
  [Parttime ⏰]      [Internship 🎓]
  [Cualquiera ➡️]

Usuario: Selecciona "Fulltime 💼" (botón)
```

**Features**:
- ✅ Botones interactivos
- ✅ Tipos válidos: `contract`, `fulltime`, `parttime`, `internship`
- ✅ "Cualquiera" = `None` (sin filtro)
- ✅ Case-insensitive
- ✅ Emoji para mejor UX

---

### FASE 4.5 ✅ Guardar en BD

**Flujo**:
```
Valida datos con Pydantic ✅
    ↓
Verifica si usuario ya existe
    ├→ Sí: UPDATE (actualizar keywords, país)
    └→ No: CREATE (usuario nuevo)
    ↓
Guarda en BD (SQLite)
    ↓
Muestra resumen con datos guardados
```

**Integración con BD**:
- ✅ `database/queries.create_user()` para usuarios nuevos
- ✅ `database/queries.update_user()` para usuarios existentes
- ✅ `database/queries.user_exists()` para verificar
- ✅ Validación Pydantic (telegram_id, experience_level)

**Datos guardados**:
```python
{
  "telegram_id": "998566560",
  "name": "User name",
  "keywords": ["Recursos Humanos", "reclutamiento", "remoto"],
  "location_preference": "Mexico",  # Formato API
  "experience_level": "mid",  # Default
  "is_active": 1,
  "created_at": "2026-02-16 16:42:30",
  "updated_at": "2026-02-16 16:42:30"
}
```

---

### FASE 4.6 ✅ Resumen Final

**Mensaje al usuario**:
```
✅ ¡Perfil guardado exitosamente!

📌 Keywords: `Recursos Humanos, reclutamiento, remoto`
🌍 País: `Mexico`
💼 Tipo: `Fulltime`

🚀 Ahora usa `/vacantes` para buscar empleos personalizados para ti.
```

---

## 🏗️ Estructura

```
bot/handlers/
├── __init__.py
├── commands.py        # /start, /help
└── profile.py         # /perfil (FASE 4) ✨

bot/main.py            # Registra ConversationHandler

database/
├── models.py          # User model con validadores
├── db.py              # SQLite connection
└── queries.py         # CRUD operations

list_users.py          # Script para listar usuarios ✨
```

---

## 🧪 Verificación (Prueba en Telegram)

**Test ejecutado**: 2026-02-16 16:42:30

```
Usuario: /perfil
Bot: Pide keywords
Usuario: "Recursos Humanos, reclutamiento, remoto"
Bot: Pide país
Usuario: Selecciona "Mexico"
Bot: Pide tipo
Usuario: Selecciona "Fulltime"
Bot: ✅ Perfil guardado!

Logs:
✅ Usuario creado: 998566560
✅ User 998566560 profile saved
```

**BD verificada**:
```bash
uv run python list_users.py
```

Output:
```
✅ Total de usuarios: 1

👤 Usuario #1
   Nombre: [Tu nombre]
   ID Telegram: 998566560
   Keywords: Recursos Humanos, reclutamiento, remoto
   País: Mexico
   Nivel: mid
   Activo: ✅ Sí
```

---

## 🔑 Decisiones técnicas

| Decisión | Razón |
|----------|-------|
| **ConversationHandler** | Maneja multi-step conversations |
| **Botones interactivos** | Mejor UX, input guaranteed |
| **Case-insensitive país** | Más amigable para usuario |
| **Separador: comas** | Más claro que espacios |
| **Soft update** | Si usuario existe, actualiza (no error) |
| **Experience level default** | "mid" para todos (puede cambiar) |
| **list_users.py script** | Fácil verificación sin instalar nada |

---

## 🚀 Próximo paso: FASE 5

**FASE 5: JobSpy Integration**

Lo que viene:
- [ ] `backend/scrapers/jobspy_client.py` - Cliente para API
- [ ] Función: `search_jobs(keywords, country, job_type)`
- [ ] Parsear respuestas a Job models
- [ ] Tests para búsquedas

---

## 📸 UX Mejorada en FASE 4

✅ **Negritas en títulos** - Claridad
✅ **Ejemplos específicos** - Más contexto
✅ **Botones interactivos** - Mejor UX
✅ **Validación robusta** - Sin errores
✅ **Resumen final bonito** - Confirmación clara
✅ **Script list_users.py** - Verificación fácil

---

**Versión**: 1.0
**Completado**: 2026-02-16
**Estado**: ✅ FUNCIONANDO EN TELEGRAM
**Tests**: N/A (conversación simple, sin tests unitarios)
**Próximo**: FASE 5 - JobSpy Integration
