# Banking Transaction Fraud Detection Analysis

Analysis of bank transaction data to identify suspicious and anomalous patterns, build anomaly detection models, and serve predictions via a REST API.

## Dataset

Bank Transaction Dataset for Fraud Detection from Kaggle.
Source: https://www.kaggle.com/datasets/valakhorasani/bank-transaction-dataset-for-fraud-detection

## Project Structure

```
├── data/                   # raw dataset
├── notebooks/              # jupyter notebooks for EDA and modeling
├── api/                    # FastAPI inference service
├── models/                 # saved model artifacts
└── requirements.txt
```

## Setup

```bash
pip install -r requirements.txt
```

## Docker

```bash
docker build -t fraud-detection-api .
docker run -p 8000:8000 fraud-detection-api
```

API docs: http://localhost:8000/docs
