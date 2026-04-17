# Slide Deck: Bank Transaction Fraud Detection Analysis

---

## Slide 1: Title

**Bank Transaction Fraud Detection**
Technical Assessment

Prima Fadhil Sulistyo
Repo: github.com/dblitz29/banking-transaction-analysis

---

## Slide 2: Dataset Overview

**Bank Transaction Dataset for Fraud Detection (Kaggle)**

- 2,512 transaksi, 16 atribut
- Atribut mencakup: transaction amount, account info, device/merchant ID, channel, customer demographics
- Tidak ada label fraud eksplisit -> pendekatan unsupervised
- Tidak ditemukan missing values maupun duplikat

---

## Slide 3: EDA - Distribusi Data

**Temuan distribusi:**

- TransactionAmount: right-skewed, mayoritas transaksi bernilai kecil
- CustomerAge: tersebar merata (19-70 tahun)
- LoginAttempts: mayoritas 1x, tapi ada outlier dengan attempts tinggi
- TransactionDuration: bervariasi luas (10-300+ detik)
- AccountBalance: range lebar, ada konsentrasi di saldo rendah-menengah

[Screenshot: histogram distribusi dari notebook 01_eda.ipynb, cell "Distribusi Variabel Numerik"]
[Screenshot: boxplot dari notebook 01_eda.ipynb]

---

## Slide 4: EDA - Korelasi dan Pola Temporal

**Korelasi:**

- Tidak ada korelasi kuat antar variabel numerik (semua < 0.1)
- Ini menandakan fitur-fitur cukup independen, baik untuk modeling

**Pola temporal:**

- Transaksi tersebar merata di semua jam dan hari
- Sebagian kecil transaksi terjadi di jam 00:00-05:59 (dini hari)

[Screenshot: correlation heatmap dari notebook 01_eda.ipynb]
[Screenshot: bar chart jam transaksi dari notebook 01_eda.ipynb]

---

## Slide 5: EDA - Identifikasi Pola Anomali

**Pola yang diwaspadai:**

- Beberapa transaksi punya rasio amount/balance sangat tinggi (spending > saldo)
- Account dengan multiple device atau lokasi berbeda -> potensi account takeover
- Transaksi dini hari dengan amount tinggi
- Login attempts > 3 -> potensi brute force

[Screenshot: tabel top 10 rasio amount/balance dari notebook 01_eda.ipynb]

---

## Slide 6: Feature Engineering

**13 fitur yang digunakan untuk modeling:**

| Kategori | Fitur |
|----------|-------|
| Raw | TransactionAmount, TransactionDuration, LoginAttempts, AccountBalance, CustomerAge |
| Temporal | TxnHour, TxnDayOfWeek, DaysSincePrevTxn |
| Derived | AmountToBalanceRatio, IsLateNight |
| Encoded | ChannelEncoded, TxnTypeEncoded, OccupationEncoded |

Semua fitur di-scale menggunakan StandardScaler.

---

## Slide 7: Model - Isolation Forest

**Kenapa Isolation Forest?**

- Cocok untuk unsupervised anomaly detection tanpa label
- Bekerja dengan prinsip: anomali lebih mudah diisolasi
- Scalable dan efisien untuk data transaksional

**Parameter:**
- n_estimators=200, contamination=0.05, random_state=42

**Hasil:** ~5% transaksi terdeteksi sebagai anomali

[Screenshot: distribusi anomaly score dari notebook 02]

---

## Slide 8: Model - Validasi dengan LOF

**Cross-validation menggunakan Local Outlier Factor:**

- LOF juga mendeteksi ~5% anomali
- Ada overlap (consensus) antara kedua model
- Transaksi yang di-flag oleh kedua model lebih likely anomali

**Profil anomali vs normal:**
- Anomali cenderung punya amount lebih tinggi, login attempts lebih banyak, dan durasi yang lebih ekstrem

[Screenshot: perbandingan profil anomali vs normal dari notebook 02]
[Screenshot: feature importance correlation chart dari notebook 02]

---

## Slide 9: Model - Thresholding dan Evaluasi

**Threshold analysis:**

| Percentile | Transaksi ter-flag |
|------------|-------------------|
| 1% | ~25 transaksi (high confidence) |
| 3% | ~75 transaksi |
| 5% | ~126 transaksi (default) |
| 10% | ~251 transaksi (aggressive) |

**Evaluasi:**
- Tanpa ground truth label, evaluasi dilakukan secara kualitatif
- Profil anomali konsisten dengan pola fraud yang umum
- Threshold bisa disesuaikan dengan risk appetite bisnis

---

## Slide 10: API - Productionized Inference

**Tech stack:**
- FastAPI + Pydantic data model
- UV untuk package management
- Docker support

**Endpoints:**
- GET /health -> health check
- POST /predict -> prediksi anomali per transaksi

**Response contoh (transaksi suspicious):**
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

---

## Slide 11: Arsitektur dan Deployment

```
[Client] -> [FastAPI] -> [Isolation Forest Model]
                |
                v
         [Model Artifacts]
         - isolation_forest.joblib
         - scaler.joblib
         - label_encoders.joblib
```

**Deployment options:**
- Local: uv run uvicorn main:app --port 8000
- Docker: docker build -t fraud-api . && docker run -p 8000:8000 fraud-api

---

## Slide 12: Kesimpulan dan Rekomendasi

**Apa yang sudah dilakukan:**
1. EDA menyeluruh dengan temuan yang actionable
2. Anomaly detection model (Isolation Forest + LOF validation)
3. Production-ready API dengan FastAPI + Docker

**Rekomendasi ke depan:**
- Kumpulkan label fraud dari investigasi manual untuk supervised learning
- Tambahkan real-time monitoring dan alerting
- Implementasi A/B testing untuk threshold tuning
- Tambah fitur behavioral (velocity check, geo-distance, dll)
