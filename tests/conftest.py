"""
Configuración de pytest y fixtures compartidas
"""

import pytest
from database.models import User, Job, JobLocation


@pytest.fixture
def sample_user():
    """Usuario de prueba"""
    return User(
        telegram_id="123456789",
        name="Juan Test",
        email="juan@test.com",
        keywords=["ux designer", "ui designer"],
        location_preference="Remote",
        experience_level="senior"
    )


@pytest.fixture
def sample_job():
    """Trabajo de prueba (similar a respuesta de JobSpy API)"""
    return Job(
        title="Senior UX Designer",
        company="Tech Corp",
        job_url="https://linkedin.com/jobs/123",
        location=JobLocation(
            country="USA",
            city="San Francisco",
            state="CA"
        ),
        is_remote=True,
        job_type="contract",
        description="We are looking for a senior UX designer...",
        source="linkedin"
    )


@pytest.fixture
def multiple_jobs():
    """Múltiples trabajos de prueba"""
    jobs = []
    titles = [
        "Senior UX Designer",
        "UI Designer - Remote",
        "Product Designer",
        "Frontend Engineer",
        "Data Scientist"
    ]
    for i, title in enumerate(titles):
        job = Job(
            title=title,
            company=f"Company {i}",
            job_url=f"https://example.com/job/{i}",
            is_remote=i % 2 == 0,
            job_type="contract" if i % 2 == 0 else "fulltime",
            source="indeed"
        )
        jobs.append(job)
    return jobs
