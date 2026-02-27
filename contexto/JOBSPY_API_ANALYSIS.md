# JobSpy API - Análisis Completo

## 📋 Información General

**Repositorio**: https://github.com/rainmanjam/jobspy-api
**Tipo**: FastAPI (Python)
**Deployment**: Docker
**Autenticación**: API Key (`x-api-key`)
**Output**: JSON o CSV
**Estado**: Production-ready

---

## 🚀 Instalación y Ejecución

### Opción 1: Docker Build Manual
```bash
docker build -t jobspy-api .
docker run -p 8000:8000 \
  -e API_KEYS=tu-api-key-aqui \
  -e ENABLE_API_KEY_AUTH=true \
  jobspy-api
```

### Opción 2: Docker Compose (Recomendado)
```bash
docker-compose up -d
```

### Opción 3: Desarrollo (con recarga automática)
```bash
docker-compose -f docker-compose.dev.yml up
```

**Importante**: La API estará disponible en `http://localhost:8000`

---

## 🔐 Autenticación

### Encabezado Requerido
```
x-api-key: tu-api-key-aqui
```

### Variables de Entorno
| Variable | Descripción | Default |
|----------|-------------|---------|
| `API_KEYS` | Claves válidas (separadas por comas) | requerido |
| `ENABLE_API_KEY_AUTH` | Activar autenticación | true |
| `API_KEY_HEADER_NAME` | Nombre del header | x-api-key |

**Ejemplo con curl:**
```bash
curl -H "x-api-key: tu-api-key" http://localhost:8000/api/v1/search_jobs?search_term=ux+designer
```

---

## ⏱️ Rate Limiting

### Configuración
| Variable | Descripción | Default |
|----------|-------------|---------|
| `RATE_LIMIT_ENABLED` | Activar rate limiting | true |
| `RATE_LIMIT_REQUESTS` | Máx solicitudes | 100 |
| `RATE_LIMIT_TIMEFRAME` | Ventana (segundos) | 3600 |

**Comportamiento:**
- Máximo 100 solicitudes por hora
- Respuesta 429 si se excede límite
- Anti-ban mediante proxies y User-Agent rotation

---

## 📡 Endpoints Disponibles

### 1. Health Check (Monitoreo)
```
GET /health
```
**Propósito**: Verificar si la API está activa
**Respuesta**: `{"status": "ok"}`
**Autenticación**: No requerida

### 2. Ping (Diagnóstico)
```
GET /ping
```
**Propósito**: Prueba rápida de conectividad
**Respuesta**: `{"message": "pong"}`
**Autenticación**: No requerida

### 3. Search Jobs (Principal)
```
GET /api/v1/search_jobs
```
**Propósito**: Buscar empleos con filtros
**Autenticación**: ✅ REQUERIDA (x-api-key)

---

## 🔍 Parámetros de Búsqueda

### Parámetros Principales

| Parámetro | Tipo | Requerido | Default | Descripción |
|-----------|------|-----------|---------|-------------|
| `search_term` | string | ✅ SÍ | - | Término a buscar (ej: "ux designer", "python developer") |
| `site_name` | string/array | No | Todas | Plataformas: linkedin, indeed, glassdoor, google, ziprecruiter, bayt, naukri |
| `location` | string | No | - | Ubicación (ej: "San Francisco, CA", "Remote") |
| `distance` | integer | No | 50 | Distancia en millas desde la ubicación |
| `is_remote` | boolean | No | - | true = solo empleos remotos |
| `job_type` | string | No | - | fulltime, parttime, internship, contract |
| `easy_apply` | boolean | No | - | true = solo con aplicación fácil |
| `results_wanted` | integer | No | 20 | Cuántos resultados por plataforma (máx ~50) |
| `format` | string | No | json | json o csv |
| `hours_old` | integer | No | - | Filtrar por horas desde publicación |
| `description_format` | string | No | markdown | markdown o html |
| `enforce_annual_salary` | boolean | No | false | Convertir todos los salarios a anuales |
| `linkedin_fetch_description` | boolean | No | true | Obtener descripción completa en LinkedIn |
| `country_indeed` | string | ⚠️ Condicional | - | **REQUERIDO para Indeed/Glassdoor**. Usa nombre completo: "USA" (no "US"), "Colombia" (no "CO"), "Canada" (no "CA"), etc. Ver lista de países válidos abajo. |

---

## 🌍 Países Válidos para `country_indeed`

**IMPORTANTE**: Usa el nombre COMPLETO del país, NO códigos ISO (US → USA, CO → Colombia, etc)

```
Argentina, Australia, Austria, Bahrain, Belgium, Brazil, Canada, Chile, China,
Colombia, Costa Rica, Czech Republic, Denmark, Ecuador, Egypt, Finland, France,
Germany, Greece, Hong Kong, Hungary, India, Indonesia, Ireland, Israel, Italy,
Japan, Kuwait, Luxembourg, Malaysia, Mexico, Morocco, Netherlands, New Zealand,
Nigeria, Norway, Oman, Pakistan, Panama, Peru, Philippines, Poland, Portugal,
Qatar, Romania, Saudi Arabia, Singapore, South Africa, South Korea, Spain,
Sweden, Switzerland, Taiwan, Thailand, Turkey, UK, USA, Ukraine,
United Arab Emirates, Uruguay, Venezuela, Vietnam
```

---

## 📊 Estructura de Respuesta JSON

### Respuesta Base
```json
{
  "count": 45,
  "jobs": [
    {
      "id": "in-e8da1599c31b66ec",
      "site": "indeed",
      "title": "Senior UX Designer",
      "company": "Acme Corp",
      "job_url": "https://www.indeed.com/viewjob?jk=e8da1599c31b66ec",
      "job_url_direct": "https://acme.com/careers",
      "location": "San Francisco, CA, US",
      "is_remote": true,
      "description": "We are looking for...",
      "job_type": "fulltime",
      "job_level": "senior",
      "salary_source": "indeed",
      "interval": "yearly",
      "min_amount": 80000,
      "max_amount": 120000,
      "currency": "USD",
      "date_posted": "2024-01-15",
      "job_function": "Design",
      "emails": null,
      "company_industry": "Technology"
    }
  ],
  "cached": false
}
```

### Campos Principales

| Campo | Tipo | Siempre presente | Descripción |
|-------|------|-----------------|-------------|
| `id` | string | ✅ | ID único del trabajo (format: site-hash) |
| `site` | string | ✅ | Sitio de origen (indeed, linkedin, glassdoor, etc) |
| `title` | string | ✅ | Título del puesto |
| `company` | string | ✅ | Nombre de la empresa |
| `job_url` | string | ✅ | Link hacia el sitio de origen |
| `job_url_direct` | string | ❌ | Link directo a la empresa (si disponible) |
| `location` | string | ✅ | Ubicación como string (ej: "San Francisco, CA, US") |
| `is_remote` | boolean | ✅ | Si es remoto |
| `description` | string | ❌ | Descripción del puesto |
| `job_type` | string | ❌ | fulltime/parttime/contract/internship (puede ser múltiple) |
| `job_level` | string | ❌ | entry, mid, senior (varía por sitio) |
| `job_function` | string | ❌ | Área funcional (Design, Engineering, etc) |
| `min_amount` | number | ❌ | Salario mínimo |
| `max_amount` | number | ❌ | Salario máximo |
| `currency` | string | ❌ | Moneda (USD, GBP, EUR, etc) |
| `interval` | string | ❌ | Intervalo salarial (yearly, monthly, hourly) |
| `date_posted` | string | ✅ | Fecha de publicación (YYYY-MM-DD) |
| `salary_source` | string | ❌ | De dónde viene la info salarial |
| `emails` | array | ❌ | Correos de contacto |
| `company_industry` | string | ❌ | Industria (Technology, Finance, etc) |

### Campos Específicos por Plataforma

**LinkedIn:**
- `job_level`: entry, mid, senior, executive
- `company_industry`: Industria específica

**Indeed:**
- `company_country`: País de la empresa
- `company_addresses`: Direcciones de oficinas
- `company_employees_label`: Tamaño de la empresa
- `company_description`: Descripción de la empresa
- `company_logo`: URL del logo

**Naukri (India):**
- `skills`: Array de habilidades requeridas
- `experience_range`: Años de experiencia
- `company_rating`: Rating de la empresa
- `vacancy_count`: Vacantes abiertas

---

## 💾 Caché

| Variable | Default | Descripción |
|----------|---------|-------------|
| `ENABLE_CACHE` | true | Activar almacenamiento en caché |
| `CACHE_EXPIRY` | 3600 | Segundos hasta expiración (1 hora) |

**Ventaja**: Respuestas más rápidas para búsquedas repetidas

---

## 🌐 Plataformas Soportadas

| Sitio | Disponible | Notas |
|-------|-----------|-------|
| LinkedIn | ✅ | Requiere descripción completa |
| Indeed | ✅ | 50+ países soportados |
| Glassdoor | ✅ | 50+ países soportados |
| Google Jobs | ✅ | Requiere términos específicos |
| ZipRecruiter | ✅ | USA principalmente |
| Bayt | ✅ | Oriente Medio |
| Naukri | ✅ | India |

---

## 📝 Ejemplos de Búsqueda

### Ejemplo 1: Búsqueda Simple
```bash
curl -X GET 'http://localhost:8000/api/v1/search_jobs?search_term=ux+designer' \
  -H 'x-api-key: tu-api-key'
```

### Ejemplo 2: Con Filtros
```bash
curl -X GET 'http://localhost:8000/api/v1/search_jobs?search_term=python+developer&location=Remote&is_remote=true&job_type=contract&results_wanted=50' \
  -H 'x-api-key: tu-api-key'
```

### Ejemplo 3: Múltiples Plataformas
```bash
curl -X GET 'http://localhost:8000/api/v1/search_jobs?search_term=designer&site_name=linkedin&site_name=indeed&site_name=glassdoor' \
  -H 'x-api-key: tu-api-key'
```

### Ejemplo 4: Exportar a CSV
```bash
curl -X GET 'http://localhost:8000/api/v1/search_jobs?search_term=engineer&format=csv' \
  -H 'x-api-key: tu-api-key' \
  -H 'accept: text/csv' \
  -o jobs.csv
```

### Ejemplo 5: Filtro por Horas
```bash
curl -X GET 'http://localhost:8000/api/v1/search_jobs?search_term=designer&hours_old=24' \
  -H 'x-api-key: tu-api-key'
```
(Solo empleos publicados en las últimas 24 horas)

---

## ⚠️ Limitaciones y Consideraciones

### Rate Limiting
- **100 solicitudes/hora** por defecto
- Esperar 36 segundos entre solicitudes para no exceder límite
- Error 429 si se supera

### Performance
- Buscar en todas las plataformas tarda más
- LinkedIn puede tardar 5-15 segundos (busca descripción completa)
- Indeed/Glassdoor más rápido (2-5 segundos)
- Google Jobs puede ser lento (~10 segundos)

### Proxy Support
- API soporta proxies para evitar bloqueos
- Configurar en `DEFAULT_PROXIES` (variable de entorno)
- User-Agent rotation automático

### Google Jobs
- Requiere términos de búsqueda muy específicos
- Puede no devolver resultados para términos genéricos

---

## 🛠️ Variables de Entorno Disponibles

```bash
# Autenticación
API_KEYS=key1,key2,key3
ENABLE_API_KEY_AUTH=true
API_KEY_HEADER_NAME=x-api-key

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_TIMEFRAME=3600

# Plataformas Predeterminadas
DEFAULT_SITE_NAMES=linkedin,indeed,glassdoor

# Búsqueda
DEFAULT_RESULTS_WANTED=20
DEFAULT_DISTANCE=50

# Proxies
DEFAULT_PROXIES=http://proxy1.com:8080,http://proxy2.com:8080

# Caché
ENABLE_CACHE=true
CACHE_EXPIRY=3600

# Certificados
CA_CERT_PATH=/path/to/cert.pem

# Logging
LOG_LEVEL=INFO

# CORS
CORS_ORIGINS=*

# Documentación
ENABLE_SWAGGER_UI=true
ENABLE_REDOC=true
```

---

## 📚 Documentación Interactiva

Una vez ejecutado el Docker:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Ambas muestran endpoints, parámetros y permiten hacer pruebas interactivas.

---

## 🔄 Flujo de Integración con el Bot (ON-DEMAND)

```
1. Usuario en Telegram: /perfil [keywords]
   ↓
2. Guardar keywords en Google Sheets
   ↓
3. Usuario en Telegram: /vacantes
   ↓
4. Bot lee keywords de Sheets (ese usuario)
   ↓
5. Bot construye search_term desde keywords
   ↓
6. Bot llama a JobSpy API: /api/v1/search_jobs
   ↓
7. JobSpy devuelve JSON (2-5 segundos)
   ↓
8. Bot personaliza con Gemini (1-2 segundos)
   ↓
9. Bot envía resultados al usuario via Telegram (en tiempo real)
```

---

## ✅ Preguntas Clave para Pruebas

1. ¿Cuánto tarda una búsqueda simple en Indeed vs LinkedIn?
2. ¿Cuántos resultados devuelve por plataforma?
3. ¿Qué información falta más frecuentemente (salario, emails, etc)?
4. ¿El rate limiting permite 100 búsquedas/hora sin problemas?
5. ¿Los filtros (`is_remote`, `job_type`) funcionan correctamente?
6. ¿La caché realmente acelera búsquedas repetidas?

---

## 🎯 INSIGHTS DEL REPOSITORIO OFICIAL (2026-02-16)

Tras leer README.md, FAQ.md, PERFORMANCE_TUNING.md y DEPLOYMENT.md del repo, encontramos:

### 1. **CACHING NATIVO (1 hora por defecto)**
- `ENABLE_CACHE=true` (default)
- `CACHE_EXPIRY=3600` segundos
- **Ventaja**: Si un usuario busca lo mismo 2 veces < 1 hora: respuesta instantánea
- **Para el bot**: No necesitamos cache adicional, ya está integrado
- **Implicación**: Resultados duplicados para el mismo usuario pueden venir en caché

### 2. **RATE LIMITING (100 req/hora por defecto)**
- `RATE_LIMIT_ENABLED=true`
- `RATE_LIMIT_REQUESTS=100` por `RATE_LIMIT_TIMEFRAME=3600s`
- **Comportamiento**: Error `429 Too Many Requests` si se excede
- **Para el bot**: Nuestro sleep de 2-3s entre búsquedas (~720-1080 req/hora max) está DENTRO del límite ✅
- **Recomendación**: No hacer ráfagas de búsquedas rápidas

### 3. **MÁS PLATAFORMAS DISPONIBLES (No solo 3)**
Además de Indeed, LinkedIn, Glassdoor:
- `zip_recruiter` - USA principalmente
- `google` - Requiere términos específicos
- `bayt` - Oriente Medio (Middle East jobs)
- `naukri` - India

**Para el bot**: De momento solo Indeed/LinkedIn/Glassdoor, pero podemos expandir en futuro

### 4. **LIMITACIONES DE PARÁMETROS (NO se pueden combinar)**

**Indeed**:
```
❌ NO puedes usar juntos:
  • hours_old + job_type + is_remote
  • hours_old + easy_apply
  • job_type + is_remote + easy_apply
```

**LinkedIn**:
```
❌ NO puedes usar juntos:
  • hours_old + easy_apply
```

**Para FASE 6** (handler /vacantes): Usar UN filtro a la vez, no combinar

### 5. **PAÍSES SOPORTADOS SON 60+, NO SOLO 12**
```
Argentina, Australia, Austria, Bahrain, Belgium, Brazil, Canada, Chile, China,
Colombia, Costa Rica, Czech Republic, Denmark, Ecuador, Egypt, Finland, France,
Germany, Greece, Hong Kong, Hungary, India, Indonesia, Ireland, Israel, Italy,
Japan, Kuwait, Luxembourg, Malaysia, Mexico, Morocco, Netherlands, New Zealand,
Nigeria, Norway, Oman, Pakistan, Panama, Peru, Philippines, Poland, Portugal,
Qatar, Romania, Saudi Arabia, Singapore, South Africa, South Korea, Spain,
Sweden, Switzerland, Taiwan, Thailand, Turkey, UK, USA, Ukraine,
United Arab Emirates, Uruguay, Venezuela, Vietnam
```

**Para el bot**: Expandir VALID_COUNTRIES en jobspy_client.py cuando escalemos a más mercados

### 6. **FEATURES ADICIONALES DISPONIBLES**

#### Paginación:
```bash
?paginate=true&page=1&page_size=20
```
**Uso**: Para resultados grandes, mostrar en páginas

#### Export CSV:
```bash
?format=csv
```
**Uso**: Permitir que usuario exporte resultados

#### LinkedIn Full Descriptions:
```bash
?linkedin_fetch_description=true
```
**Costo**: Más lento (5-15s vs 0.6-1s)
**Para el bot**: NO activar por defecto

#### Enforce Annual Salary:
```bash
?enforce_annual_salary=true
```
**Uso**: Normalizar todos los salarios a anuales

### 7. **ERROR HANDLING ROBUSTO**
- API devuelve errores descriptivos CON SUGERENCIAS
- Parámetros inválidos → recomienda valores válidos
- Combinaciones inválidas → explica por qué

**Para el bot**: Podemos parsear estos errores y mostrar mensajes amigables al usuario

### 8. **OPCIONES DE DESCRIPCIÓN**
- `description_format=markdown` (default) ✅
- `description_format=html`

**Para el bot**: Las descripciones vienen en markdown, PERFECTO para Telegram

### 9. **MONITORING Y HEALTH CHECKS**
```bash
GET /health        # {status: "ok"}
GET /ping          # {message: "pong"}
```
**Para el bot**: Podemos verificar API health antes de buscar

---

## 📊 RESUMEN DE RECOMENDACIONES

| Item | Recomendación | Estado |
|------|---------------|--------|
| **Caching** | Usar nativo (ya está) | ✅ En uso |
| **Rate Limit** | 2-3s entre búsquedas | ✅ En uso |
| **Plataformas** | Indeed/LinkedIn/Glassdoor por ahora | ✅ En uso |
| **Parámetros** | Validar combos en FASE 6 | ⏳ Próximo |
| **Países** | Expandir lista VALID_COUNTRIES | ⏳ Futuro |
| **Descripciones** | Mantener markdown | ✅ En uso |
| **LinkedIn full desc** | NO activar por defecto | ✅ En uso |
| **Paginación** | Usar si resultados > 50 | ⏳ Futuro |
| **Export CSV** | Agregar como feature extra | ⏳ Futuro |
| **Health checks** | Verificar antes de buscar | ⏳ FASE 6 |

---

**Actualizado**: 2026-02-16
**Base**: Análisis oficial de rainmanjam/jobspy-api (README.md, FAQ.md, PERFORMANCE_TUNING.md, DEPLOYMENT.md)
**Estado**: Listo para FASE 6 (/vacantes handler)
