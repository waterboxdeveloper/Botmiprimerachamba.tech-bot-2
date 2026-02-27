# 🐳 Docker Setup para Bot2MVP

Guía rápida para correr el bot con Docker.

## 📋 Prerequisitos

- Docker: https://docs.docker.com/get-docker/
- Docker Compose: `docker --version` && `docker-compose --version`

## 🚀 Quick Start (3 pasos)

### 1. Configurar credenciales
```bash
cp .env.example .env
# Editar .env con tus credenciales reales:
# - TELEGRAM_BOT_TOKEN
# - GEMINI_API_KEY
# - SUPABASE_URL, SUPABASE_KEY, SUPABASE_SERVICE_ROLE
# - ADMIN_CHAT_ID
nano .env
```

### 2. Build y Start
```bash
# Opción A: Manual
docker-compose build
docker-compose up -d

# Opción B: Con helper script (recomendado)
./scripts/docker-helper.sh build
./scripts/docker-helper.sh up
```

### 3. Verificar
```bash
# Ver status
docker-compose ps

# Ver logs
docker-compose logs -f telegram-bot

# Esperar hasta ver: "✅ Bot initialized successfully"
```

## 📖 Comandos Comunes

```bash
# Ver help
./scripts/docker-helper.sh help

# Build
./scripts/docker-helper.sh build

# Start (background)
./scripts/docker-helper.sh up

# Start (foreground - ver logs en vivo)
./scripts/docker-helper.sh up-fg

# Stop
./scripts/docker-helper.sh down

# Ver logs
./scripts/docker-helper.sh logs telegram-bot
./scripts/docker-helper.sh logs jobspy-api

# Conectarse a shell en bot
./scripts/docker-helper.sh shell-bot

# Conectarse a shell en API
./scripts/docker-helper.sh shell-api

# Test health
./scripts/docker-helper.sh health

# Desarrollo (con volume mounts)
./scripts/docker-helper.sh dev

# Limpiar todo
./scripts/docker-helper.sh clean
```

## 🔧 Manual (sin helper script)

```bash
# Build
docker-compose build

# Start en background
docker-compose up -d

# Ver status
docker-compose ps

# Ver logs
docker-compose logs -f

# Conectarse a bot shell
docker-compose exec telegram-bot /bin/bash

# Conectarse a API shell
docker-compose exec jobspy-api /bin/bash

# Verificar connectivity
docker-compose exec telegram-bot curl http://jobspy-api:8000/health

# Stop
docker-compose down
```

## 📊 Arquitectura

```
docker-compose.yml
├── telegram-bot (Python 3.11 + bot dependencies)
│   ├── Builds from: Dockerfile
│   ├── Mount: ./logs:/app/logs
│   └── Depends on: jobspy-api:healthy
│
└── jobspy-api (Python 3.13 + FastAPI + JobSpy)
    ├── Builds from: ./jobspy-api/Dockerfile
    ├── Port: 127.0.0.1:8000 (localhost only)
    └── Health: http://localhost:8000/health

Network: 172.20.0.0/16 (Docker bridge network)
```

## 🔐 Seguridad

- ✅ `.env` NO commiteado (en .gitignore)
- ✅ Usuario no-root en containers
- ✅ jobspy-api NO expuesto a internet (127.0.0.1:8000)
- ✅ Logs rotados (10MB max per file)

## 🧪 Testing

```bash
# Test 1: Health check
./scripts/docker-helper.sh health

# Test 2: Ver logs del bot
docker-compose logs telegram-bot | tail -20

# Test 3: Ver logs del API
docker-compose logs jobspy-api | tail -20

# Test 4: Connectivity test
docker-compose exec -T telegram-bot curl -v http://jobspy-api:8000/health

# Test 5: Enviar /start al bot en Telegram
# (Abrir Telegram, enviar /start)
# (Verificar que bot responde)
```

## 🐛 Troubleshooting

### "Cannot connect to Docker daemon"
```bash
# Linux
sudo systemctl start docker

# macOS
open --application Docker
```

### "service jobspy-api 'service_healthy' never became true"
```bash
# Ver error
docker-compose logs jobspy-api

# Rebuild sin cache
docker-compose build --no-cache jobspy-api

# Levantar nuevamente
docker-compose up -d
```

### "Cannot find .env"
```bash
# Copiar desde template
cp .env.example .env
```

### Limpiar logs que crecen mucho
```bash
# Ver tamaño
du -sh logs/

# Limpiar Docker logs
docker system prune -a

# Dentro de container
docker-compose exec telegram-bot rm /app/logs/*.log
```

## 📚 Documentación Completa

Ver: `documentation/PHASE_9_DOCKERIZATION.md`

---

**Última actualización:** 2026-02-15
**Estado:** ✅ Listo para producción
