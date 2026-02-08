# JobSpy API - rainmanjam/jobspy-api

**Repo**: https://github.com/rainmanjam/jobspy-api

## Cómo Funciona

Es una API FastAPI que busca vacantes. Se corre en Docker (contenedor).

**Parámetros principales**:
- `keywords` - Lo que quiere buscar (ej: "Python developer")
- `location` - Dónde buscar (ej: "USA")
- `job_type` - Tipo de empleo (full-time, part-time, etc)
- `date_posted` - Fechas recientes (last_7days, last_30days, etc)

**Responde con**:
- Lista de vacantes en JSON
- Campos: título, empresa, ubicación, salario, link

## Si Tengo Dudas

Leer: `tests/pruebasApi/HALLAZGOS_CONSOLIDADOS.md`

Ahí está cómo responde realmente la API, qué parámetros funcionan, qué no, y todos los detalles que se descubrieron en las pruebas.
