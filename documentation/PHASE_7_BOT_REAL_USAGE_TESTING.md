# FASE 7: Pruebas de Bot - Uso Real y Limitaciones Encontradas

**Fecha**: 2026-02-21
**Estado**: ⚠️ LIMITACIONES IDENTIFICADAS EN TESTING
**Prioridad**: ALTA (afecta UX y matching quality)

---

## 🔑 Limitaciones Clave Encontradas

1. **Gemini Free Tier**: Max 20 requests/día → No puede analizar todos los jobs
2. **JobSpy Diversity**: Si Indeed devuelve 25, los TOP 5 pueden ser todos de Indeed
3. **CSV Export**: Funciona bien pero TOP 5 pueden no ser óptimos

---

## 🎯 Problema Identificado

Para hacer **matching ÓPTIMO**, necesitamos analizar **TODOS los jobs** con Gemini.

Pero el free tier de Gemini tiene límites:

```
📊 Límites Gemini 2.5 Flash (Free Tier):
├── 5 requests/minuto
└── 20 requests/día ← ⚠️ CUELLO DE BOTELLA
```

### Caso Real:
```
Búsqueda con keywords "Marketing Digital, Ventas" en Mexico:
├── Indeed: 25 jobs
├── LinkedIn: 2 jobs
├── Glassdoor: 0 jobs
└── TOTAL: 27 jobs

Para análisis ÓPTIMO:
  27 requests a Gemini = EXCEDE límite de 20/día ❌

Solución ACTUAL:
  5 requests a Gemini = Dentro del límite ✅
  PERO: Solo analiza primeros 5 (puede perder mejores matches)
```

---

## 📋 Impacto en UX

| Escenario | Jobs Encontrados | Gemini Requests | Status | Matching |
|-----------|------------------|-----------------|--------|----------|
| Búsqueda pequeña (< 5 jobs) | 3-4 | 3-4 | ✅ | ÓPTIMO |
| Búsqueda normal (5-20 jobs) | 12 | 5 (TOP 5) | ✅ | PARCIAL |
| Búsqueda grande (> 20 jobs) | 27+ | 5 (TOP 5) | ✅ | SUBÓPTIMO |

**Problema**: Si Indeed devuelve 25 jobs al inicio, los TOP 5 por Gemini serán todos de Indeed (no diverso).

---

## 🔧 Soluciones Propuestas

### Opción A: Upgrade Gemini a Cuenta Paga ⭐ RECOMENDADO
```
✅ Límites:
   • 1,000 requests/minuto
   • 10,000 requests/día
✅ Análisis de TODOS los jobs sin restricción
✅ Mejor matching + diversidad
❌ Costo: $0.075 per 1M tokens
```

### Opción B: Diversificar Muestreo
```
En lugar de jobs[:5], tomar:
├── 3 jobs de Indeed
├── 1-2 jobs de LinkedIn
└── 1 job de Glassdoor

✅ Respeta límite Gemini (5 requests)
✅ Diversidad garantizada
❌ Puede perder mejores matches si están en positions 6-25
```

### Opción C: Batch Processing
```
Analizar en batches a través del día:
├── Día 1: Primeros 20 jobs
├── Día 2: Siguientes 20 jobs
└── Día 3: Resto

✅ Sin exceder límite diario
❌ UX pobre: usuario espera TOP 5 "ahora"
```

### Opción D: Usar Otro LLM
```
Alternativas con límites más generosos:
├── Claude (Anthropic) - 50k tokens/min
├── GPT-4 (OpenAI) - Pay-as-you-go
└── Local LLM (Ollama) - Sin límite

❌ Requiere refactor del código
```

---

## 📊 Estado Actual (Fase 6)

```
Implementado: Opción B (Parcial)
├── Procesa TOP 5 jobs
├── Ordena por match_score DESC
├── Envía TOP 5 a usuario
└── CSV con TODOS los 27 jobs

Limitación:
  Si Indeed llena los primeros 25, TOP 5 serán:
  [Indeed#1, Indeed#2, Indeed#3, Indeed#4, Indeed#5]

  LinkedIn (2 jobs) nunca llega al TOP 5
```

---

## 🚀 Recomendación para Producción

**Implementar Opción A (Upgrade Pago)** cuando el bot esté listo para escalar:

1. **Corto plazo (Testing actual)**:
   - Mantener Opción B (TOP 5 de primeros jobs)
   - Documentar en CSV que hay más empleos
   - Mencionar en UI: "Showing best 5 of 27 jobs"

2. **Mediano plazo (MVP)**:
   - Usuario puede upgraar Gemini API
   - Bot obtiene API key pago del usuario
   - Analiza TODOS los jobs → matching óptimo

3. **Largo plazo (Producción)**:
   - Empresa paga por Gemini API
   - Análisis completo para todos los usuarios
   - Caché de resultados (evitar re-analysis)

---

## 💡 Workarounds Temporales

Mientras usas free tier:

```python
# Opción B mejorada: Diversificar antes de analizar
jobs_diverse = []
jobs_diverse.extend(jobs_by_source["indeed"][:3])
jobs_diverse.extend(jobs_by_source["linkedin"][:1])
jobs_diverse.extend(jobs_by_source["glassdoor"][:1])

# Luego analizar estos 5 con Gemini
top_5 = match_jobs_batch(jobs_diverse)  # 5 requests máximo

# CSV sigue teniendo todos los 27
```

---

## 📈 Métrica de Éxito

```
Actual (Free Tier):
  ✅ Funcional
  ⚠️ Matching parcial
  ⚠️ Solo 5 de 27 analizados

Con Gemini Pago:
  ✅ Funcional
  ✅ Matching ÓPTIMO
  ✅ Todos analizados
```

---

## 🔗 Referencias

- **Gemini API Quotas**: https://ai.google.dev/gemini-api/docs/rate-limits
- **Pricing**: https://ai.google.dev/pricing
- **Status**: TESTING PHASE - Awaiting user decision on upgrade

---

**Próximos Pasos**:
- [ ] Decidir si upgrade a Gemini pago
- [ ] Implementar Opción B mejorada (diversificación)
- [ ] Comunicar limitación a usuarios
- [ ] Evaluar ROI de upgrade pago

