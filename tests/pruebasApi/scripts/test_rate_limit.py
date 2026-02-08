#!/usr/bin/env python3
"""
Test de Rate Limiting
Simula múltiples solicitudes para encontrar el límite
"""

import requests
import time
from datetime import datetime

API_BASE_URL = "http://localhost:8000"
API_KEY = "test-key-12345"

def test_rate_limit_burst():
    """
    Test 1: Hacer solicitudes rápidas en ráfaga
    """
    print("\n" + "="*60)
    print("📊 Test 1: Ráfaga de 20 solicitudes (sin espera)")
    print("="*60)

    url = f"{API_BASE_URL}/api/v1/search_jobs"
    headers = {"x-api-key": API_KEY}
    params = {"search_term": "python", "results_wanted": 5}

    results = {
        "200": 0,
        "429": 0,
        "other": 0
    }

    start_time = time.time()

    for i in range(20):
        try:
            response = requests.get(url, headers=headers, params=params, timeout=5)
            status = response.status_code

            if status == 200:
                results["200"] += 1
                print(f"✅ Req {i+1}: 200 OK")
            elif status == 429:
                results["429"] += 1
                print(f"⚠️  Req {i+1}: 429 RATE LIMITED")
            else:
                results["other"] += 1
                print(f"❌ Req {i+1}: {status}")

        except Exception as e:
            print(f"❌ Req {i+1}: Exception - {e}")

        time.sleep(0.05)  # Pequeña pausa

    elapsed = time.time() - start_time

    print(f"\n📈 Resultados:")
    print(f"   ✅ 200 OK: {results['200']}")
    print(f"   ⚠️  429 Rate Limited: {results['429']}")
    print(f"   ❌ Otros: {results['other']}")
    print(f"⏱️  Tiempo total: {elapsed:.2f}s")


def test_rate_limit_gradual():
    """
    Test 2: Hacer solicitudes con intervalos graduales
    """
    print("\n" + "="*60)
    print("📊 Test 2: Solicitudes con intervalos graduales")
    print("="*60)

    url = f"{API_BASE_URL}/api/v1/search_jobs"
    headers = {"x-api-key": API_KEY}
    params = {"search_term": "design", "results_wanted": 5}

    intervals = [0.5, 1, 2]  # segundos entre solicitudes
    results = {"200": 0, "429": 0, "other": 0}

    for interval in intervals:
        print(f"\n🔄 Prueba con intervalo de {interval}s entre solicitudes:")
        for i in range(5):
            try:
                start = time.time()
                response = requests.get(url, headers=headers, params=params, timeout=5)
                elapsed = time.time() - start

                if response.status_code == 200:
                    results["200"] += 1
                    print(f"   ✅ Req {i+1}: 200 ({elapsed:.2f}s)")
                elif response.status_code == 429:
                    results["429"] += 1
                    print(f"   ⚠️  Req {i+1}: 429 RATE LIMITED")
                else:
                    results["other"] += 1
                    print(f"   ❌ Req {i+1}: {response.status_code}")

            except Exception as e:
                print(f"   ❌ Req {i+1}: Exception - {str(e)[:50]}")

            time.sleep(interval)

    print(f"\n📈 Resultados totales:")
    print(f"   ✅ 200 OK: {results['200']}")
    print(f"   ⚠️  429 Rate Limited: {results['429']}")
    print(f"   ❌ Otros: {results['other']}")


def test_optimal_interval():
    """
    Test 3: Encontrar el intervalo óptimo
    (100 solicitudes en 3600 segundos = 1 solicitud cada 36 segundos)
    """
    print("\n" + "="*60)
    print("📊 Test 3: Intervalo óptimo (100 req/hora)")
    print("="*60)

    optimal_interval = 3600 / 100  # 36 segundos
    print(f"⏱️  Intervalo óptimo calculado: {optimal_interval:.2f} segundos")
    print(f"📌 Para ser seguro, usar 40-45 segundos entre solicitudes")

    print("\n💡 Recomendación para el bot:")
    print(f"   Si tienes N usuarios, espaciar búsquedas cada {optimal_interval * 2:.2f}s")


def main():
    """Ejecuta suite de tests de rate limiting"""

    print("\n" + "="*60)
    print("🚀 SUITE DE TESTS RATE LIMITING - JobSpy API")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Límite: 100 solicitudes / 3600 segundos")
    print("="*60)

    test_rate_limit_burst()
    time.sleep(2)

    test_rate_limit_gradual()
    time.sleep(2)

    test_optimal_interval()

    print("\n" + "="*60)
    print("✅ Tests completados")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
