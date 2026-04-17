# Banking Transaction Fraud Detection Analysis

Analisis data transaksi bank untuk mengidentifikasi pola-pola mencurigakan dan anomali yang berpotensi fraud. Project ini mencakup exploratory data analysis, anomaly detection modeling, dan productionized API inference.

## Dataset

Bank Transaction Dataset for Fraud Detection dari Kaggle.
- Source: https://www.kaggle.com/datasets/valakhorasani/bank-transaction-dataset-for-fraud-detection
- 2,512 transaksi dengan 16 atribut (amount, account info, device, channel, demographics, dll)

## Project Structure

```
├── data/                   # raw dataset (not tracked in git)
├── notebooks/
│   ├── 01_eda.ipynb        # exploratory data analysis
│   └── 02_anomaly_detection.ipynb  # model training & evaluation
├── api/
│   ├── main.py             # FastAPI app
│   ├── schemas.py          # Pydantic models
│   └── pyproject.toml      # dependencies (managed by uv)
├── models/                 # saved model artifacts (generated from notebook)
├── docs/                   # slide deck content reference
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Quick Start

### 1. Setup environment

```bash
pip install -r requirements.txt
```

### 2. Jalankan notebooks

Buka dan run notebook secara berurutan:
1. `notebooks/01_eda.ipynb` - EDA dan analisis data
2. `notebooks/02_anomaly_detection.ipynb` - training model (output: model artifacts di `models/`)

### 3. Jalankan API

```bash
cd api
uv sync
uv run uvicorn main:app --reload --port 8000
```

API docs otomatis tersedia di http://localhost:8000/docs

### 4. Docker (opsional)

```bash
docker compose up --build
```

atau manual:

```bash
docker build -t fraud-detection-api .
docker run -p 8000:8000 fraud-detection-api
```

## API Endpoints

| Method | Endpoint | Deskripsi |
|--------|----------|-----------|
| GET | /health | Health check, cek status model |
| POST | /predict | Prediksi anomali untuk satu transaksi |

### Contoh request

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
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
  }'
```

### Contoh response

```json
{
  "is_anomaly": true,
  "anomaly_score": -0.1303,
  "risk_level": "medium",
  "contributing_factors": [
    "Login attempts tinggi (7x)",
    "Rasio amount/balance tinggi (78.19)",
    "Transaksi di jam tidak wajar (02:00)",
    "Nominal transaksi besar (9,500.00)",
    "Durasi transaksi sangat singkat (5s)"
  ]
}
```

## Approach

### Q1: Exploratory Data Analysis
- Analisis distribusi variabel numerik dan kategorikal
- Korelasi antar fitur
- Identifikasi pola temporal (jam, hari)
- Deteksi outlier menggunakan IQR method
- Analisis behavioral per account (multi-device, multi-location)

### Q2: Anomaly Detection Model
- **Model utama:** Isolation Forest (contamination=5%, n_estimators=200)
- **Validasi:** Local Outlier Factor sebagai pembanding
- **Feature engineering:** 13 fitur (raw + temporal + derived + encoded)
- **Evaluasi:** kualitatif (profil anomali vs normal, consensus analysis, threshold analysis)

### Q3: Productionized API
- FastAPI dengan Pydantic data model
- UV untuk package management
- Docker support
- Health check endpoint
- Contributing factors explanation per prediksi

## Tech Stack

- Python 3.12+
- pandas, numpy, matplotlib, seaborn
- scikit-learn (Isolation Forest, LOF)
- FastAPI, Pydantic, uvicorn
- UV (package manager)
- Docker
