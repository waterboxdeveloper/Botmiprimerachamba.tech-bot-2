con# 🔍 Hallazgos Consolidados - Tests API JobSpy

**Fecha**: 2026-02-01
**Agente de Prueba**: Test Suite Básico
**Estado**: Validado ✅

---

## 1️⃣ Estructura de Respuesta API

### ❌ INCORRECTO (documentación anterior)
```json
{
  "data": [...],
  "status": "success",
  "count": 45
}
```

### ✅ CORRECTO (respuesta real)
```json
{
  "count": 45,
  "jobs": [...],
  "cached": false
}
```

**Cambio crítico**:
- Campo de trabajos es `'jobs'` NO `'data'`
- NO hay campo `'status'`
- Hay campo `'cached'` para indicar si está en caché

---

## 2️⃣ Comportamiento por Plataforma

### Indeed
| Aspecto | Dato |
|---------|------|
| **Velocidad** | 1-2 segundos |
| **Fiabilidad** | ⭐⭐⭐⭐⭐ Excelente |
| **Campos** | Completos (title, company, location, job_type, is_remote, date_posted) |
| **Salario** | ❌ Raramente disponible (null) |
| **Filtros** | ✅ Respeta is_remote, job_type |
| **Requerimientos** | ✅ `country_indeed` OBLIGATORIO (nombre completo: "USA", "Colombia", etc) |
| **Ejemplo Exitoso** | "ux designer" USA remote contract → 5 resultados |

### LinkedIn
| Aspecto | Dato |
|---------|------|
| **Velocidad** | 0.6-1 segundo ⚡ (MÁS RÁPIDO) |
| **Fiabilidad** | ⭐⭐⭐ Media |
| **Campos** | Incompletos (falta job_type, location a veces vacío) |
| **Salario** | ❌ Nunca disponible (null) |
| **Filtros** | ⚠️ Ignora job_type (devuelve null) |
| **Requerimientos** | ❌ NO requiere country |
| **Problema** | job_type=None aunque lo especifiques |
| **Ejemplo** | "ui designer" USA remote contract → 5 resultados pero sin job_type |

### Glassdoor
| Aspecto | Dato |
|---------|------|
| **Velocidad** | 0.3 segundos ⚡ (MÁS RÁPIDO) |
| **Fiabilidad** | ⭐⭐ Baja (inconsistente) |
| **Campos** | Depende del resultado |
| **Salario** | ❌ Raramente disponible |
| **Filtros** | ⚠️ Poco confiables |
| **Requerimientos** | ✅ `country_indeed` OBLIGATORIO |
| **Problema** | A veces 0 resultados aunque existan |
| **Ejemplo** | "graphic designer" UK remote → 0 resultados |

---

## 3️⃣ Campos Disponibles por Plataforma

### Indeed - Campos Presentes
```
✅ id, site, title, company, job_url, job_url_direct
✅ location, is_remote, job_type, date_posted
❌ job_level, job_function, description
❌ salary: min_amount, max_amount, currency, interval
```

### LinkedIn - Campos Presentes
```
✅ id, site, title, company, job_url
❌ job_url_direct (siempre null)
❌ location (frecuentemente vacío)
❌ job_type (siempre null incluso si especificas)
✅ is_remote, date_posted
❌ job_level, job_function, description
❌ salary: todo null
```

### Glassdoor - Campos Presentes
```
✅ id, site, title, company, job_url
❌ Otros campos menos confiables
```

---

## 4️⃣ Parámetros Validados

| Parámetro | Funciona | Notas |
|-----------|----------|-------|
| `search_term` | ✅ Obligatorio | Funciona bien |
| `site_name` | ✅ | Especifica plataforma |
| `country_indeed` | ✅ Condicional | OBLIGATORIO para Indeed/Glassdoor. Usar nombre completo (USA, Colombia, UK, etc) |
| `is_remote` | ✅ Parcialmente | Indeed respeta. LinkedIn ignora |
| `job_type` | ✅ Parcialmente | Indeed respeta. LinkedIn devuelve null |
| `results_wanted` | ✅ | Limita resultados |

---

## 5️⃣ Tiempos de Respuesta

```
Glassdoor (sin resultados):  0.32s  ⚡ MÁS RÁPIDO
LinkedIn:                     0.67s  ✅ Rápido
Indeed (USA):                1.27s  ⚠️  Moderado
Indeed (Colombia):           1.83s  ⚠️  Más lento
```

---

## 6️⃣ Recomendaciones para el Bot

### Para Usuarios en USA/Canadá/UK:
```
Usar: Indeed + LinkedIn
- Indeed primero (más fiable)
- LinkedIn como respaldo (más rápido)
- Glassdoor NO recomendado
```

### Para Usuarios en Colombia/Latam:
```
Usar: Indeed
- Usar country_indeed="Colombia" (nombre completo)
- LinkedIn fallará (no especifica country)
```

### Para Búsquedas de Salario:
```
❌ NO CONFIAR en salarios
- min_amount, max_amount casi siempre null
```

---

**Versión**: 1.0
**Siguiente paso**: Ejecutar test_filtros.py, test_rate_limit.py, test_multiples.py
