#!/usr/bin/env python3
"""
Test de Múltiples Usuarios
Simula búsquedas reales del bot
"""

import requests
import json
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

API_BASE_URL = "http://localhost:8000"
API_KEY = "test-key-12345"

# Datos de usuarios simulados
USERS = {
    "juan": {
        "keywords": ["ux designer", "ui designer", "product designer"],
        "remote": True,
        "job_type": "contract"
    },
    "ana": {
        "keywords": ["python", "backend developer", "django"],
        "remote": True,
        "job_type": "fulltime"
    },
    "carlos": {
        "keywords": ["react", "frontend", "javascript"],
        "remote": False,
        "job_type": "fulltime"
    },
    "maria": {
        "keywords": ["data scientist", "machine learning", "python"],
        "remote": True,
        "job_type": None
    },
    "pedro": {
        "keywords": ["devops", "kubernetes", "aws"],
        "remote": True,
        "job_type": None
    }
}


def search_for_user(username: str, keywords: list, remote: bool, job_type: str):
    """
    Busca vacantes para un usuario
    Retorna cantidad de resultados y tiempo
    """
    results_per_keyword = {}
    total_results = 0
    total_time = 0

    print(f"\n👤 Buscando para {username}:")

    for keyword in keywords:
        url = f"{API_BASE_URL}/api/v1/search_jobs"
        headers = {"x-api-key": API_KEY}

        params = {
            "search_term": keyword,
            "results_wanted": 10,
            "is_remote": remote,
        }

        if job_type:
            params["job_type"] = job_type

        try:
            start = time.time()
            response = requests.get(url, headers=headers, params=params, timeout=30)
            elapsed = time.time() - start
            total_time += elapsed

            if response.status_code == 200:
                data = response.json()
                count = len(data.get('data', []))
                results_per_keyword[keyword] = count
                total_results += count

                print(f"   ✅ '{keyword}': {count} resultados ({elapsed:.2f}s)")

            else:
                print(f"   ❌ '{keyword}': Error {response.status_code}")

        except Exception as e:
            print(f"   ❌ '{keyword}': {str(e)[:50]}")

        time.sleep(0.5)  # Pequeña pausa entre keywords

    return {
        "username": username,
        "total_keywords": len(keywords),
        "results_per_keyword": results_per_keyword,
        "total_results": total_results,
        "total_time": total_time,
        "avg_time_per_keyword": total_time / len(keywords) if keywords else 0
    }


def test_sequential():
    """
    Test 1: Búsquedas secuenciales (una tras otra)
    """
    print("\n" + "="*60)
    print("📊 Test 1: Búsquedas Secuenciales (Un usuario a la vez)")
    print("="*60)

    start_time = time.time()
    results = []

    for username, user_config in USERS.items():
        result = search_for_user(
            username,
            user_config["keywords"],
            user_config["remote"],
            user_config.get("job_type")
        )
        results.append(result)
        time.sleep(1)  # Pausa entre usuarios

    elapsed = time.time() - start_time

    print(f"\n📈 Resumen Secuencial:")
    for result in results:
        print(f"   {result['username']}: {result['total_results']} resultados ({result['total_time']:.2f}s)")

    total_results = sum(r['total_results'] for r in results)
    print(f"\n✅ Total: {total_results} resultados en {elapsed:.2f}s")

    return results, elapsed


def test_parallel():
    """
    Test 2: Búsquedas paralelas (usando ThreadPoolExecutor)
    NOTA: Cuidado con rate limiting
    """
    print("\n" + "="*60)
    print("📊 Test 2: Búsquedas Paralelas (Múltiples usuarios simultáneamente)")
    print("="*60)
    print("⚠️  CUIDADO: Esto puede activar rate limiting\n")

    start_time = time.time()

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {}

        for username, user_config in USERS.items():
            future = executor.submit(
                search_for_user,
                username,
                user_config["keywords"],
                user_config["remote"],
                user_config.get("job_type")
            )
            futures[future] = username

        results = []
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            print(f"   ✅ {result['username']}: {result['total_results']} resultados")

    elapsed = time.time() - start_time

    print(f"\n📈 Resumen Paralelo:")
    total_results = sum(r['total_results'] for r in results)
    print(f"   Total: {total_results} resultados en {elapsed:.2f}s")

    return results, elapsed


def test_simulation_daily():
    """
    Test 3: Simulación de ejecución diaria
    """
    print("\n" + "="*60)
    print("📊 Test 3: Simulación de Ejecución Diaria")
    print("="*60)
    print(f"Usuarios: {len(USERS)}")
    print(f"Total keywords: {sum(len(u['keywords']) for u in USERS.values())}")

    total_keywords = sum(len(u['keywords']) for u in USERS.values())
    total_users = len(USERS)

    print(f"\n📋 Estadísticas teóricas:")
    print(f"   Total búsquedas por ejecución: {total_keywords}")
    print(f"   Rate limit: 100 solicitudes/hora")
    print(f"   Búsquedas/hora: {total_keywords}")

    if total_keywords <= 100:
        print(f"   ✅ Cabe en rate limit (1 ejecución/hora)")
    else:
        executions_per_hour = 100 / total_keywords
        print(f"   ⚠️  Necesita {1/executions_per_hour:.1f}h entre ejecuciones")

    # Simulación
    print(f"\n🔄 Simulación (1 ronda de búsquedas):")
    results, elapsed = test_sequential()

    if len(USERS) > 0 and elapsed > 0:
        searches_per_hour = (total_keywords / elapsed) * 3600
        print(f"\n📊 Velocidad actual: {searches_per_hour:.1f} búsquedas/hora")


def main():
    """Ejecuta suite de tests múltiples"""

    print("\n" + "="*60)
    print("🚀 SUITE DE TESTS MÚLTIPLES - Simulación Real del Bot")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("="*60)

    # Test 1: Secuencial
    results_seq, time_seq = test_sequential()

    # Pausa
    print(f"\n⏱️  Pausa de 5s antes del siguiente test...")
    time.sleep(5)

    # Test 3: Simulación diaria
    test_simulation_daily()

    print("\n" + "="*60)
    print("✅ Tests completados")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
