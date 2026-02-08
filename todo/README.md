# 📚 TODO - Plan de Implementación del Bot

Este directorio contiene el plan completo para implementar el bot de Telegram con notificaciones de vacantes personalizadas.

---

## 📋 Estructura de Fases

```
todo/
├── README.md                  # Este archivo
├── pruebasApi/               # ← EMPEZAR AQUÍ (Entender la API)
│   ├── 01-SETUP.md
│   ├── 02-TEST_BASICO.md
│   ├── 03-TEST_FILTROS.md
│   ├── 04-TEST_RATE_LIMIT.md
│   ├── 05-TEST_MULTIPLES.md
│   ├── 06-ANALISIS_FINAL.md
│   ├── README.md
│   └── scripts/
│
├── 01-SETUP.md              # [Próximamente] Setup del proyecto
├── 02-FIREBASE.md           # [Próximamente] Config Firebase/Sheets
├── 03-DATABASE.md           # [Próximamente] Modelos y queries
├── 04-BACKEND.md            # [Próximamente] Scheduler y scraping
├── 05-BOT.md                # [Próximamente] Handlers de Telegram
├── 06-TESTS.md              # [Próximamente] Suite de tests
└── 07-DEPLOYMENT.md         # [Próximamente] Deploy en servidor
```

---

## 🎯 Orden de Ejecución

### ✅ FASE ACTUAL: Análisis de JobSpy API
```
📁 pruebasApi/
├─ 01-SETUP.md              [10-15 min]  Levantar Docker
├─ 02-TEST_BASICO.md        [15-20 min]  Primeras búsquedas
├─ 03-TEST_FILTROS.md       [15 min]     Validar filtros
├─ 04-TEST_RATE_LIMIT.md    [15 min]     Entender límites
├─ 05-TEST_MULTIPLES.md     [15-20 min]  Simular uso real
└─ 06-ANALISIS_FINAL.md     [10 min]     Conclusiones

⏱️  TOTAL: ~90 minutos
📌 REQUISITO: Completar ANTES de empezar con el bot
```

### ⏳ PRÓXIMAS FASES (después de pruebas)

1. **FASE 1: Setup del Proyecto** (~30 min)
   - Crear estructura de directorios
   - Setup de `uv` y dependencias
   - Variables de entorno

2. **FASE 2: Database** (~60 min)
   - Setup de Google Sheets API
   - Modelos de datos (User, Job)
   - Queries básicas

3. **FASE 3: Backend** (~120 min)
   - Integración con JobSpy API
   - APScheduler para búsquedas automáticas
   - Lógica de filtrado y deduplicación

4. **FASE 4: Bot** (~90 min)
   - Handlers de Telegram (`/perfil`, `/vacantes`, etc)
   - Notificaciones personalizadas
   - Integración con backend

5. **FASE 5: Tests** (~60 min)
   - Tests unitarios
   - Tests de integración
   - Coverage > 80%

6. **FASE 6: Deployment** (~45 min)
   - Setup en servidor Linux
   - Systemd service
   - Monitoreo

---

## 🚀 Cómo Empezar Ahora Mismo

### Opción 1: Guía Rápida (si tienes prisa)
```bash
cd pruebasApi
# Lee el README.md de pruebas
cat README.md

# Ejecuta solo el setup y tests básicos (30 min)
bash 01-SETUP.md
python scripts/test_basico.py
```

### Opción 2: Análisis Completo (recomendado)
```bash
cd pruebasApi
# Lee TODO con detenimiento
for file in 01-SETUP.md 02-TEST_BASICO.md 03-TEST_FILTROS.md 04-TEST_RATE_LIMIT.md 05-TEST_MULTIPLES.md 06-ANALISIS_FINAL.md; do
  echo "📖 Leyendo $file..."
  cat $file
  echo ""
done

# Ejecuta todos los scripts
python scripts/test_basico.py
python scripts/test_filtros.py
python scripts/test_rate_limit.py
python scripts/test_multiples.py
```

### Opción 3: Test Manual (si prefieres curl)
```bash
cd pruebasApi
# Lee 01-SETUP.md para levantar Docker
cat 01-SETUP.md

# Luego copia y pega los comandos curl de 02-TEST_BASICO.md
```

---

## 📊 Checklist General

- [ ] **Pruebas API** - Completar `pruebasApi/`
  - [ ] Setup (Docker levantado)
  - [ ] Tests básicos ejecutados
  - [ ] Filtros validados
  - [ ] Rate limiting entendido
  - [ ] Múltiples usuarios simulados
  - [ ] Análisis final completado

- [ ] **Diseño del Bot** (después de pruebas)
  - [ ] Modelos de datos definidos
  - [ ] Estructura de directorios lista
  - [ ] Dependencias en `pyproject.toml`

- [ ] **Implementación** (próximas fases)
  - [ ] Database setup
  - [ ] Backend funcionando
  - [ ] Bot handlers implementados
  - [ ] Tests pasando
  - [ ] Deployed en servidor

---

## 📚 Referencias

- `contexto/idea.md` - Requisitos del proyecto
- `contexto/stack.md` - Tech stack
- `contexto/CLAUDE.md` - Guía de trabajo
- `contexto/scrapersdoc.md` - Documentación de JobSpy
- `contexto/JOBSPY_API_ANALYSIS.md` - Análisis detallado de API

---

## 🔗 Relación entre Documentos

```
contexto/idea.md
    ↓
contexto/stack.md
    ↓
contexto/JOBSPY_API_ANALYSIS.md (referencia API)
    ↓
todo/pruebasApi/ (ERES AQUÍ → validar API)
    ↓
todo/01-SETUP.md (estructura del proyecto)
    ↓
todo/02-FIREBASE.md (database)
    ↓
todo/03-DATABASE.md (modelos)
    ↓
todo/04-BACKEND.md (integración)
    ↓
todo/05-BOT.md (Telegram)
    ↓
todo/06-TESTS.md (pruebas)
    ↓
todo/07-DEPLOYMENT.md (producción)
```

---

## ⏰ Estimación Total

| Fase | Duración | Estado |
|------|----------|--------|
| **Pruebas API** | ~90 min | 🔴 **AHORA** |
| Setup Proyecto | ~30 min | ⏳ |
| Database | ~60 min | ⏳ |
| Backend | ~120 min | ⏳ |
| Bot | ~90 min | ⏳ |
| Tests | ~60 min | ⏳ |
| Deployment | ~45 min | ⏳ |
| **TOTAL** | **~495 min (~8h)** | |

---

## 💡 Principios de Trabajo

1. **Tests Primero (TDD)**
   - Escribe tests antes de código
   - Red → Green → Refactor

2. **Documentación mientras Avanzas**
   - Cada fase tiene su archivo `.md`
   - Consigna hallazgos inmediatamente

3. **Sin Commits sin Permiso**
   - Solo documenta y prepara
   - Usuario decide cuándo commitear

4. **Entender antes de Codificar**
   - `pruebasApi/` es crucial
   - Evita decisiones equivocadas después

---

## 📞 Contacto/Dudas

Si tienes dudas mientras avanzas:
1. Revisa `contexto/CLAUDE.md`
2. Pregunta antes de continuar
3. Nunca asumas decisiones técnicas

---

## ✅ Estado Actual

**Última actualización**: 2026-01-31
**Fase actual**: 🔴 Análisis de JobSpy API
**Siguiente**: Pruebas completas en `pruebasApi/`

---

**¡Listo para empezar? Entra en `pruebasApi/README.md`! 🚀**
