"""
Tests para FASE 6: Handler /vacantes (on-demand job search)

Propósito: Probar flujo completo de búsqueda personalizada de empleos
- Obtener perfil del usuario (BD)
- Buscar empleos (JobSpyClient)
- Personalizar con Gemini 2.5 Flash (LangChain)
- Enviar a Telegram con formato bonito

Framework: pytest + mocking
Complejidad: ALTA (multiples integraciones)
"""

import pytest
from typing import List
from database.models import User, Job


class TestDatabaseQueries:
    """Tests para queries de BD - obtener perfil del usuario"""

    def test_get_user_profile_exists(self):
        """
        RED TEST: Obtener perfil de usuario existente desde BD

        Escenario:
        - Usuario con ID existe en BD
        - Debe retornar User model con keywords, país, etc
        """
        from database.queries import get_user_profile

        # Usuario que guardó perfil en FASE 4
        telegram_id = "998566560"
        user = get_user_profile(telegram_id)

        assert user is not None
        assert isinstance(user, User)
        assert user.telegram_id == telegram_id
        assert len(user.keywords) > 0
        assert user.location_preference is not None

    def test_get_user_profile_not_found(self):
        """
        RED TEST: Usuario no existe en BD

        Escenario:
        - Usuario nunca hizo /perfil
        - Debe retornar None o lanzar excepción clara
        """
        from database.queries import get_user_profile

        user = get_user_profile("999999999")
        assert user is None

    def test_get_user_profile_has_keywords_list(self):
        """
        RED TEST: Keywords vienen como lista

        Escenario:
        - BD guarda keywords como JSON
        - Debe parsear a List[str]
        """
        from database.queries import get_user_profile

        telegram_id = "998566560"
        user = get_user_profile(telegram_id)

        assert isinstance(user.keywords, list)
        assert all(isinstance(k, str) for k in user.keywords)


class TestVacantesSearchIntegration:
    """Tests para búsqueda de empleos - JobSpyClient integration"""

    def test_search_jobs_with_user_keywords(self):
        """
        RED TEST: Buscar empleos usando keywords del usuario

        Escenario:
        - Usuario tiene keywords: ["python", "remote", "contract"]
        - Bot construye search_term y busca
        - Debe retornar List[Job]
        """
        from database.queries import get_user_profile
        from backend.scrapers.jobspy_client import JobSpyClient

        # 1. Obtener perfil del usuario
        user = get_user_profile("998566560")
        assert user is not None

        # 2. Construir search_term desde keywords
        search_term = " ".join(user.keywords)

        # 3. Buscar empleos
        client = JobSpyClient()
        jobs = client.search_jobs(
            keywords=search_term,
            country=user.location_preference,
            job_type=None,  # User didn't specify
        )

        assert isinstance(jobs, list)
        assert len(jobs) > 0
        assert all(isinstance(job, Job) for job in jobs)

    def test_search_jobs_respects_country(self):
        """
        RED TEST: Búsqueda respeta país del usuario

        Escenario:
        - Usuario guardó país: "Mexico"
        - Búsqueda debe usar ese país
        """
        from database.queries import get_user_profile
        from backend.scrapers.jobspy_client import JobSpyClient

        user = get_user_profile("998566560")
        client = JobSpyClient()

        jobs = client.search_jobs(
            keywords="python",
            country=user.location_preference,
        )

        assert len(jobs) > 0
        # Al menos algunos jobs deben ser relevantes al país


class TestGeminiPersonalization:
    """Tests para personalización con Gemini 2.5 Flash"""

    def test_gemini_agent_personalizes_job(self):
        """
        RED TEST: LangChain agent personaliza un job

        Escenario:
        - Job: "Senior Python Developer - Acme Corp"
        - User keywords: ["python", "remote", "senior"]
        - Gemini devuelve: "Matches porque: Python (✅), Remote (✅), Senior (✅)"
        """
        from backend.agents.job_matcher import JobMatcher

        # Mock job
        job = Job(
            id="indeed-123",
            title="Senior Python Developer",
            company="Acme Corp",
            job_url="https://indeed.com/jobs/123",
            is_remote=True,
            job_type="fulltime",
            description="We need a Senior Python dev...",
        )

        # User profile
        user_keywords = ["python", "remote", "senior"]
        user_location = "USA"

        # Personalizar
        matcher = JobMatcher()
        result = matcher.match_job(
            job=job,
            user_keywords=user_keywords,
            user_location=user_location,
        )

        assert result is not None
        assert hasattr(result, "match_score")
        assert hasattr(result, "personalized_message")
        assert 0 <= result.match_score <= 100
        assert len(result.personalized_message) > 0

    def test_gemini_agent_scores_job_correctly(self):
        """
        RED TEST: Score de match es coherente

        Escenario:
        - Job que matchea MUCHO: score alto (80+)
        - Job que matchea POCO: score bajo (20-)
        """
        from backend.agents.job_matcher import JobMatcher

        # Job que matchea MUCHO
        perfect_job = Job(
            id="indeed-123",
            title="Python Developer - Remote - Contract",
            company="TechCorp",
            job_url="https://indeed.com/jobs/123",
            is_remote=True,
            job_type="contract",
            description="Python, remote, contract position",
        )

        # Job que matchea POCO
        bad_job = Job(
            id="indeed-456",
            title="Senior Java Developer - On-site - Fulltime",
            company="OldCorp",
            job_url="https://indeed.com/jobs/456",
            is_remote=False,
            job_type="fulltime",
            description="Java on-site position",
        )

        user_keywords = ["python", "remote", "contract"]
        user_location = "USA"

        matcher = JobMatcher()

        perfect_match = matcher.match_job(perfect_job, user_keywords, user_location)
        bad_match = matcher.match_job(bad_job, user_keywords, user_location)

        # Perfect match debería tener score más alto
        assert perfect_match.match_score > bad_match.match_score


class TestTelegramFormatting:
    """
    Tests para formato de mensajes en Telegram

    NOTA: Comentados porque Gemini YA devuelve telegram_message formateado.
    JobMatchResult.telegram_message viene listo para enviar a Telegram.
    No necesitamos formatter separado.
    """

    # def test_format_single_job_for_telegram(self):
    #     """DEPRECATED: Gemini ya formatea el mensaje"""
    #     pass

    # def test_format_multiple_jobs_with_separator(self):
    #     """DEPRECATED: Gemini ya formatea el mensaje"""
    #     pass


class TestVacantesHandler:
    """Tests para handler /vacantes - flujo completo"""

    def test_vacantes_handler_success(self):
        """
        RED TEST: Flujo completo /vacantes funciona

        Escenario:
        1. Usuario hace /vacantes
        2. Bot obtiene perfil
        3. Bot busca empleos
        4. Bot personaliza con Gemini
        5. Bot envía a Telegram

        Esperado: Sin errores, usuario recibe TOP 3-5 empleos
        """
        # Este test se implementará con mocking de Telegram
        # Por ahora es placeholder
        pass

    def test_vacantes_handler_user_not_configured(self):
        """
        RED TEST: Usuario sin /perfil intenta /vacantes

        Escenario:
        - Usuario nuevo nunca hizo /perfil
        - Intenta /vacantes
        - Bot debe responder: "❌ Primero debes configurar tu perfil con /perfil"
        """
        pass

    def test_vacantes_handler_no_jobs_found(self):
        """
        RED TEST: Búsqueda sin resultados

        Escenario:
        - User keywords: ["xyz-job-that-doesnt-exist"]
        - Bot no encuentra empleos
        - Responde: "😞 No encontramos empleos con tus criterios. Intenta otros keywords."
        """
        pass


class TestErrorHandling:
    """Tests para manejo de errores"""

    def test_vacantes_handler_api_error_graceful(self):
        """
        RED TEST: Error en JobSpyClient → mensaje claro

        Escenario:
        - API de JobSpy está offline
        - Bot debe responder: "⚠️ Error buscando empleos. Intenta más tarde."
        - NO crash, NO error técnico al usuario
        """
        pass

    def test_vacantes_handler_gemini_error_fallback(self):
        """
        RED TEST: Error en Gemini → enviar sin personalización

        Escenario:
        - Gemini API falla
        - Bot busca empleos correctamente
        - Envía TOP 3-5 SIN personalización (sin "matches porque")
        - Usuario aún recibe empleos válidos
        """
        pass

    def test_vacantes_handler_timeout_handling(self):
        """
        RED TEST: Búsqueda tarda mucho → timeout graceful

        Escenario:
        - Búsqueda tarda > 60 segundos
        - Bot responde: "Búsqueda en progreso... espera un momento"
        - NO deja al usuario sin respuesta
        """
        pass
