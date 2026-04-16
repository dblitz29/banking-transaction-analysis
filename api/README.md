# Fraud Detection API

FastAPI inference service untuk model anomaly detection transaksi bank.

## Setup

```bash
cd api
uv sync
```

## Menjalankan

```bash
uv run uvicorn main:app --reload --port 8000
```

API docs tersedia di http://localhost:8000/docs

## Endpoints

- `GET /health` - health check
- `POST /predict` - prediksi anomali untuk satu transaksi

## Contoh Request

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
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
  }'
```
