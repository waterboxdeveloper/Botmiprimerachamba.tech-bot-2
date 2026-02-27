# 📋 PARÁMETROS API JobSpy - Documentación Completa

**Fecha**: 2026-02-15
**Fuente**: Análisis de test_basico.py y test_filtros.py
**Estado**: Validado ✅

---

## 🔗 Endpoint

```
GET http://localhost:8000/api/v1/search_jobs
Headers: x-api-key: test-key-12345
```

---

## 📦 PARÁMETROS EXACTOS

### Parámetro: `search_term` (OBLIGATORIO)
```python
"search_term": "python"  # String, lo que busca el usuario
```

### Parámetro: `site_name` (RECOMENDADO)
```python
"site_name": "indeed"   # Valores: "indeed", "linkedin", "glassdoor"
```

**Comportamiento:**
- Sin especificar: busca en TODAS
- Especificado: busca SOLO en esa plataforma

### Parámetro: `country_indeed` (CONDICIONAL)
```python
"country_indeed": "Colombia"  # Nombre COMPLETO (no código ISO)
```

**Requerimientos:**
- ✅ OBLIGATORIO para: `site_name="indeed"` o `site_name="glassdoor"`
- ❌ NO REQUERIDO para: `site_name="linkedin"` (lo ignora)

**Valores válidos (nombres completos):**
```
USA, UK, Canada, Colombia, Mexico, Brazil, Argentina, Chile,
Germany, France, Italy, Spain, Australia, etc.
```

### Parámetro: `is_remote` (BOOLEANO)
```python
"is_remote": True   # True o False
```

**Comportamiento:**
- Indeed: ✅ Respeta (filtra remote)
- LinkedIn: ⚠️ Ignora (devuelve todos)
- Glassdoor: ⚠️ Ignora (poco confiable)

### Parámetro: `job_type` (STRING)
```python
"job_type": "contract"  # Valores: "fulltime", "contract", "parttime", "internship"
```

**Comportamiento:**
- Indeed: ✅ Respeta (filtra por tipo)
- LinkedIn: ❌ Ignora (siempre devuelve null)
- Glassdoor: ⚠️ Poco confiable

### Parámetro: `results_wanted` (INT)
```python
"results_wanted": 10  # Número de resultados deseados (default: 20)
```

### Parámetro: `hours_old` (INT)
```python
"hours_old": 24  # Solo empleos publicados hace X horas
```

### Parámetro: `format` (STRING)
```python
"format": "json"  # Valores: "json", "csv" (default: "json")
```

---

## ✅ EJEMPLOS DE LLAMADAS REALES

### Ejemplo 1: Usuario de Colombia buscando Python
```python
params = {
    "search_term": "python remote contract",
    "site_name": "indeed",
    "country_indeed": "Colombia",
    "is_remote": True,
    "job_type": "contract",
    "results_wanted": 15
}
```

**Respuesta esperada:** ~5-15 empleos de Colombia

---

### Ejemplo 2: Usuario de USA buscando Designer
```python
params = {
    "search_term": "designer",
    "site_name": "linkedin",
    "is_remote": True,
    "results_wanted": 15
}
# Nota: NO enviar country_indeed a LinkedIn (lo ignora)
```

**Respuesta esperada:** ~8-12 empleos globales

---

### Ejemplo 3: Buscar en TODAS las plataformas
```python
# Primera llamada
params1 = {
    "search_term": "python remote contract",
    "site_name": "indeed",
    "country_indeed": "Colombia",
    "results_wanted": 15
}

# Segunda llamada
params2 = {
    "search_term": "python remote contract",
    "site_name": "linkedin",
    "results_wanted": 15
}

# Tercera llamada
params3 = {
    "search_term": "python remote contract",
    "site_name": "glassdoor",
    "country_indeed": "Colombia",
    "results_wanted": 15
}
```

**Total:** 45 empleos (combinados)

---

## 📊 RESPUESTA (ESTRUCTURA)

```json
{
  "count": 15,
  "jobs": [
    {
      "id": "indeed-xyz123",
      "site": "indeed",
      "title": "Senior Python Developer",
      "company": "Acme Corp",
      "job_url": "https://indeed.com/viewjob?jk=xyz123",
      "location": "Bogotá, Colombia",
      "is_remote": true,
      "date_posted": "2026-02-15",
      "job_type": "contract",
      "description": "We are looking for..."
    }
    // ... más jobs
  ],
  "cached": false
}
```

---

## 🚨 ERRORES COMUNES

### ❌ Error: `country_indeed` con LinkedIn
```python
# MAL:
{"site_name": "linkedin", "country_indeed": "Colombia"}
# Resultado: LinkedIn lo ignora, devuelve empleos globales
```

### ❌ Error: Código ISO en lugar de nombre completo
```python
# MAL:
{"country_indeed": "CO"}  # Código ISO
# BIEN:
{"country_indeed": "Colombia"}  # Nombre completo
```

### ❌ Error: `job_type` con LinkedIn
```python
# MAL expectativa:
{"site_name": "linkedin", "job_type": "contract"}
# Resultado: LinkedIn devuelve null en job_type (ignora filtro)
```

---

## ⚡ TIEMPOS DE RESPUESTA

```
Indeed USA:        1.27s
Indeed Colombia:   1.83s  (50% más lento)
LinkedIn:          0.67s  (más rápido)
Glassdoor:         0.32s  (muy rápido pero poco confiable)

TOTAL (3 búsquedas en paralelo): ~2 segundos
```

---

## 🔐 AUTENTICACIÓN

```python
headers = {"x-api-key": "test-key-12345"}
```

**Nota**: La API key es local (Docker). NO es una API remota.

---

## 📝 RECOMENDACIONES PARA BOT

### Cuando usuario hace `/vacantes`:

```python
def buscar_empleos(user_keywords: str, user_location: str):
    """Busca en TODAS las plataformas"""

    results = {
        "indeed": [],
        "linkedin": [],
        "glassdoor": []
    }

    # Búsqueda 1: Indeed
    params_indeed = {
        "search_term": user_keywords,
        "site_name": "indeed",
        "country_indeed": user_location,  # ✅ Enviar
        "is_remote": True,
        "job_type": "contract",
        "results_wanted": 15
    }
    results["indeed"] = call_jobspy_api(params_indeed)

    # Búsqueda 2: LinkedIn
    params_linkedin = {
        "search_term": user_keywords,
        "site_name": "linkedin",
        # ❌ NO enviar country_indeed
        "is_remote": True,
        "results_wanted": 15
    }
    results["linkedin"] = call_jobspy_api(params_linkedin)

    # Búsqueda 3: Glassdoor
    params_glassdoor = {
        "search_term": user_keywords,
        "site_name": "glassdoor",
        "country_indeed": user_location,  # ✅ Enviar
        "results_wanted": 15
    }
    results["glassdoor"] = call_jobspy_api(params_glassdoor)

    # Gemini analiza TODOS y elige TOP 3-5
    return gemini_filter(results, user_location)
```

---

**Versión**: 1.0
**Próximo paso**: Crear client de JobSpy en backend/scrapers/jobspy_client.py
