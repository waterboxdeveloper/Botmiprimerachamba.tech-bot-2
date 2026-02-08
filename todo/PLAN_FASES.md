# Plan de Desarrollo - Bot de Vacantes

## Contexto Consolidado

**Objetivo**: Bot de Telegram que entrega vacantes personalizadas a freelancers.

**Flujo**:
1. Usuario `/perfil` → Configura keywords (ej: "python", "remote", "contract")
2. Usuario `/vacantes` → Bot busca en JobSpy API con esas keywords
3. JobSpy devuelve vacantes freshas (JSON)
4. Bot personaliza con Gemini ("Esta vacante te matchea porque...")
5. Bot envía vacantes personalizadas a Telegram

**Tech Stack**: Python 3.10 + uv, SQLite (usuarios), Telegram, JobSpy API, LangChain + Gemini, APScheduler

**Base de Datos**: SQLite local (MVP) → Supabase luego

**JobSpy API**: rainmanjam/jobspy-api (Docker). Lee `tests/pruebasApi/HALLAZGOS_CONSOLIDADOS.md` si dudas.

---

## FASE 1: Setup Inicial

**Objetivo**: Ambiente listo, dependencias instaladas, estructura base.

### Tareas
- [ ] `FASE_1_1.md` - Crear `pyproject.toml` con dependencias
- [ ] `FASE_1_2.md` - Crear `.env.example` con variables necesarias
- [ ] `FASE_1_3.md` - Setup inicial de directorios y archivos base
- [ ] `FASE_1_4.md` - Verificar instalación de dependencias (uv sync)

---

## FASE 2: Bot Básico

**Objetivo**: Bot conectado a Telegram, responde comandos básicos.

### Tareas
- [ ] `FASE_2_1.md` - Crear `bot/main.py` (entry point)
- [ ] `FASE_2_2.md` - Comando `/start` - Mensaje de bienvenida
- [ ] `FASE_2_3.md` - Comando `/help` - Muestra comandos disponibles
- [ ] `FASE_2_4.md` - Conectar Bot Father → obtener token → enviar token a `.env`

---

## FASE 3: Database (SQLite + Modelos)

**Objetivo**: Guardar y recuperar usuarios con sus keywords.

### Tareas
- [ ] `FASE_3_1.md` - Crear Pydantic models (`database/models.py`)
- [ ] `FASE_3_2.md` - Crear SQLite database + schema (`database/db.py`)
- [ ] `FASE_3_3.md` - CRUD operations para usuarios (`database/queries.py`)
- [ ] `FASE_3_4.md` - Tests unitarios para DB

---

## FASE 4: Handler /perfil

**Objetivo**: Usuario configura su perfil (keywords, location, etc).

### Tareas
- [ ] `FASE_4_1.md` - Handler `/perfil` - Ask keywords
- [ ] `FASE_4_2.md` - Handler `/perfil` - Ask location
- [ ] `FASE_4_3.md` - Handler `/perfil` - Ask job type (freelance/contract/any)
- [ ] `FASE_4_4.md` - Guardar perfil en SQLite

---

## FASE 5: JobSpy Integration

**Objetivo**: Llamar a JobSpy API con keywords del usuario, parsear respuestas.

### Tareas
- [ ] `FASE_5_1.md` - Crear `backend/scrapers/jobspy_client.py`
- [ ] `FASE_5_2.md` - Function: `scrape_jobs(keywords, location, job_type)`
- [ ] `FASE_5_3.md` - Parsear respuesta JSON a Job models
- [ ] `FASE_5_4.md` - Tests: verificar que respuestas sean correctas

---

## FASE 6: Handler /vacantes (Sin AI)

**Objetivo**: Usuario hace `/vacantes` → obtiene vacantes freshas.

### Tareas
- [ ] `FASE_6_1.md` - Handler `/vacantes` - Read keywords from DB
- [ ] `FASE_6_2.md` - Handler `/vacantes` - Call JobSpy API
- [ ] `FASE_6_3.md` - Format jobs para Telegram (link + titulo + empresa)
- [ ] `FASE_6_4.md` - Send jobs to user

---

## FASE 7: AI Personalization

**Objetivo**: LangChain + Gemini personaliza cada vacante.

### Tareas
- [ ] `FASE_7_1.md` - Crear `backend/agents/job_matcher.py`
- [ ] `FASE_7_2.md` - Function: `generate_match_message(user_profile, job)`
- [ ] `FASE_7_3.md` - Integrar LangChain + Gemini API
- [ ] `FASE_7_4.md` - Tests: verificar que los mensajes tengan sentido

---

## FASE 8: Scheduler (Notificaciones Automáticas)

**Objetivo**: Bot envía notificaciones 1-2 veces al día sin que usuario pida.

### Tareas
- [ ] `FASE_8_1.md` - Crear `backend/scheduler.py` (APScheduler setup)
- [ ] `FASE_8_2.md` - Task: Scrape jobs cada X horas
- [ ] `FASE_8_3.md` - Task: Personalize + Send notificaciones a todos los usuarios
- [ ] `FASE_8_4.md` - Handler `/config` - Usuario configura frecuencia (1x día, 2x día)

---

## FASE 9: Main Entry Point

**Objetivo**: Bot + Scheduler corriendo juntos.

### Tareas
- [ ] `FASE_9_1.md` - Crear `main.py` (inicia bot + scheduler)
- [ ] `FASE_9_2.md` - Manejo de graceful shutdown
- [ ] `FASE_9_3.md` - Logging setup
- [ ] `FASE_9_4.md` - Test en local

---

## FASE 10: Deployment

**Objetivo**: Bot corriendo 24/7 en servidor Linux.

### Tareas
- [ ] `FASE_10_1.md` - Create systemd service file
- [ ] `FASE_10_2.md` - Deploy a servidor (DigitalOcean/AWS)
- [ ] `FASE_10_3.md` - Configure monitoring + logs
- [ ] `FASE_10_4.md` - Backup strategy

---

## FASE 11: Polish + Testing

**Objetivo**: Edge cases, error handling, UX improvements.

### Tareas
- [ ] `FASE_11_1.md` - Error handling en todos los handlers
- [ ] `FASE_11_2.md` - Tests de integración (E2E)
- [ ] `FASE_11_3.md` - User feedback + iterate
- [ ] `FASE_11_4.md` - Documentation

---

## Orden de Ejecución

```
FASE 1 (Setup)
    ↓
FASE 2 (Bot básico)
    ↓
FASE 3 (Database)
    ↓
FASE 4 (Perfil)
    ↓
FASE 5 (JobSpy)
    ↓
FASE 6 (Vacantes - sin AI)
    ↓
FASE 7 (AI)
    ↓
FASE 8 (Scheduler)
    ↓
FASE 9 (Main)
    ↓
FASE 10 (Deploy)
    ↓
FASE 11 (Polish)
```

---

## MVP Mínimo (Para empezar a probar)

Completar hasta **FASE 6**: Usuario puede `/perfil` + `/vacantes` y obtiene resultados frescos.

Después agregar:
- FASE 7: AI personalización
- FASE 8: Scheduler automático
