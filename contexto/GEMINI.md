# Gemini Code - Guía de Respuesta y Contexto

## Propósito
Este documento define cómo Claude debe comunicarse y trabajar en este proyecto. El proyecto es tanto una solución de producción como una oportunidad de **aprendizaje**, por lo que cada paso debe ser explicado claramente.

---

## 1. Contexto Siempre Presente

Antes de cualquier sugerencia, Claude DEBE verificar:

### 📋 idea.md
- **Problema**: Freelancers buscan vacantes de forma manual e ineficiente
- **Solución**: Bot de Telegram con notificaciones personalizadas 1-2 veces al día
- **Workflow**:
  1. Usuario → `/perfil` (configura keywords: ux/ui, design system, etc)
  2. Sistema → Scraping automático de vacantes
  3. AI → LangChain + Gemini 2.5 Flash personalizan cada vacante
  4. Bot → Envía resultados personalizados al usuario
- **Storage**: Google Sheets (usuarios + vacantes simplificado)
- **JobSpy API**: rainmanjam/jobspy-api (DOCKERIZADO)

### 🛠️ stack.md
- **Lenguaje**: Python 3.10+ con `uv` (NO pip)
- **Bot**: python-telegram-bot
- **Database**: Google Sheets
- **Data Validation**: Pydantic>=2.0 (validación de User y Job models)
- **AI**: LangChain + Gemini 2.5 Flash
- **Scraping**: rainmanjam/jobspy-api (Docker)
- **Scheduling**: APScheduler
- **Package Manager**: `uv` (uv sync, uv pip, etc)
- **Deployment**: Linux Server + systemd

### 🔍 scrapersdoc.md
**OPCIÓN SELECCIONADA**: `rainmanjam/jobspy-api` ⭐
- ✅ API FastAPI lista para producción
- ✅ **DOCKERIZADA** (contenedor)
- ✅ JSON nativo
- ✅ Autenticación por API key
- ✅ Rate limiting + proxy support
- ✅ CORS habilitado

---

## 2. Estilo de Respuesta: Explicativo y Educativo

### ✅ HACER:
- **Explicar el propósito** de cada paso
- **Mostrar la estructura** antes de escribir código
- **Documentar decisiones** técnicas (por qué esto y no lo otro)
- **Incluir comentarios** en código clave
- **Referencias**: "Esto se define en stack.md línea X" o "Como menciona idea.md"
- **Paso a paso**: "1. Primero... 2. Luego... 3. Finalmente..."
- **Contexto visual**: Diagramas ASCII o explicaciones claras

### ❌ NO HACER:
- Saltar pasos sin explicar
- Sugerir tecnologías no mencionadas en stack.md
- Hacer cambios sin explicar el porqué
- Usar `git add .` sin que el usuario lo pida explícitamente
- Hacer `git commit` sin que el usuario lo pida explícitamente
- Cambiar decisiones ya tomadas en idea.md/stack.md
- Agregar features no pedidas

---

## 3. Workflow de Implementación

### Cada Feature Importante Sigue Este Orden:

**1️⃣ TESTS PRIMERO** (Test-Driven Development)
```bash
# 1. Crear tests en tests/unit/...
pytest tests/unit/[componente]/ -v
# Deben FALLAR (red phase)

# 2. Implementar código
# Tests deben PASAR (green phase)

# 3. Refactor si necesario
# Tests siguen PASANDO
```

**2️⃣ LUEGO DOCUMENTACIÓN**
```
- Actualizar el archivo phase correspondiente: phase1_done.md, phase2_done.md, etc
- Incluir:
  - Qué se hizo (resumen)
  - Por qué (decisiones técnicas)
  - Cómo verificarlo (comandos de test)
  - Próximo paso
```

**3️⃣ NUNCA commit sin permiso**
```bash
# Claude NUNCA ejecuta:
git add .
git commit -m "..."

# Usuario es quien controla commits:
# Usuario: "haz commit de esto"
# Claude: Ejecuta y verifica
```

---

## 4. Convenciones de Trabajo

### Estructura de Directorios (según idea.md + stack.md)
```
botmvp/
├── contexto/              # Este directorio (referencias del proyecto)
│   ├── idea.md
│   ├── stack.md
│   ├── scrapersdoc.md
│   ├── CLAUDE.md          # Este archivo
│   └── ...
├── todo/                  # Fases de implementación
│   ├── 01_SETUP.md
│   ├── 02_FIREBASE.md
│   ├── ...
│   └── 07_DEPLOYMENT.md
├── bot/                   # Código del bot
│   ├── handlers/
│   ├── main.py
│   └── ...
├── backend/               # Servicios backend
│   ├── scrapers/          # rainmanjam/jobspy-api integration
│   ├── agents/            # LangChain agent (JobMatcher)
│   ├── scheduler.py       # APScheduler tasks
│   └── ...
├── database/              # Firebase Firestore ops
│   ├── firebase_init.py
│   ├── models.py
│   ├── queries/
│   └── ...
├── tests/                 # Tests (pytest)
│   ├── unit/
│   ├── integration/
│   └── conftest.py
├── main.py                # Entry point (bot + scheduler)
├── pyproject.toml         # Dependencies (uv)
├── uv.lock                # Locked dependencies
├── .env.example           # Template
└── .env                   # Local (NO versionar)
```

### Archivos de Documentación Post-Implementation
```
documentation/
├── PHASE_1_SETUP_DONE.md
├── PHASE_2_FIREBASE_DONE.md
├── PHASE_3_DATABASE_DONE.md
├── PHASE_4_BACKEND_DONE.md
├── PHASE_5_BOT_DONE.md
├── PHASE_6_TESTS_DONE.md
└── PHASE_7_DEPLOYMENT_DONE.md
```

---

## 5. Reglas de Oro

| Regla | Cumplimiento |
|-------|--------------|
| **Siempre revisar idea.md antes de sugerir** | 100% |
| **Siempre revisar stack.md antes de usar tech** | 100% |
| **JobSpy = rainmanjam/jobspy-api (Docker)** | Siempre |
| **Package manager = uv (NO pip)** | Siempre |
| **Explicar cada paso** | Obligatorio |
| **Tests ANTES de documentación** | Obligatorio |
| **NUNCA commit sin permiso** | Obligatorio |
| **Responder en español** | Preferencia del usuario |

---

## 6. Ejemplo de Respuesta Correcta

### ❌ INCORRECTO:
```
Voy a crear el archivo bot/handlers/command_handler.py
```

### ✅ CORRECTO:
```
## Paso 1: Crear Command Handlers

**Propósito** (según idea.md):
- Manejar comandos del usuario (/perfil, /vacantes, /help, etc)
- Iniciar la conversación con el bot de Telegram

**Estructura** (según stack.md):
- Usamos python-telegram-bot para los handlers
- Handlers son async functions que reciben Update y ContextTypes

**Pasos:**
1. Crear archivo bot/handlers/command_handler.py
2. Implementar:
   - `cmd_start()` - Mensaje de bienvenida
   - `cmd_help()` - Muestra comandos disponibles
   - etc...

**Por qué esta estructura:**
- Separar handlers por tipo (commands, messages, etc)
- Facilita testing y mantenimiento
- Escalable cuando agregamos más handlers

Voy a crear el archivo ahora:
```

---

## 7. Verificación Antes de Empezar

- ✅ ¿Entiendes idea.md? → Problema, solución, workflow
- ✅ ¿Entiendes stack.md? → Tech stack, Python 3.10+, uv, Firebase, Gemini
- ✅ ¿Sabes cuál JobSpy usar? → rainmanjam/jobspy-api (Docker)
- ✅ ¿Tests ANTES de docs? → Sí
- ✅ ¿NUNCA commit sin permiso? → Sí
- ✅ ¿Explicar cada paso? → Sí

---

## 8. Contacto y Preguntas

Si Claude tiene dudas:
1. Preguntar al usuario ANTES de proceder
2. Nunca asumir decisiones técnicas
3. Referirse siempre a contexto/ para verificar

Ejemplo de pregunta correcta:
```
Antes de continuar con FASE 2, tengo una pregunta:
¿Debo usar Firebase Authentication para login seguro,
o solo Telegram ID es suficiente? (idea.md no especifica esto)
```

---

**Última actualización**: 2026-01-08
**Versión**: 1.0
**Estado**: ✅ Listo para empezar
