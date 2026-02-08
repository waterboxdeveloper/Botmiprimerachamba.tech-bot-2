#!/usr/bin/env python3
"""Test de filtros - Con LOGS DETALLADOS"""
import requests, json, time
from datetime import datetime

API_BASE_URL = "http://localhost:8000"
API_KEY = "test-key-12345"

def validate_filter(search_term, filters, filter_name):
    print(f"\n{'='*70}\n🔍 Test: {filter_name}\n📋 Parámetros: {json.dumps(filters, indent=2)}\n{'='*70}")
    url = f"{API_BASE_URL}/api/v1/search_jobs"
    headers = {"x-api-key": API_KEY}
    params = {"search_term": search_term, "results_wanted": 10, **filters}
    print(f"📤 Request: {json.dumps(params, indent=2)}\n")

    try:
        start = time.time()
        response = requests.get(url, headers=headers, params=params, timeout=30)
        elapsed = time.time() - start
        data = response.json()
        jobs = data.get('jobs', [])

        print(f"⏱️  Tiempo: {elapsed:.2f}s | 📊 Resultados: {len(jobs)} | 📈 Count: {data.get('count')} | 💾 Cached: {data.get('cached')}")
        print(f"🔍 Response keys: {list(data.keys())}")

        if not jobs:
            print(f"📄 Response: {json.dumps(data, indent=2)}")
        else:
            print(f"📄 Sample: {json.dumps(jobs[0], indent=2)[:300]}...")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    print(f"\n{'='*70}\n🚀 SUITE TESTS FILTROS - JobSpy API\nTimestamp: {datetime.now().isoformat()}\n{'='*70}")
    tests = [
        ("python", {"site_name": "indeed", "country_indeed": "USA", "is_remote": True}, "Indeed: Python Remote"),
        ("designer", {"site_name": "indeed", "country_indeed": "USA", "job_type": "contract"}, "Indeed: Designer Contract"),
        ("developer", {"site_name": "linkedin", "is_remote": True}, "LinkedIn: Developer Remote"),
        ("engineer", {"site_name": "indeed", "country_indeed": "Colombia", "job_type": "fulltime"}, "Indeed: Engineer Colombia"),
        ("python", {"site_name": "indeed", "country_indeed": "USA", "hours_old": 24}, "Indeed: Python 24h"),
        ("designer", {"site_name": "indeed", "country_indeed": "USA", "is_remote": True, "job_type": "contract"}, "Indeed: Designer Remote Contract"),
    ]
    for search_term, filters, test_name in tests:
        validate_filter(search_term, filters, test_name)
        time.sleep(1)
    print(f"\n{'='*70}\n✅ Tests completados\n{'='*70}\n")

if __name__ == "__main__":
    main()
