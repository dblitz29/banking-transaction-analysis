from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
import joblib
import numpy as np
import pandas as pd
import os
from pathlib import Path

from schemas import TransactionInput, PredictionResult, HealthResponse

MODEL_DIR = Path(
    os.environ.get("MODEL_DIR", str(Path(__file__).parent.parent / "models"))
)


def load_artifacts():
    """Load semua model artifacts dari disk."""
    artifacts = {}
    try:
        artifacts["model"] = joblib.load(MODEL_DIR / "isolation_forest.joblib")
        artifacts["scaler"] = joblib.load(MODEL_DIR / "scaler.joblib")
        artifacts["le_channel"] = joblib.load(MODEL_DIR / "le_channel.joblib")
        artifacts["le_txntype"] = joblib.load(MODEL_DIR / "le_txntype.joblib")
        artifacts["le_occupation"] = joblib.load(MODEL_DIR / "le_occupation.joblib")
        artifacts["feature_cols"] = joblib.load(MODEL_DIR / "feature_cols.joblib")
    except FileNotFoundError as e:
        raise RuntimeError(
            f"Model artifacts not found di {MODEL_DIR}. "
            f"Jalankan notebook 02_anomaly_detection.ipynb dulu untuk generate model. "
            f"Detail: {e}"
        )
    return artifacts


app_state = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    app_state["artifacts"] = load_artifacts()
    yield
    # shutdown
    app_state.clear()


app = FastAPI(
    title="Fraud Detection API",
    description="API untuk mendeteksi anomali pada transaksi bank menggunakan Isolation Forest",
    version="0.1.0",
    lifespan=lifespan,
)


def build_features(txn: TransactionInput, artifacts: dict) -> np.ndarray:
    """Transform input transaksi menjadi feature vector untuk model."""

    le_channel = artifacts["le_channel"]
    le_txntype = artifacts["le_txntype"]
    le_occupation = artifacts["le_occupation"]
    scaler = artifacts["scaler"]
    feature_cols = artifacts["feature_cols"]

    txn_dt = txn.transaction_date
    prev_dt = txn.previous_transaction_date

    # hitung derived features
    txn_hour = txn_dt.hour
    txn_day_of_week = txn_dt.weekday()
    days_since_prev = (
        (txn_dt - prev_dt).total_seconds() / 86400 if prev_dt else 0.0
    )
    amount_to_balance_ratio = txn.transaction_amount / (txn.account_balance + 1)
    is_late_night = 1 if 0 <= txn_hour <= 5 else 0

    # encode categoricals, handle unseen labels gracefully
    try:
        channel_enc = le_channel.transform([txn.channel])[0]
    except ValueError:
        channel_enc = -1

    try:
        txntype_enc = le_txntype.transform([txn.transaction_type])[0]
    except ValueError:
        txntype_enc = -1

    try:
        occupation_enc = le_occupation.transform([txn.customer_occupation])[0]
    except ValueError:
        occupation_enc = -1

    features = {
        "TransactionAmount": txn.transaction_amount,
        "TransactionDuration": txn.transaction_duration,
        "LoginAttempts": txn.login_attempts,
        "AccountBalance": txn.account_balance,
        "CustomerAge": txn.customer_age,
        "TxnHour": txn_hour,
        "TxnDayOfWeek": txn_day_of_week,
        "DaysSincePrevTxn": days_since_prev,
        "AmountToBalanceRatio": amount_to_balance_ratio,
        "IsLateNight": is_late_night,
        "ChannelEncoded": channel_enc,
        "TxnTypeEncoded": txntype_enc,
        "OccupationEncoded": occupation_enc,
    }

    df = pd.DataFrame([features])[feature_cols]
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df.fillna(0, inplace=True)

    scaled = scaler.transform(df)
    return scaled


def get_risk_level(score: float) -> str:
    """Tentukan risk level berdasarkan anomaly score."""
    if score < -0.15:
        return "high"
    elif score < -0.05:
        return "medium"
    return "low"


def get_contributing_factors(txn: TransactionInput) -> list[str]:
    """Identifikasi faktor-faktor yang berkontribusi terhadap risiko."""
    factors = []

    if txn.login_attempts > 3:
        factors.append(f"Login attempts tinggi ({txn.login_attempts}x)")

    ratio = txn.transaction_amount / (txn.account_balance + 1)
    if ratio > 0.5:
        factors.append(f"Rasio amount/balance tinggi ({ratio:.2f})")

    hour = txn.transaction_date.hour
    if 0 <= hour <= 5:
        factors.append(f"Transaksi di jam tidak wajar ({hour:02d}:00)")

    if txn.transaction_amount > 5000:
        factors.append(f"Nominal transaksi besar ({txn.transaction_amount:,.2f})")

    if txn.transaction_duration < 10:
        factors.append(f"Durasi transaksi sangat singkat ({txn.transaction_duration}s)")

    return factors


@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="ok",
        model_loaded="artifacts" in app_state,
    )


@app.post("/predict", response_model=PredictionResult)
async def predict(txn: TransactionInput):
    if "artifacts" not in app_state:
        raise HTTPException(status_code=503, detail="Model belum loaded")

    artifacts = app_state["artifacts"]

    try:
        features = build_features(txn, artifacts)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Error saat memproses input: {e}")

    model = artifacts["model"]
    prediction = model.predict(features)[0]
    score = model.decision_function(features)[0]

    is_anomaly = prediction == -1
    risk_level = get_risk_level(score)
    factors = get_contributing_factors(txn) if is_anomaly else []

    return PredictionResult(
        is_anomaly=is_anomaly,
        anomaly_score=round(float(score), 4),
        risk_level=risk_level,
        contributing_factors=factors,
    )
