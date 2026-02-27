"""
JobSpy API Client - Búsqueda de vacantes en múltiples plataformas

Propósito:
- Conectar con rainmanjam/jobspy-api (Docker en localhost:8000)
- Buscar vacantes en Indeed, LinkedIn, Glassdoor
- Parsear respuestas a Job models (Pydantic)
- Manejar diferencias entre plataformas

Consideraciones (de tests/pruebasApi/HALLAZGOS_CONSOLIDADOS.md):
- Indeed: 1-2s, requiere country_indeed (nombre completo)
- LinkedIn: 0.6-1s, ignora country_indeed, job_type=null
- Glassdoor: 0.3s, requiere country_indeed, poco confiable
- Rate limiting: 2-5s entre búsquedas (no hay 429, pero timeouts)
"""

import logging
import time
import requests
from typing import List, Optional
from urllib.parse import urljoin

from database.models import Job

logger = logging.getLogger(__name__)


class JobSpyClient:
    """Cliente para JobSpy API (localhost:8000)"""

    # Plataformas válidas
    VALID_PLATFORMS = ["indeed", "linkedin", "glassdoor"]

    # Tipos de trabajo válidos
    VALID_JOB_TYPES = ["contract", "fulltime", "parttime", "internship"]

    # Países válidos (nombres completos para API)
    VALID_COUNTRIES = {
        "usa": "USA",
        "colombia": "Colombia",
        "canada": "Canada",
        "uk": "UK",
        "mexico": "Mexico",
        "argentina": "Argentina",
        "chile": "Chile",
        "peru": "Peru",
        "spain": "Spain",
        "germany": "Germany",
        "france": "France",
        "brazil": "Brazil",
    }

    def __init__(self, api_url: str = "http://localhost:8000", timeout: int = 30):
        """
        Inicializar cliente JobSpy

        Args:
            api_url: URL base de API (default: localhost:8000)
            timeout: Timeout en segundos para requests
        """
        self.api_url = api_url
        self.timeout = timeout
        self.endpoint = urljoin(api_url, "/api/v1/search_jobs")

        logger.info(f"✅ JobSpyClient inicializado: {self.api_url}")

    def search_jobs(
        self,
        keywords: str,
        country: str,
        job_type: Optional[str] = None,
        is_remote: Optional[bool] = None,
        platforms: Optional[List[str]] = None,
        results_wanted: int = 25,
    ) -> List[Job]:
        """
        Buscar empleos en JobSpy API

        Args:
            keywords: Términos de búsqueda (ej: "python remote")
            country: País (ej: "Colombia", "USA")
            job_type: Tipo de empleo (contract, fulltime, parttime, internship)
            is_remote: Si es remoto (True/False/None)
            platforms: Lista de plataformas (default: todas)
            results_wanted: Cuántos resultados (default: 25)

        Returns:
            List[Job]: Lista de modelos Job

        Raises:
            ValueError: Si parámetros son inválidos
        """
        # Validar parámetros
        self._validate_params(keywords, country, job_type)

        # Por defecto, buscar en todas las plataformas
        if platforms is None:
            platforms = self.VALID_PLATFORMS

        # Convertir país a nombre completo
        country_name = self._normalize_country(country)

        all_jobs = []

        # Buscar en cada plataforma
        for platform in platforms:
            logger.info(
                f"🔍 Buscando en {platform.upper()}: {keywords} ({country_name})"
            )

            try:
                jobs = self._search_platform(
                    platform=platform,
                    keywords=keywords,
                    country=country_name,
                    job_type=job_type,
                    is_remote=is_remote,
                    results_wanted=results_wanted,
                )
                all_jobs.extend(jobs)

            except Exception as e:
                logger.error(f"❌ Error buscando en {platform}: {e}")
                continue

            # Rate limiting: esperar entre búsquedas (2-3 segundos)
            time.sleep(2)

        logger.info(
            f"✅ Total de jobs encontrados: {len(all_jobs)} "
            f"({', '.join(set(j.source for j in all_jobs))})"
        )

        return all_jobs

    def _search_platform(
        self,
        platform: str,
        keywords: str,
        country: str,
        job_type: Optional[str] = None,
        is_remote: Optional[bool] = None,
        results_wanted: int = 25,
    ) -> List[Job]:
        """
        Buscar en una plataforma específica

        Consideraciones especiales:
        - Indeed: requiere country_indeed
        - LinkedIn: ignora country_indeed
        - Glassdoor: requiere country_indeed
        """
        params = {
            "search_term": keywords,
            "site_name": platform,
            "results_wanted": results_wanted,
        }

        # LinkedIn NO requiere country_indeed (lo ignora)
        # Indeed y Glassdoor SÍ lo requieren
        if platform != "linkedin":
            params["country_indeed"] = country

        # job_type: Indeed lo respeta, LinkedIn lo ignora
        if job_type:
            params["job_type"] = job_type

        # is_remote: Indeed lo respeta, LinkedIn lo ignora
        if is_remote is not None:
            params["is_remote"] = is_remote

        logger.debug(f"Parámetros de búsqueda: {params}")

        # Hacer request
        response = requests.get(
            self.endpoint,
            params=params,
            timeout=self.timeout,
        )

        response.raise_for_status()  # Lanzar error si status != 200

        # Parsear respuesta
        data = response.json()
        jobs_data = data.get("jobs", [])
        count = data.get("count", 0)

        logger.info(
            f"✅ {platform.upper()}: {count} resultados en {response.elapsed.total_seconds():.2f}s"
        )

        # Convertir a Job objects
        jobs = [self._parse_job(job_data, platform) for job_data in jobs_data]

        return jobs

    def _parse_job(self, job_data: dict, platform: str) -> Job:
        """
        Parsear respuesta JSON a Job model (Pydantic)

        Args:
            job_data: Dict con datos del trabajo
            platform: Plataforma (indeed, linkedin, glassdoor)

        Returns:
            Job: Modelo Pydantic validado
        """
        # Location viene como string ("ANT, CO") pero Job model espera None
        # Para MVP, ignoramos location (se puede parsear luego)
        location = None

        # Mapear campos de la API a Job model
        job = Job(
            id=job_data.get("id"),
            title=job_data.get("title"),
            company=job_data.get("company"),
            company_url=job_data.get("company_url"),
            job_url=job_data.get("job_url"),
            location=location,  # Ignorar por ahora (es string en API)
            is_remote=job_data.get("is_remote", False),
            description=job_data.get("description"),
            job_type=job_data.get("job_type"),
            job_function=job_data.get("job_function"),
            job_level=job_data.get("job_level"),
            company_industry=job_data.get("company_industry"),
            date_posted=job_data.get("date_posted"),
            source=platform,  # Marcar plataforma
            scraped_at=None,  # Se puede llenar después
        )

        return job

    def _validate_params(
        self, keywords: str, country: str, job_type: Optional[str]
    ) -> None:
        """
        Validar parámetros de búsqueda

        Raises:
            ValueError: Si algún parámetro es inválido
        """
        # Validar keywords
        if not keywords or not keywords.strip():
            raise ValueError("keywords no puede estar vacío")

        # Validar country
        if not country or not country.strip():
            raise ValueError("country no puede estar vacío")

        if country.lower() not in self.VALID_COUNTRIES:
            available = ", ".join(set(self.VALID_COUNTRIES.values()))
            raise ValueError(
                f"country '{country}' no válido. "
                f"Válidos: {available}"
            )

        # Validar job_type
        if job_type and job_type.lower() not in self.VALID_JOB_TYPES:
            raise ValueError(
                f"job_type '{job_type}' no válido. "
                f"Válidos: {', '.join(self.VALID_JOB_TYPES)}"
            )

    def _normalize_country(self, country: str) -> str:
        """
        Convertir país a nombre completo (para API)

        Ej: "colombia" → "Colombia", "usa" → "USA"

        Args:
            country: País (cualquier caso)

        Returns:
            str: Nombre completo del país
        """
        country_lower = country.lower().strip()

        if country_lower not in self.VALID_COUNTRIES:
            raise ValueError(f"País no válido: {country}")

        return self.VALID_COUNTRIES[country_lower]

    def check_api_health(self) -> bool:
        """
        Verificar si API está corriendo

        Returns:
            bool: True si API responde, False si error
        """
        try:
            health_url = urljoin(self.api_url, "/health")
            response = requests.get(health_url, timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"❌ API no está disponible: {e}")
            return False
