"""
Script sederhana buat test API endpoint.
Jalankan API dulu sebelum run script ini:
    cd api && uv run uvicorn main:app --port 8000

Lalu di terminal lain:
    python test_api.py
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"


def test_health():
    print("=== Test Health Check ===")
    resp = requests.get(f"{BASE_URL}/health")
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.json()}")
    print()
    return resp.status_code == 200


def test_predict_normal():
    print("=== Test Prediksi - Transaksi Normal ===")
    payload = {
        "transaction_amount": 14.09,
        "transaction_date": "2023-04-11T16:29:14",
        "transaction_type": "Debit",
        "channel": "ATM",
        "customer_age": 70,
        "customer_occupation": "Doctor",
        "transaction_duration": 81,
        "login_attempts": 1,
        "account_balance": 5112.21,
        "previous_transaction_date": "2024-11-04T08:08:08"
    }

    resp = requests.post(f"{BASE_URL}/predict", json=payload)
    data = resp.json()
    print(f"Status: {resp.status_code}")
    print(f"Anomaly: {data['is_anomaly']}")
    print(f"Score: {data['anomaly_score']}")
    print(f"Risk: {data['risk_level']}")
    print()
    return resp.status_code == 200


def test_predict_suspicious():
    print("=== Test Prediksi - Transaksi Suspicious ===")
    payload = {
        "transaction_amount": 9500.00,
        "transaction_date": "2023-04-11T02:15:00",
        "transaction_type": "Credit",
        "channel": "Online",
        "customer_age": 25,
        "customer_occupation": "Student",
        "transaction_duration": 5,
        "login_attempts": 7,
        "account_balance": 120.50,
        "previous_transaction_date": "2024-11-04T08:08:08"
    }

    resp = requests.post(f"{BASE_URL}/predict", json=payload)
    data = resp.json()
    print(f"Status: {resp.status_code}")
    print(f"Anomaly: {data['is_anomaly']}")
    print(f"Score: {data['anomaly_score']}")
    print(f"Risk: {data['risk_level']}")
    print(f"Factors: {data['contributing_factors']}")
    print()
    return resp.status_code == 200


def test_predict_missing_field():
    print("=== Test Prediksi - Missing Field (harusnya 422) ===")
    payload = {
        "transaction_amount": 100.0,
        # sengaja field lain ga diisi
    }

    resp = requests.post(f"{BASE_URL}/predict", json=payload)
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.json()}")
    print()
    return resp.status_code == 422


if __name__ == "__main__":
    print("Testing Fraud Detection API...\n")

    results = []
    results.append(("Health Check", test_health()))
    results.append(("Predict Normal", test_predict_normal()))
    results.append(("Predict Suspicious", test_predict_suspicious()))
    results.append(("Predict Missing Field", test_predict_missing_field()))

    print("=" * 40)
    print("HASIL:")
    for name, passed in results:
        status = "PASS" if passed else "FAIL"
        print(f"  {name}: {status}")

    all_passed = all(r[1] for r in results)
    print(f"\n{'Semua test passed.' if all_passed else 'Ada test yang gagal.'}")
