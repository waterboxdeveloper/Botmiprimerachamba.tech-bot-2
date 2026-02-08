#!/usr/bin/env python3
"""
Test básico de la API JobSpy
Prueba diferentes configuraciones de usuario:
- País (US, UK, Colombia, etc)
- Ubicación (Remote vs específica)
- Tipo de trabajo (fulltime vs contract/freelance)
"""

import requests
import json
import time
from datetime import datetime

API_BASE_URL = "http://localhost:8000"
API_KEY = "test-key-12345"

# Mapping de códigos ISO a nombres de países válidos en la API
COUNTRY_CODES = {
    "US": "USA",
    "UK": "UK",
    "CA": "Canada",
    "CO": "Colombia",
    "MX": "Mexico",
    "BR": "Brazil",
    "AR": "Argentina",
    "CL": "Chile",
    "DE": "Germany",
    "FR": "France",
    "IT": "Italy",
    "ES": "Spain",
    "AU": "Australia",
    "NZ": "New Zealand",
    "JP": "Japan",
    "CN": "China",
    "IN": "India",
    "SG": "Singapore",
    "HK": "Hong Kong",
    "KR": "South Korea",
    "TH": "Thailand",
    "NL": "Netherlands",
    "BE": "Belgium",
    "CH": "Switzerland",
    "AT": "Austria",
    "SE": "Sweden",
    "NO": "Norway",
    "DK": "Denmark",
    "FI": "Finland",
    "PL": "Poland",
    "CZ": "Czech Republic",
    "RO": "Romania",
    "GR": "Greece",
    "PT": "Portugal",
    "IE": "Ireland",
    "IL": "Israel",
    "AE": "United Arab Emirates",
    "SA": "Saudi Arabia",
    "EG": "Egypt",
    "NG": "Nigeria",
    "ZA": "South Africa",
}

def test_search(search_term: str, config: dict):
    """
    Ejecuta una búsqueda con configuración de usuario

    config esperada:
    {
        "site_name": "indeed",
        "country": "US",  # Para Indeed/Glassdoor
        "is_remote": True,
        "job_type": "contract",
        "results_wanted": 10
    }
    """

    site_name = config.get("site_name", "linkedin")
    country_code = config.get("country", "US")

    # Convertir código ISO a nombre de país completo
    country = COUNTRY_CODES.get(country_code, country_code)

    is_remote = config.get("is_remote", None)
    job_type = config.get("job_type", None)
    results_wanted = config.get("results_wanted", 10)

    # Construir descripción del test
    desc_parts = [f"'{search_term}'"]
    if is_remote:
        desc_parts.append("Remote")
    if job_type:
        desc_parts.append(f"({job_type})")
    if country:
        desc_parts.append(f"País: {country}")

    print(f"\n{'='*70}")
    print(f"🔍 Búsqueda: {' | '.join(desc_parts)}")
    print(f"   Sitio: {site_name}")
    print(f"{'='*70}")

    url = f"{API_BASE_URL}/api/v1/search_jobs"
    headers = {"x-api-key": API_KEY}

    # Construir parámetros
    params = {
        "search_term": search_term,
        "site_name": site_name,
        "results_wanted": results_wanted,
    }

    # Agregar country_indeed si es Indeed o Glassdoor
    if site_name in ["indeed", "glassdoor"]:
        params["country_indeed"] = country

    # Agregar filtros opcionales
    if is_remote is not None:
        params["is_remote"] = is_remote

    if job_type:
        params["job_type"] = job_type

    print(f"📋 Parámetros: {json.dumps(params, indent=2)}\n")

    # Medir tiempo
    start_time = time.time()
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        elapsed = time.time() - start_time

        print(f"⏱️  Tiempo de respuesta: {elapsed:.2f} segundos")
        print(f"📡 Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            jobs = data.get('jobs', [])  # Cambio: API usa 'jobs' no 'data'

            print(f"📊 Resultados encontrados: {len(jobs)}")
            print(f"✅ Status API: {data.get('status', 'N/A')}")

            # DEBUG: Mostrar respuesta completa si está disponible
            if 'count' in data:
                print(f"📈 Count total: {data.get('count')}")

            print(f"\n🔍 Response keys: {list(data.keys())}")
            print(f"📋 Raw response (primeros 500 chars): {str(data)[:500]}")

            if jobs:
                print(f"\n📄 Estructura del primer resultado:")
                first_job = jobs[0]

                # Mostrar solo campos importantes
                important_fields = {
                    "title": first_job.get("title"),
                    "company": first_job.get("company"),
                    "is_remote": first_job.get("is_remote"),
                    "job_type": first_job.get("job_type"),
                    "location": first_job.get("location"),
                    "salary": {
                        "min": first_job.get("min_amount"),
                        "max": first_job.get("max_amount"),
                        "currency": first_job.get("currency")
                    },
                    "date_posted": first_job.get("date_posted"),
                }
                print(json.dumps(important_fields, indent=2, ensure_ascii=False))

                # Contar campos completos
                print(f"\n🏷️  Campos principales disponibles:")
                key_fields = ["title", "company", "job_url", "is_remote", "job_type",
                             "min_amount", "max_amount", "location", "date_posted"]
                for field in key_fields:
                    status = "✅" if first_job.get(field) else "❌"
                    print(f"   {status} {field}")
            else:
                print("⚠️  No se encontraron resultados")
                print(f"📌 Posibles causas:")
                print(f"   1. Búsqueda muy específica o rara")
                print(f"   2. Filtros muy restrictivos (remote + contract)")
                print(f"   3. Sitio no tiene vacantes con esos criterios")
                print(f"   4. País/región sin datos disponibles")
                print(f"\n💡 Sugerencia: Intenta sin 'is_remote' o 'job_type'")

        else:
            print(f"❌ Error: {response.status_code}")
            error_msg = response.json().get("message", response.text[:200])
            print(f"Mensaje: {error_msg}")

    except Exception as e:
        print(f"❌ Excepción: {str(e)}")


def main():
    """Ejecuta suite de tests con diferentes configuraciones"""

    print("\n" + "="*70)
    print("🚀 SUITE DE TESTS - DIFERENTES CONFIGURACIONES DE USUARIO")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("="*70)

    # Simulamos diferentes perfiles de usuario
    user_configs = [
        # Usuario 1: Freelancer UX/UI Remote en USA
        {
            "name": "👤 Usuario 1: Freelancer UX/UI (USA, Remote, Contract)",
            "searches": [
                {
                    "term": "ux designer",
                    "config": {
                        "site_name": "indeed",
                        "country": "US",
                        "is_remote": True,
                        "job_type": "contract",
                        "results_wanted": 5
                    }
                },
                {
                    "term": "ui designer",
                    "config": {
                        "site_name": "linkedin",
                        "is_remote": True,
                        "job_type": "contract",
                        "results_wanted": 5
                    }
                }
            ]
        },
        # Usuario 2: Developer Python Colombia
        {
            "name": "👤 Usuario 2: Developer Python (Colombia, Full-time)",
            "searches": [
                {
                    "term": "python developer",
                    "config": {
                        "site_name": "indeed",
                        "country": "CO",  # Colombia
                        "results_wanted": 5
                    }
                }
            ]
        },
        # Usuario 3: Designer UK Remote
        {
            "name": "👤 Usuario 3: Designer (UK, Remote)",
            "searches": [
                {
                    "term": "graphic designer",
                    "config": {
                        "site_name": "glassdoor",
                        "country": "UK",
                        "is_remote": True,
                        "results_wanted": 5
                    }
                }
            ]
        }
    ]

    for user in user_configs:
        print(f"\n\n{'#'*70}")
        print(f"# {user['name']}")
        print(f"{'#'*70}")

        for search in user["searches"]:
            test_search(search["term"], search["config"])
            time.sleep(1)  # Pausa entre búsquedas

    print("\n\n" + "="*70)
    print("✅ Tests completados")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
