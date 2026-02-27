# FASE 9: Dockerización - Bot2MVP

**Fecha**: 2026-02-15
**Estado**: ✅ IMPLEMENTADA
**Prioridad**: ALTA (Requerido para producción)

---

## 🎯 Objetivo

Containerizar el bot de Telegram y sus dependencias (JobSpy API) usando Docker y Docker Compose para:
- ✅ Portabilidad: ejecutar en cualquier máquina
- ✅ Reproducibilidad: mismo comportamiento en dev y producción
- ✅ Escalabilidad: desplegar múltiples instancias
- ✅ Aislamiento: servicios independientes con redes compartidas
- ✅ Facilidad de deployment: `docker-compose up` y listo

---

## 📋 Archivos Creados / Modificados

### 1. **Dockerfile** (NUEVO)
Dockerfile multi-stage para el bot de Telegram.

**Características:**
- ✅ Base: `python:3.11-slim` (ligero, ~150MB)
- ✅ Multi-stage: builder + runtime (reduce tamaño final)
- ✅ Usuario no-root: `bot` (seguridad)
- ✅ `uv` package manager (rápido, determinístico)
- ✅ Health check incluido
- ✅ PYTHONUNBUFFERED=1 (logs en tiempo real)
- ✅ Logs persistentes en volumen

**Ubicación**: `/Dockerfile`

**Flujo:**
```dockerfile
Stage 1 (Builder):
  - FROM python:3.11-slim
  - Install uv
  - Copy pyproject.toml + uv.lock
  - uv sync --no-dev
  - Result: .venv precompilado

Stage 2 (Runtime):
  - FROM python:3.11-slim
  - Install curl (healthcheck)
  - Create user 'bot'
  - Copy .venv from builder
  - Copy source code
  - Run: uv run python bot/main.py
```

**Tamaño esperado**: ~400-500MB (con todas las dependencias)

---

### 2. **docker-compose.yml** (NUEVO)
Orquestación de dos servicios: telegram-bot + jobspy-api.

**Servicios:**

#### a) `telegram-bot`
```yaml
build:
  context: .
  dockerfile: Dockerfile
container_name: bot2mvp-telegram-bot
restart: unless-stopped
env_file: .env
environment:
  JOBSPY_API_URL: http://jobspy-api:8000  # Service discovery (DNS interno)
depends_on:
  jobspy-api:
    condition: service_healthy  # Wait for API to be healthy
volumes:
  - ./logs:/app/logs  # Persist logs
networks:
  - app-network
resources:
  limits: {cpus: "1", memory: 512M}
```

#### b) `jobspy-api`
```yaml
build:
  context: ./jobspy-api
  dockerfile: Dockerfile
container_name: bot2mvp-jobspy-api
ports:
  - "127.0.0.1:8000:8000"  # Only localhost (seguridad)
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 10s
networks:
  - app-network
resources:
  limits: {cpus: "2", memory: 1G}
```

**Red compartida:**
```yaml
networks:
  app-network:
    driver: bridge
    subnet: 172.20.0.0/16  # Explicit range para DNS reliability
```

**Volúmenes:**
```yaml
volumes:
  jobspy-logs:
    driver: local  # Logs de JobSpy API
```

**Ubicación**: `/docker-compose.yml`

---

### 3. **.env.example** (ACTUALIZADO)
Añadidas credenciales Supabase y reorganizadas secciones.

**Cambios:**
- ✅ Agregado: `SUPABASE_URL`, `SUPABASE_KEY`, `SUPABASE_SERVICE_ROLE`
- ✅ Agregado: `ADMIN_CHAT_ID` (para rate limiting bypass)
- ✅ Reorganizado en secciones claras
- ✅ Comentario útil: "Docker: http://jobspy-api:8000 (automatic service discovery)"

**Ubicación**: `/.env.example`

---

## 🚀 Quick Start

### Prerequisitos
```bash
# Verificar Docker instalado
docker --version
docker-compose --version

# Ir a directorio del proyecto
cd bot2mvp
```

### Configuración Inicial
```bash
# 1. Copiar .env.example a .env
cp .env.example .env

# 2. Rellenar credenciales (NO commitear)
nano .env
# TELEGRAM_BOT_TOKEN=tu_token_real
# GEMINI_API_KEY=tu_api_key_real
# SUPABASE_URL=https://tu-proyecto.supabase.co
# SUPABASE_KEY=sb_publishable_xxx
# SUPABASE_SERVICE_ROLE=sb_secret_xxx
# ADMIN_CHAT_ID=tu_telegram_id
```

### Build & Run
```bash
# Build images (primera vez, ~2-3 min)
docker-compose build

# Levantar servicios en background
docker-compose up -d

# Ver logs en tiempo real
docker-compose logs -f telegram-bot

# Detener servicios
docker-compose down
```

### Verificar Status
```bash
# Ver contenedores corriendo
docker-compose ps

# Ver health status
docker ps --format "table {{.Names}}\t{{.Status}}"

# Conectarse a contenedor para debug
docker-compose exec telegram-bot /bin/bash

# Ver logs del jobspy-api
docker-compose logs jobspy-api -f
```

---

## 🔧 Arquitectura Técnica

### Diagrama de Componentes
```
┌─────────────────────────────────────────────────────────┐
│         Docker Compose Network (172.20.0.0/16)         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────────────┐     ┌──────────────────────┐ │
│  │  telegram-bot        │     │  jobspy-api          │ │
│  ├──────────────────────┤     ├──────────────────────┤ │
│  │ Python 3.11          │     │ Python 3.13          │ │
│  │ Dependencies: 22     │     │ FastAPI + JobSpy     │ │
│  │ Port: (internal)     │     │ Port: 8000           │ │
│  │ Health: ✅           │     │ Health: ✅ /health   │ │
│  │ Logs: /app/logs      │     │ Logs: /app/logs      │ │
│  │                      │     │ Exposed: 127.0.0.1  │ │
│  │ Depends on:          │     │ (localhost only)     │ │
│  │  - jobspy-api:ready  │     │                      │ │
│  │                      │     │                      │ │
│  │ Env: .env           │     │ Env: .env            │ │
│  │ Mount: ./logs:/logs  │     │ Mount: ./logs:/logs  │ │
│  └──────────────────────┘     └──────────────────────┘ │
│         ↓                             ↓                 │
│    curl to Supabase         curl to JobSpy via        │
│    (Internet)               172.20.0.2:8000            │
│                                                        │
└─────────────────────────────────────────────────────────┘
         ↓ (external)
    🌍 Telegram API
    🌍 Supabase API (PostgreSQL)
    🌍 Gemini API
    🌍 Indeed, LinkedIn, Glassdoor
```

### Flujo de Comunicación
```
User /vacantes
  ↓
Telegram API → telegram-bot container
  ↓
JobSpy Handler
  ↓
HTTP request: http://jobspy-api:8000/api/v1/search_jobs
  (Docker DNS resuelve automáticamente a 172.20.0.2 aproximadamente)
  ↓
jobspy-api container → Indeed/LinkedIn/Glassdoor
  ↓
Results → telegram-bot
  ↓
Gemini API (TOP 5 personalization)
  ↓
Supabase (guardar jobs + rate logs)
  ↓
Telegram API → User
```

### Isolation & Security
```
localhost:8000
  ↓ (port binding, conexión desde host)
  ↓ [FIREWALL]
  ↓
jobspy-api container (127.0.0.1:8000)
  ↓ (NOT accessible from internet)

telegram-bot container
  ↓
  ├─→ Internet (Telegram API, Gemini API, Supabase)
  └─→ jobspy-api:8000 (internal Docker network)
```

---

## ⚙️ Configuración Avanzada

### Variables de Entorno

#### Bot Service (telegram-bot)
```env
# Requerido
TELEGRAM_BOT_TOKEN=xxx
GEMINI_API_KEY=xxx
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=xxx
SUPABASE_SERVICE_ROLE=xxx

# Opcional pero recomendado
ADMIN_CHAT_ID=xxx  # Tu Telegram ID (rate limit bypass)
LOG_LEVEL=INFO     # DEBUG, INFO, WARNING, ERROR

# Automático en Docker
JOBSPY_API_URL=http://jobspy-api:8000
```

#### API Service (jobspy-api)
```env
LOG_LEVEL=DEBUG
ENVIRONMENT=production
ENABLE_CACHE=false
RATE_LIMIT_ENABLED=false  # Rate limiting en el bot, no en API
```

### Resource Limits

**telegram-bot:**
- CPU: 1 core (limit) / 0.5 core (reservation)
- Memory: 512MB (limit) / 256MB (reservation)
- Justificación: I/O-bound (espera API calls)

**jobspy-api:**
- CPU: 2 cores (limit) / 1 core (reservation)
- Memory: 1GB (limit) / 512MB (reservation)
- Justificación: CPU-bound (web scraping)

Ajustar según tu máquina:
```yaml
# Para máquina débil (2GB RAM total)
telegram-bot: {limits: {memory: 256M}, reservations: {memory: 128M}}
jobspy-api: {limits: {memory: 512M}, reservations: {memory: 256M}}

# Para máquina potente (8GB+ RAM)
telegram-bot: {limits: {memory: 1G}, reservations: {memory: 512M}}
jobspy-api: {limits: {memory: 2G}, reservations: {memory: 1G}}
```

### Logging

**Configuración:**
```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"    # Rotar cada 10MB
    max-file: "3"      # Guardar máx 3 archivos rotados
```

**Ubicaciones:**
- Bot logs: `/logs/bot.log`
- API logs: `/logs/jobspy-api.log`
- Docker logs: `docker-compose logs [service]`

**Limpiar logs:**
```bash
# Ver tamaño de logs
docker system df

# Limpiar logs viejos
docker system prune -a --volumes
```

---

## 🧪 Testing y Validación

### 1. Verificar Build
```bash
# Build images
docker-compose build

# Verificar imágenes creadas
docker images | grep bot2mvp
```

### 2. Verificar Servicios
```bash
# Levantar en foreground (Ctrl+C para detener)
docker-compose up

# Logs del bot
# (en otra terminal)
docker-compose logs telegram-bot -f

# Logs del API
docker-compose logs jobspy-api -f
```

### 3. Verificar Conectividad
```bash
# Conectarse al bot container
docker-compose exec telegram-bot /bin/bash

# Dentro del container:
# Verificar que puede conectar a jobspy-api
curl -v http://jobspy-api:8000/health

# Verificar que puede conectar a internet
curl -I https://api.telegram.org/

# Verificar que variables de entorno están seteadas
env | grep -E "TELEGRAM|JOBSPY|SUPABASE"
```

### 4. Verificar Health Checks
```bash
# Esperar a que ambos servicios sean healthy
docker-compose ps

# Salida esperada:
# NAME                          STATUS
# bot2mvp-telegram-bot          Up (healthy)
# bot2mvp-jobspy-api            Up (healthy)
```

### 5. Testing End-to-End
```bash
# Enviar comando /start al bot
# (Abrir Telegram, enviar /start)

# Verificar logs
docker-compose logs telegram-bot | tail -20

# Esperar "Bot started successfully"
```

---

## 🐛 Troubleshooting

### Error: "Cannot connect to Docker daemon"
```bash
# Verificar que Docker está corriendo
sudo systemctl status docker

# Iniciar Docker
sudo systemctl start docker

# En macOS
open --application Docker
```

### Error: "service_healthy never becomes true"
```bash
# Verificar health check del jobspy-api
docker-compose up jobspy-api

# Ver error en logs
docker-compose logs jobspy-api | grep -A 5 -B 5 health

# Soluciones comunes:
# 1. Puerto 8000 ya en uso
sudo lsof -i :8000

# 2. Imagen no compiló correctamente
docker-compose build --no-cache jobspy-api
```

### Error: "Cannot find .env file"
```bash
# Asegurarse de estar en directorio correcto
pwd
# Debe ser: /path/to/bot2mvp

# Crear .env si no existe
cp .env.example .env
```

### Error: "JOBSPY_API_URL not resolved"
```bash
# Verificar que docker-compose está usando la red correcta
docker network ls | grep app-network

# Si no existe, recrear:
docker-compose down -v
docker-compose build
docker-compose up -d
```

### Logs del bot no se actualizan
```bash
# Verificar que volumen está montado
docker inspect bot2mvp-telegram-bot | grep Mounts

# Ver logs directamente en contenedor
docker-compose exec telegram-bot tail -f /app/logs/bot.log
```

---

## 🔐 Seguridad

### Principios Implementados

1. **Secretos NO en imagen:**
   - ✅ `.env` en `.gitignore`
   - ✅ `.env` en `.dockerignore`
   - ✅ Cargados en runtime desde archivo `.env`

2. **Usuario no-root:**
   - ✅ Bot corre como usuario `bot` (no root)
   - ✅ Previene escalación de privilegios

3. **Red aislada:**
   - ✅ jobspy-api NO expuesto a internet (127.0.0.1:8000)
   - ✅ Solo accesible desde localhost o otros containers en red

4. **Health checks:**
   - ✅ Verifica que servicios están vivos
   - ✅ `depends_on: condition: service_healthy` para startup ordering

5. **Logs rotados:**
   - ✅ Max 10MB por archivo
   - ✅ Máx 3 archivos guardados
   - ✅ Previene llenar disco

### Mejoras de Seguridad (Producción)

Para llevar a producción, agregar:

```yaml
# docker-compose.yml
telegram-bot:
  # Usuario no-root (ya implementado)
  # Filesystem read-only (opcional)
  read_only: true
  tmpfs:
    - /tmp
    - /run
    - /app/logs  # Escribir logs

  # Capabilities mínimas
  cap_drop:
    - ALL
  cap_add:
    - NET_BIND_SERVICE  # Solo si es necesario

  # No permitir privilegios escalonados
  security_opt:
    - no-new-privileges:true
```

---

## 📈 Monitoreo y Logs

### Comandos Útiles

```bash
# Ver status de todos los servicios
docker-compose ps

# Ver logs en tiempo real
docker-compose logs -f

# Ver logs de un servicio específico
docker-compose logs -f telegram-bot
docker-compose logs -f jobspy-api

# Ver últimas N líneas
docker-compose logs --tail=50 telegram-bot

# Ver logs desde cierta fecha
docker-compose logs --since 1m telegram-bot

# Ver tamaño de logs
du -sh logs/

# Limpiar logs viejos
docker system prune

# Ver usar de recursos en tiempo real
docker stats

# Ver eventos en tiempo real
docker-compose logs --follow --timestamps

# Exportar logs
docker-compose logs > debug.log 2>&1
```

### Monitoreo Recomendado

1. **Telegram API**: Verificar que bot recibe mensajes
2. **Jobspy API**: Verificar que `/health` responde
3. **Supabase**: Dashboard en supabase.com
4. **Gemini API**: Dashboard en console.cloud.google.com
5. **Disk space**: `df -h` (logs pueden crecer)

---

## 📦 Deployment

### Deploy a Producción

1. **Preparar servidor:**
   ```bash
   # SSH al servidor
   ssh user@production-server

   # Instalar Docker
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh

   # Instalar Docker Compose
   sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   ```

2. **Clonar repositorio:**
   ```bash
   git clone https://github.com/tu-repo/bot2mvp.git
   cd bot2mvp
   ```

3. **Configurar .env:**
   ```bash
   nano .env
   # (rellenar con credenciales reales)
   ```

4. **Levantar servicios:**
   ```bash
   docker-compose up -d

   # Verificar
   docker-compose ps
   ```

5. **Configurar auto-restart (systemd):**
   ```bash
   # Crear archivo systemd
   sudo nano /etc/systemd/system/bot2mvp.service

   [Unit]
   Description=Bot2MVP Telegram Bot
   After=docker.service
   Requires=docker.service

   [Service]
   Type=simple
   WorkingDirectory=/home/user/bot2mvp
   ExecStart=/usr/bin/docker-compose up
   ExecStop=/usr/bin/docker-compose down
   Restart=always

   [Install]
   WantedBy=multi-user.target

   # Habilitar
   sudo systemctl enable bot2mvp
   sudo systemctl start bot2mvp
   ```

### Deploy Alternativo: Cloud Services

**AWS ECS:**
```bash
# Push image a ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789.dkr.ecr.us-east-1.amazonaws.com
docker tag bot2mvp:latest 123456789.dkr.ecr.us-east-1.amazonaws.com/bot2mvp:latest
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/bot2mvp:latest
```

**Google Cloud Run:**
```bash
gcloud run deploy bot2mvp \
  --image gcr.io/PROJECT_ID/bot2mvp:latest \
  --platform managed \
  --region us-central1 \
  --set-env-vars TELEGRAM_BOT_TOKEN=xxx,GEMINI_API_KEY=xxx
```

---

## 🎯 Checklist de Implementación

- [x] Crear Dockerfile para telegram-bot
- [x] Crear docker-compose.yml con ambos servicios
- [x] Actualizar .env.example
- [x] Agregar Supabase credentials a .env.example
- [x] Verificar .dockerignore completo
- [x] Testing build local
- [x] Testing run local
- [x] Documentación completa
- [ ] Deploy a servidor test
- [ ] Deploy a producción
- [ ] Monitoreo en producción

---

## 🔗 Referencias

- **Docker Docs**: https://docs.docker.com/
- **Docker Compose**: https://docs.docker.com/compose/
- **Best Practices**: https://docs.docker.com/develop/develop-images/dockerfile_best-practices/
- **Security**: https://docs.docker.com/engine/security/

---

**Estado**: ✅ FASE 9 COMPLETADA - Docker setup listo para testing

**Próximos Pasos**:
1. Testing end-to-end en local
2. Deploy a servidor test
3. Monitoreo en producción
4. Auto-scaling (si es necesario)
