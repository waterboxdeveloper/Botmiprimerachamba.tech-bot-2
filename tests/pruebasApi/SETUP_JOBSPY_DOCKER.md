# 🐳 Setup JobSpy API Docker - Guía Completa

**Fecha**: 2026-02-15
**Repo**: https://github.com/rainmanjam/jobspy-api
**Status**: En Construcción (Docker building...)

---

## 📋 Paso 1: Clonar el Repositorio

```bash
cd ~/Documents/opino.tech/miprimerachamba.com/bot2mvp
git clone https://github.com/rainmanjam/jobspy-api.git
cd jobspy-api
```

**Resultado**:
```
✅ Repo clonado en ./jobspy-api (dentro del proyecto)
```

**Estructura ahora**:
```
bot2mvp/
├── jobspy-api/                ← AQUÍ
│   ├── docker-compose.yml
│   ├── Dockerfile
│   └── app/
├── bot/
├── backend/
├── tests/
...
```

---

## 📁 Estructura del Repo

```
jobspy-api/
├── .env                      # Configuración (API_KEYS, rate limiting, etc)
├── docker-compose.yml        # Orquestación de Docker
├── Dockerfile               # Imagen Docker (Python 3.13-slim)
├── app/                     # Código principal FastAPI
├── scripts/                 # Scripts de utilidad
├── requirements.txt         # Dependencias Python
├── pyproject.toml          # Config del proyecto
├── README.md               # Documentación oficial
└── tests/                  # Tests del proyecto
```

---

## 🐳 Paso 2: Levantar Docker

```bash
cd ~/jobspy-api
docker-compose up -d
```

**Qué hace**:
1. ✅ Descarga imagen base Python 3.13-slim
2. ✅ Instala dependencias
3. ✅ Construye imagen Docker
4. ✅ Inicia contenedor en puerto 8000

**Tiempo estimado**: 2-5 minutos (primera vez)

---

## ✅ Paso 3: Verificar que esté corriendo

```bash
# Opción A: Health check
curl http://localhost:8000/health

# Opción B: Swagger UI
curl http://localhost:8000/docs

# Opción C: Ver logs
docker-compose logs -f jobspy-api
```

**Respuesta esperada**:
```json
{
  "status": "healthy",
  "version": "...",
  "timestamp": "2026-02-15T..."
}
```

---

## 🔧 Configuración .env

El archivo `.env` controla cómo funciona la API:

```env
# Seguridad
ENABLE_API_KEY_AUTH=false      # Sin key auth para tests
API_KEYS=                       # Vacío (no requerido)

# Rate Limiting
RATE_LIMIT_ENABLED=false       # Desactivado para tests
RATE_LIMIT_REQUESTS=100        # Max 100 req/hora en prod
RATE_LIMIT_TIMEFRAME=3600      # Ventana de 1 hora

# Plataformas por defecto
DEFAULT_SITE_NAMES=indeed,linkedin,zip_recruiter,glassdoor,google,bayt,naukri

# Caché
ENABLE_CACHE=false             # Desactivado para tests
CACHE_EXPIRY=3600              # 1 hora si se activa

# API Documentation
ENABLE_SWAGGER_UI=true         # Swagger en /docs
ENABLE_REDOC=true              # ReDoc en /redoc
```

---

## 📍 Endpoints Principales

### 1. Health Check
```bash
GET http://localhost:8000/health
```

### 2. Swagger UI (Explorar API)
```
http://localhost:8000/docs
```

### 3. Buscar Empleos
```bash
GET http://localhost:8000/api/v1/search_jobs
  ?search_term=python
  &site_name=indeed
  &country_indeed=Colombia
  &is_remote=true
  &job_type=contract
```

---

## 🚀 Próximos Pasos

1. ✅ Docker debe estar corriendo (localhost:8000)
2. ⏳ Re-ejecutar tests:
   - test_rate_limit.py
   - test_multiples.py
   - test_edge_cases.py (nuevo)
3. 📝 Documentar hallazgos en HALLAZGOS_CONSOLIDADOS.md

---

## 🆘 Troubleshooting

### Error: "Connection refused"
```
❌ Significa que Docker NO está corriendo en localhost:8000
✅ Solución: docker-compose up -d
```

### Error: "Pull access denied for jobspy-docker-api"
```
❌ Docker intenta descargar imagen que no existe
✅ Solución: `docker-compose up` compilará la imagen localmente
```

### Error: "Port 8000 already in use"
```
❌ Otro servicio usa puerto 8000
✅ Soluciones:
   - docker-compose down (detener contenedor existente)
   - lsof -i :8000 (ver qué usa el puerto)
   - Cambiar puerto en docker-compose.yml
```

---

## 📊 Estado Actual (2026-02-15 18:49)

- ✅ Repo clonado: ~/jobspy-api
- ⏳ Docker building (en progreso...)
- ⏳ Verificación pending

---

**Última actualización**: 2026-02-15 18:50
**Próximo checkpoint**: Docker corriendo + Tests ejecutados
