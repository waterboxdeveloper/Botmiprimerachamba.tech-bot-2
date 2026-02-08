# FASE 1.2: Crear .env.example

## Objetivo
Template de variables de entorno. El archivo `.env` real (con valores) NO se commitea, pero `.env.example` SÍ (para que otros sepan qué variables necesitan).

## Qué hacer
Crear `/bot2mvp/.env.example` con las variables necesarias (sin valores reales).

## Variables necesarias

```env
# Telegram Bot
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Gemini AI
GEMINI_API_KEY=your_gemini_api_key

# JobSpy API
JOBSPY_API_URL=http://localhost:8000
# O si usas el API remoto:
# JOBSPY_API_URL=https://your-jobspy-instance.com

# Google Sheets (opcional para MVP, lo vamos a usar para logging/backups)
GOOGLE_SHEETS_ID=your_sheet_id_here

# Scheduler
NOTIFICATION_TIMEZONE=America/Bogota
NOTIFICATION_HOUR_1=09:00
NOTIFICATION_HOUR_2=17:00

# Database
SQLITE_DB_PATH=./usuarios.db

# Logging
LOG_LEVEL=INFO
```

## Tareas
- [ ] Crear `.env.example`
- [ ] Agregar todas las variables listadas
- [ ] Agregar comments explicativos
- [ ] Crear `.env` local (copiando `.env.example`) para desarrollo
- [ ] Verificar que `.env` NO está en `.gitignore` (espera, SÍ debe estar)

## Verificación
```bash
# .env.example debe existir
ls -la .env.example

# .env debe ser local (no commitear)
grep ".env" .gitignore
# Debe mostrar: .env
```

## Notas
- `.env.example` se commitea, `.env` NO
- Usuarios nuevos copian `.env.example` → `.env` y agregan sus valores
- Para Bot Father token: Busca `BotFather` en Telegram, copia el token
