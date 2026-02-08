# Tech Stack

El proyecto usa estas tecnologías. Nada de Google Cloud Functions, todo es simple.

---

## 🐍 Python

**Versión**: Python 3.10+

**Por qué**: Es lo mejor para bots, automatización y AI.

---

## 📦 Package Manager: uv

**Para qué**: Instalar dependencias (como npm para Python pero más rápido).

```bash
uv venv .venv              # Crear ambiente
source .venv/bin/activate  # Activar
uv sync                    # Instalar dependencias
```

---

## 🗄️ Base de Datos: Google Sheets

**Por qué**: Simple, visual, gratis. Abres la hoja y ves los datos.

Dos hojas:
- **Usuarios**: telegram_id, name, email, keywords, location, level, frequency, active, created_at
- **Vacantes**: title, company, job_url, location, salary_min, salary_max, date_posted, sent_to

**Librería**:
```bash
uv pip install google-api-python-client google-auth-oauthlib
```

---

## 📋 Validación: Pydantic

**Para qué**: Asegurar que los datos sean correctos antes de guardarlos.

Ejemplo:
- Si un usuario no tiene email válido, Pydantic lo rechaza
- Si un salary_min es mayor que salary_max, lo detecta

```bash
uv pip install pydantic>=2.0
```

---

## 🤖 AI: LangChain + Gemini

**LangChain**: Orquesta el flujo de AI (llamadas a Gemini, procesamiento de datos).

**Gemini 2.5 Flash**: El modelo de IA que genera mensajes personalizados sobre vacantes.

```bash
uv pip install langchain langchain-google-genai google-generativeai
```

**Necesitas**: API key de Gemini (gratis en Google AI Studio).

---

## 📱 Bot: Telegram

**Librería**: `python-telegram-bot`

Comandos que el usuario usa:
- `/perfil` - Configura qué busca
- `/vacantes` - Ve vacantes recientes
- `/help` - Ayuda

```bash
uv pip install python-telegram-bot
```

---

## 📡 API de Vacantes: JobSpy

**Repo**: https://github.com/rainmanjam/jobspy-api

Corre en Docker. Es la API que busca vacantes en LinkedIn, Indeed, etc.

**Si tienes dudas**: Lee `tests/pruebasApi/HALLAZGOS_CONSOLIDADOS.md`

---

## ⏰ Scheduler: APScheduler

**Para qué**: Ejecutar tareas periódicamente (buscar vacantes cada día a las 9am, por ejemplo).

```bash
uv pip install apscheduler
```

---

## 🌍 Deployment: Linux Server

**Dónde corre**: Un servidor Linux (DigitalOcean, AWS, Linode, etc).

**Cómo**: Como un servicio systemd que siempre está corriendo.

```ini
[Unit]
Description=Freelance Vacancy Bot
After=network.target

[Service]
Type=simple
User=botmvp
WorkingDirectory=/home/botmvp/botmvp
ExecStart=/home/botmvp/botmvp/.venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

---

## 🔐 Variables de Entorno

Crear `.env` en el root del proyecto:

```env
TELEGRAM_BOT_TOKEN=tu_token
GEMINI_API_KEY=tu_key
JOBSPY_API_URL=http://localhost:8000
GOOGLE_SHEETS_ID=tu_sheet_id
NOTIFICATION_TIMEZONE=America/Bogota
```

**Nunca** commitear `.env`.

---

## 📋 Dependencias

```bash
uv pip install \
  python-telegram-bot \
  google-api-python-client \
  google-auth-oauthlib \
  pydantic \
  langchain \
  langchain-google-genai \
  google-generativeai \
  apscheduler \
  requests \
  python-dotenv
```

---

## Resumen

| Componente | Tecnología | Para qué |
|---|---|---|
| Lenguaje | Python 3.10+ | Core |
| Package Manager | uv | Instalar deps |
| Database | Google Sheets | Guardar usuarios y vacantes |
| Validación | Pydantic | Datos correctos |
| AI | LangChain + Gemini | Personalizar vacantes |
| Bot | python-telegram-bot | Interfaz Telegram |
| Scraper | JobSpy API (Docker) | Buscar vacantes |
| Scheduler | APScheduler | Tareas periódicas |
| Deploy | Linux Server + systemd | Servidor |
| Config | python-dotenv | Variables de entorno |
