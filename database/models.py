"""
Modelos Pydantic para validación de datos
Usuario y Job matching con rainmanjam/jobspy-api output
Diseñados para trabajar con Google Sheets como database
"""

from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional, List
from datetime import datetime


class User(BaseModel):
    """
    Modelo de Usuario
    Almacenado en Google Sheets (Sheet: "Usuarios")
    Cada fila es un usuario
    """
    telegram_id: str = Field(..., min_length=1, description="ID único del usuario en Telegram")
    name: str = Field(..., min_length=1, description="Nombre del usuario")
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    keywords: List[str] = Field(
        default_factory=list,
        description="Palabras clave que el usuario busca (ej: ['ux/ui', 'design system'])"
    )
    location_preference: Optional[str] = None
    experience_level: str = Field(
        default="mid",
        description="Nivel de experiencia: junior, mid, senior"
    )
    is_active: bool = Field(default=True, description="Si el usuario está activo")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @field_validator('experience_level')
    @classmethod
    def validate_experience_level(cls, v):
        """Validar que experience_level sea uno de los valores permitidos"""
        valid_levels = ['junior', 'mid', 'senior']
        if v not in valid_levels:
            raise ValueError(f'experience_level debe ser uno de {valid_levels}, recibido: {v}')
        return v

    @field_validator('telegram_id')
    @classmethod
    def validate_telegram_id(cls, v):
        """Validar que telegram_id no esté vacío"""
        if not v or not v.strip():
            raise ValueError('telegram_id no puede estar vacío')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "telegram_id": "123456789",
                "name": "Juan Pérez",
                "email": "juan@example.com",
                "keywords": ["ux designer", "ui designer", "remote"],
                "location_preference": "Remote",
                "experience_level": "senior"
            }
        }


class JobLocation(BaseModel):
    """Ubicación del trabajo"""
    country: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None


class SalaryRange(BaseModel):
    """Rango salarial"""
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
    currency: Optional[str] = None
    interval: Optional[str] = None  # hourly, monthly, yearly


class Job(BaseModel):
    """
    Modelo de Trabajo
    Estructura que devuelve rainmanjam/jobspy-api
    Almacenado en Google Sheets (Sheet: "Vacantes")
    Cada fila es un trabajo
    """
    id: Optional[str] = None  # ID único del trabajo (puede no existir en algunos casos)
    title: str
    company: Optional[str] = None  # Algunos jobs no tienen empresa (ej: Indeed)
    company_url: Optional[str] = None
    job_url: str
    location: Optional[JobLocation] = None
    is_remote: Optional[bool] = False
    description: Optional[str] = None
    job_type: Optional[str] = None  # fulltime, parttime, contract, internship
    job_function: Optional[str] = None
    job_level: Optional[str] = None  # entry, mid, senior
    salary: Optional[SalaryRange] = None
    company_industry: Optional[str] = None
    date_posted: Optional[str] = None
    emails: Optional[List[str]] = None

    # Metadatos del bot
    source: Optional[str] = None  # linkedin, indeed, glassdoor, etc
    scraped_at: Optional[datetime] = None
    sent_to: Optional[List[str]] = Field(
        default_factory=list,
        description="Lista de telegram_ids que ya recibieron este trabajo"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Senior UX Designer",
                "company": "Acme Corp",
                "job_url": "https://linkedin.com/jobs/123",
                "is_remote": True,
                "job_type": "contract",
                "location": {
                    "country": "USA",
                    "city": "San Francisco",
                    "state": "CA"
                },
                "source": "linkedin"
            }
        }


class JobMatch(BaseModel):
    """
    Trabajo con análisis de match personalizad
    Lo que se envía al usuario por Telegram
    """
    job: Job
    match_score: float = Field(..., ge=0, le=100, description="Score de 0-100")
    personalized_message: str = Field(
        ...,
        description="Mensaje personalizado generado por Gemini"
    )
    matched_keywords: List[str] = Field(
        default_factory=list,
        description="Keywords del usuario que matchean con el job"
    )
