from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class TransactionInput(BaseModel):
    """Input schema untuk prediksi anomali transaksi."""

    transaction_amount: float = Field(..., gt=0, description="Nominal transaksi")
    transaction_date: datetime = Field(..., description="Waktu transaksi")
    transaction_type: str = Field(..., description="Tipe transaksi (Debit/Credit)")
    channel: str = Field(..., description="Channel transaksi (ATM/Online/Branch)")
    customer_age: int = Field(..., ge=0, le=120, description="Usia customer")
    customer_occupation: str = Field(..., description="Pekerjaan customer")
    transaction_duration: int = Field(..., ge=0, description="Durasi transaksi dalam detik")
    login_attempts: int = Field(..., ge=0, description="Jumlah percobaan login")
    account_balance: float = Field(..., ge=0, description="Saldo akun")
    previous_transaction_date: Optional[datetime] = Field(
        None, description="Waktu transaksi sebelumnya"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "transaction_amount": 14.09,
                    "transaction_date": "2023-04-11T16:29:14",
                    "transaction_type": "Debit",
                    "channel": "ATM",
                    "customer_age": 70,
                    "customer_occupation": "Doctor",
                    "transaction_duration": 81,
                    "login_attempts": 1,
                    "account_balance": 5112.21,
                    "previous_transaction_date": "2024-11-04T08:08:08",
                }
            ]
        }
    }


class PredictionResult(BaseModel):
    """Output schema untuk hasil prediksi."""

    is_anomaly: bool = Field(..., description="Apakah transaksi terdeteksi sebagai anomali")
    anomaly_score: float = Field(..., description="Skor anomali (semakin negatif = semakin anomalous)")
    risk_level: str = Field(..., description="Level risiko: low / medium / high")
    contributing_factors: list[str] = Field(
        default_factory=list,
        description="Faktor-faktor yang berkontribusi terhadap prediksi anomali",
    )


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
