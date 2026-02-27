"""
Tests para backend/scrapers/jobspy_client.py

Propósito: Probar integración con JobSpy API (localhost:8000)
Consideraciones: Indeed, LinkedIn, Glassdoor tienen diferente comportamiento
Framework: pytest + mocking + real API calls
Complejidad: ALTA (API real, manejo de errores, rate limiting)
"""

import pytest
from typing import List
from database.models import Job


class TestJobSpyClient:
    """Tests para JobSpyClient"""

    def test_jobspy_client_initializes(self):
        """
        RED TEST: JobSpyClient debe inicializarse con URL de API

        Escenario:
        - Importar JobSpyClient
        - Inicializar con URL de API
        - Verificar que está listo
        """
        from backend.scrapers.jobspy_client import JobSpyClient

        client = JobSpyClient(api_url="http://localhost:8000")
        assert client is not None
        assert client.api_url == "http://localhost:8000"

    def test_search_jobs_basic(self):
        """
        RED TEST: search_jobs() debe retornar lista de Jobs

        Escenario:
        - Buscar "python" en Colombia
        - Debe retornar lista de Job objects
        - Mínimo 1 resultado
        """
        from backend.scrapers.jobspy_client import JobSpyClient

        client = JobSpyClient()
        jobs = client.search_jobs(keywords="python", country="Colombia")

        assert isinstance(jobs, list)
        assert len(jobs) > 0
        assert all(isinstance(job, Job) for job in jobs)

    def test_search_jobs_with_country(self):
        """
        RED TEST: search_jobs() debe respetar parámetro country

        Escenario:
        - Buscar en "Colombia"
        - Resultados deben tener jobs válidos (location es optional, Glassdoor lo omite)
        """
        from backend.scrapers.jobspy_client import JobSpyClient

        client = JobSpyClient()
        jobs = client.search_jobs(keywords="python", country="Colombia")

        assert len(jobs) > 0
        # Todos los jobs deben tener campos obligatorios (title, company, job_url)
        for job in jobs:
            assert job.title is not None
            assert job.company is not None
            assert job.job_url is not None

    def test_search_jobs_with_job_type(self):
        """
        RED TEST: search_jobs() debe respetar parámetro job_type

        Escenario:
        - Buscar "python" tipo "contract"
        - Resultados deben tener job_type="contract" (si Indeed respeta)
        """
        from backend.scrapers.jobspy_client import JobSpyClient

        client = JobSpyClient()
        jobs = client.search_jobs(
            keywords="python", country="USA", job_type="contract"
        )

        assert len(jobs) > 0
        # Indeed respeta job_type, LinkedIn no (devuelve null)
        indeed_jobs = [j for j in jobs if j.source == "indeed"]
        if indeed_jobs:
            # Indeed jobs deben tener job_type
            jobs_with_type = [j for j in indeed_jobs if j.job_type]
            assert len(jobs_with_type) > 0

    def test_search_jobs_remote_filter(self):
        """
        RED TEST: search_jobs() con is_remote=True debe filtrar remote

        Escenario:
        - Buscar "python" remoto
        - Resultados deben tener is_remote=True
        """
        from backend.scrapers.jobspy_client import JobSpyClient

        client = JobSpyClient()
        jobs = client.search_jobs(
            keywords="python remote", country="USA", is_remote=True
        )

        assert len(jobs) > 0
        # Algún job debe tener is_remote=True
        remote_jobs = [j for j in jobs if j.is_remote]
        assert len(remote_jobs) > 0


class TestJobSpyClientPlatforms:
    """Tests específicos por plataforma"""

    def test_search_indeed_only(self):
        """
        RED TEST: search_jobs() puede buscar solo en Indeed

        Escenario:
        - Parámetro platforms=["indeed"]
        - Retorna jobs solo de Indeed
        """
        from backend.scrapers.jobspy_client import JobSpyClient

        client = JobSpyClient()
        jobs = client.search_jobs(
            keywords="python", country="Colombia", platforms=["indeed"]
        )

        assert len(jobs) > 0
        assert all(job.source == "indeed" for job in jobs)

    def test_search_linkedin_only(self):
        """
        RED TEST: search_jobs() puede buscar solo en LinkedIn

        Escenario:
        - Parámetro platforms=["linkedin"]
        - Retorna jobs solo de LinkedIn
        """
        from backend.scrapers.jobspy_client import JobSpyClient

        client = JobSpyClient()
        jobs = client.search_jobs(
            keywords="python", country="USA", platforms=["linkedin"]
        )

        assert len(jobs) > 0
        assert all(job.source == "linkedin" for job in jobs)

    def test_search_all_platforms(self):
        """
        RED TEST: search_jobs() busca en TODAS las plataformas por defecto

        Escenario:
        - Sin parámetro platforms
        - Debe buscar en Indeed + LinkedIn + Glassdoor
        - Retorna mezcla de plataformas
        """
        from backend.scrapers.jobspy_client import JobSpyClient

        client = JobSpyClient()
        jobs = client.search_jobs(keywords="python", country="USA")

        assert len(jobs) > 0

        # Debe haber jobs de al menos 2 plataformas
        sources = set(job.source for job in jobs)
        assert len(sources) >= 2, f"Se esperaban al menos 2 plataformas, obtuvo: {sources}"


class TestJobSpyClientValidation:
    """Tests para validación de parámetros"""

    def test_search_jobs_invalid_keywords(self):
        """
        RED TEST: keywords vacío debe fallar

        Escenario:
        - Llamar search_jobs(keywords="")
        - Debe lanzar ValueError
        """
        from backend.scrapers.jobspy_client import JobSpyClient

        client = JobSpyClient()

        with pytest.raises(ValueError):
            client.search_jobs(keywords="", country="Colombia")

    def test_search_jobs_invalid_country(self):
        """
        RED TEST: country inválido debe fallar

        Escenario:
        - Llamar search_jobs(country="InvalidCountry")
        - Debe lanzar ValueError o manejar gracefully
        """
        from backend.scrapers.jobspy_client import JobSpyClient

        client = JobSpyClient()

        with pytest.raises(ValueError):
            client.search_jobs(keywords="python", country="InvalidCountry")

    def test_search_jobs_invalid_job_type(self):
        """
        RED TEST: job_type inválido debe fallar

        Escenario:
        - Llamar search_jobs(job_type="invalid_type")
        - Debe lanzar ValueError
        """
        from backend.scrapers.jobspy_client import JobSpyClient

        client = JobSpyClient()

        with pytest.raises(ValueError):
            client.search_jobs(
                keywords="python",
                country="Colombia",
                job_type="invalid_type",
            )


class TestJobModelParsing:
    """Tests para parseo de respuestas a Job models"""

    def test_job_model_has_required_fields(self):
        """
        RED TEST: Job model debe tener todos los campos necesarios

        Escenario:
        - Buscar jobs
        - Verificar que cada Job tiene: id, title, company, job_url
        """
        from backend.scrapers.jobspy_client import JobSpyClient

        client = JobSpyClient()
        jobs = client.search_jobs(keywords="python", country="USA")

        for job in jobs:
            assert job.id is not None
            assert job.title is not None
            assert job.company is not None
            assert job.job_url is not None
            assert job.source is not None

    def test_job_model_optional_fields(self):
        """
        RED TEST: Job model puede tener campos opcionales

        Escenario:
        - Algunos jobs pueden no tener location, salary, etc
        - No debe lanzar error
        """
        from backend.scrapers.jobspy_client import JobSpyClient

        client = JobSpyClient()
        jobs = client.search_jobs(keywords="python", country="USA")

        # Algunos jobs pueden no tener estos campos
        for job in jobs:
            # No debe fallar si field es None
            _ = job.location
            _ = job.salary
            _ = job.job_type
