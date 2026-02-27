"""
JobMatcher Agent - Personaliza empleos con Gemini 2.5 Flash + LangChain

Propósito:
- Analizar un job contra keywords del usuario
- Calcular match score (0-100)
- Generar mensaje formateado en Markdown para Telegram
- Usar LangChain CORRECTAMENTE: FewShotPromptTemplate + with_structured_output()

Framework: LangChain + Google Generative AI (Gemini 2.5 Flash)

Diseño:
1. FewShotPromptTemplate: Ejemplos estructurados para enseñar al LLM cómo responder
2. with_structured_output(): Garantizar JSON válido con Pydantic
3. PromptTemplate: Template reutilizable para formatear ejemplos
"""

import json
import logging
import os
from typing import List, Optional
from pydantic import BaseModel, Field

from database.models import Job
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import FewShotPromptTemplate, PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Cargar variables de entorno desde .env
load_dotenv()


# ============================================================================
# MODELS
# ============================================================================


class JobMatchResult(BaseModel):
    """Resultado del análisis de match de un job - YA FORMATEADO PARA TELEGRAM"""

    job: Job = Field(..., description="Job object original (para acceder a job_url, etc)")
    match_score: float = Field(..., ge=0, le=100, description="Score de 0-100")
    personalized_message: str = Field(
        ..., description="Mensaje personalizado generado por Gemini"
    )
    telegram_message: str = Field(
        ..., description="Mensaje YA formateado en Markdown para Telegram, listo para enviar"
    )


# ============================================================================
# FEW-SHOT EXAMPLES (Ejemplos estructurados para el LLM)
# ============================================================================

EXAMPLES = [
    {
        "job_info": """
Job: Senior Python Developer
Company: Acme Corp
Remote: Yes
Type: Contract
Description: We're looking for a Senior Python Developer with 5+ years experience.
             Strong in FastAPI, PostgreSQL. Remote-first company.
""",
        "user_profile": """
Keywords: ["python", "remote", "contract"]
Location: USA
""",
        "output": {
            "match_score": 85,
            "personalized_message": "Matches porque: ✅ Python (skill exacto), ✅ Remote (como pediste), ✅ Contract (tu tipo favorito)",
            "telegram_message": """✅ Senior Python Developer
🏢 Acme Corp
📍 Remote | 💼 Contract
⭐ Score: 85/100

🤖 Matches porque: ✅ Python (skill exacto), ✅ Remote, ✅ Contract

🔗 [Ver en Indeed](https://indeed.com/jobs/123)""",
        },
    },
    {
        "job_info": """
Job: Java Developer - On-site
Company: OldCorp Inc
Remote: No
Type: Fulltime
Description: Looking for Java developer. On-site in New York office. Traditional enterprise environment.
""",
        "user_profile": """
Keywords: ["python", "remote", "contract"]
Location: USA
""",
        "output": {
            "match_score": 15,
            "personalized_message": "No matchea. Java ≠ Python, On-site ≠ Remote, Fulltime ≠ Contract",
            "telegram_message": """❌ Java Developer - On-site
🏢 OldCorp Inc
📍 On-site | 💼 Fulltime
⭐ Score: 15/100

🤖 No coincide con tu perfil. Buscas Python/Remote/Contract.

💡 Sugerencia: Intenta /perfil con keywords más específicos como 'Senior Python Developer' en lugar de solo 'python'

🔗 [Ver en Indeed](https://indeed.com/jobs/456)""",
        },
    },
]


# ============================================================================
# JOB MATCHER
# ============================================================================


class JobMatcher:
    """
    Agent que personaliza empleos usando LangChain + Gemini 2.5 Flash

    Usa:
    - FewShotPromptTemplate: Ejemplos estructurados para enseñar al LLM
    - with_structured_output(): Garantizar respuestas JSON válidas
    - PromptTemplate: Template reutilizable

    Propósito:
    - Analizar job contra keywords del usuario
    - Generar match score y mensaje personalizado
    - Devolver texto YA formateado en Markdown para Telegram

    Ejemplo:
        >>> matcher = JobMatcher()
        >>> job = Job(title="Senior Python Dev", company="Acme", ...)
        >>> result = matcher.match_job(job, ["python", "remote"], "USA")
        >>> print(result.match_score)  # 85
        >>> print(result.telegram_message)  # "✅ Senior Python Developer..."
    """

    def __init__(self):
        """Inicializar JobMatcher con Gemini 2.5 Flash + FewShotPromptTemplate"""
        try:
            # Inicializar modelo con structured output
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                temperature=0.3,  # Más bajo para mayor consistencia
            )

            # Crear structured model con Pydantic
            self.structured_llm = self.llm.with_structured_output(
                JobMatchResult,
                method="json_schema",  # Usar JSON Schema (recomendado para Gemini)
            )

            # Crear FewShotPromptTemplate
            self._setup_few_shot_template()

            logger.info("✅ JobMatcher inicializado con FewShotPromptTemplate + with_structured_output()")
        except Exception as e:
            logger.error(f"❌ Error inicializando JobMatcher: {e}")
            raise e

    def _setup_few_shot_template(self):
        """Configurar FewShotPromptTemplate con ejemplos estructurados"""

        # Template para formatear cada ejemplo
        example_prompt = PromptTemplate(
            input_variables=["job_info", "user_profile"],
            template="""JOB DETAILS:
{job_info}

USER PROFILE:
{user_profile}""",
        )

        # FewShotPromptTemplate que combina ejemplos + suffix
        self.few_shot_prompt = FewShotPromptTemplate(
            examples=EXAMPLES,
            example_prompt=example_prompt,
            suffix="""Ahora analiza este nuevo job:

JOB DETAILS:
{job_info}

USER PROFILE:
{user_profile}

Retorna JSON con 3 campos: match_score (0-100), personalized_message, telegram_message.
telegram_message DEBE estar formateado en Markdown con emojis, listo para enviar a Telegram.""",
            input_variables=["job_info", "user_profile"],
        )

    def match_job(
        self,
        job: Job,
        user_keywords: List[str],
        user_location: str,
    ) -> JobMatchResult:
        """
        Analizar un job y generar match score + mensaje personalizado

        Args:
            job: Job model con detalles del empleo
            user_keywords: Keywords que busca el usuario ["python", "remote"]
            user_location: País/ubicación del usuario "Colombia"

        Returns:
            JobMatchResult: {match_score, personalized_message, telegram_message}

        Raises:
            Exception: Si error en API de Gemini
        """
        try:
            # Construir información del job
            job_info = f"""
Job: {job.title}
Company: {job.company}
Remote: {'Yes' if job.is_remote else 'No'}
Type: {job.job_type or 'Unknown'}
Description: {job.description[:300] if job.description else 'No description'}..."""

            # Construir perfil del usuario
            user_profile = f"""
Keywords: {user_keywords}
Location: {user_location}"""

            # Llamar FewShotPromptTemplate
            prompt = self.few_shot_prompt.format(
                job_info=job_info,
                user_profile=user_profile,
            )

            logger.debug(f"Prompt:\n{prompt}")

            # Llamar modelo estructurado
            result = self.structured_llm.invoke(prompt)

            logger.info(
                f"✅ Job matched: {job.title} @ {job.company} (score: {result.match_score})"
            )
            # Agregar job object al resultado
            result.job = job
            return result

        except Exception as e:
            logger.error(f"❌ Error en JobMatcher: {e}")
            # Fallback: score bajo (con job object)
            return JobMatchResult(
                job=job,
                match_score=0,
                personalized_message="⚠️ Error analizando este job",
                telegram_message="⚠️ Error analizando este job. Intenta más tarde.",
            )

    def match_jobs_batch(
        self,
        jobs: List[Job],
        user_keywords: List[str],
        user_location: str,
    ) -> List[JobMatchResult]:
        """
        Analizar múltiples jobs (para TOP 3-5)

        Args:
            jobs: Lista de jobs a analizar
            user_keywords: Keywords del usuario
            user_location: Ubicación del usuario

        Returns:
            List[JobMatchResult]: Resultados para cada job
        """
        results = []
        for job in jobs:
            try:
                result = self.match_job(job, user_keywords, user_location)
                results.append(result)
            except Exception as e:
                logger.error(f"Error matching {job.title}: {e}")
                continue

        return results
