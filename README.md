# Banking Transaction Fraud Detection Analysis

Analysis of bank transaction data to identify suspicious patterns and potential fraud anomalies. This project includes exploratory data analysis, anomaly detection modeling, and productionized API inference.

## Dataset

Bank Transaction Dataset for Fraud Detection from Kaggle.
- Source: https://www.kaggle.com/datasets/valakhorasani/bank-transaction-dataset-for-fraud-detection
- 2,512 transactions with 16 attributes (amount, account info, device, channel, demographics, etc.)

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

### 2. Run notebooks

Open and run notebooks sequentially:
1. `notebooks/01_eda.ipynb` - EDA and data analysis
2. `notebooks/02_anomaly_detection.ipynb` - model training (output: model artifacts in `models/`)

### 3. Run API

```bash
cd api
uv sync
uv run uvicorn main:app --reload --port 8000
```

API docs automatically available at http://localhost:8000/docs

### 4. Docker (optional)

```bash
docker compose up --build
```

or manually:

```bash
docker build -t fraud-detection-api .
docker run -p 8000:8000 fraud-detection-api
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /health | Health check, verify model status |
| POST | /predict | Predict anomaly for a single transaction |

### Example request

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

### Example response

```json
{
  "is_anomaly": true,
  "anomaly_score": -0.1303,
  "risk_level": "medium",
  "contributing_factors": [
    "High login attempts (7x)",
    "High amount/balance ratio (78.19)",
    "Transaction at unusual hour (02:00)",
    "Large transaction amount (9,500.00)",
    "Very short transaction duration (5s)"
  ]
}
```

## Approach

### Q1: Exploratory Data Analysis
- Analysis of numerical and categorical variable distributions
- Correlation between features
- Identification of temporal patterns (hour, day)
- Outlier detection using IQR method
- Behavioral analysis per account (multi-device, multi-location)

### Q2: Anomaly Detection Model
- **Main model:** Isolation Forest (contamination=5%, n_estimators=200)
- **Validation:** Local Outlier Factor as comparison
- **Feature engineering:** 13 features (raw + temporal + derived + encoded)
- **Evaluation:** qualitative (anomaly vs normal profile, consensus analysis, threshold analysis)

### Q3: Productionized API
- FastAPI with Pydantic data model
- UV for package management
- Docker support
- Health check endpoint
- Contributing factors explanation per prediction

## Tech Stack

- Python 3.12+
- pandas, numpy, matplotlib, seaborn
- scikit-learn (Isolation Forest, LOF)
- FastAPI, Pydantic, uvicorn
- UV (package manager)
- Docker

</content>
