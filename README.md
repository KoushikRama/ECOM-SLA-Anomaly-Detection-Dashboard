# 🚨 E-Commerce SLA Anomaly Detection (Serverless ML System)

---

## 🎯 Goal

Detect **anomalies in hourly aggregated e-commerce SLA metrics**, including:

- Traffic spikes / drops  
- Latency degradation  
- Failure surges  

The system is designed to:

- Detect **both minor and major deviations**
- Provide **root cause analysis**
- Deliver **real-time inference via API**
- Visualize results using an interactive dashboard

---

## 📊 Problem Context

E-commerce systems generate high-volume SLA metrics such as:

- Success / failure request volume  
- Response time (latency)  

These are aggregated **hourly per operation**:

- browse_products  
- checkout  
- cart_update  

Anomalies may indicate:

- System degradation  
- Latency spikes  
- Failure surges  
- Traffic irregularities  

---

## 🏗️ Architecture Overview

"""
Synthetic Data → Feature Engineering → Model → Thresholding → Inference → API Gateway → Dashboard
"""

---

### ☁️ Cloud Architecture

"""
Streamlit UI
↓
API Gateway (REST API)
↓
SageMaker Endpoint (Serverless)
↓
ML Model (XGBoost)
"""

---

## 📁 Project Structure

"""
.
├── app.py # Streamlit UI
├── config/ # Config (API URL, constants)
├── core/
│ ├── pipeline.py # End-to-end pipeline
│ └── generate_test_data.py
├── services/
│ └── api_client.py # API calls
├── utils/ # Plotting & helpers
├── requirements.txt
"""


---

## ⚙️ Feature Engineering

### 🕒 Time Features

- `hour`
- `hour_sin`, `hour_cos`  
→ Captures cyclic hourly patterns

---

### 🎯 SLA Metrics

- `success_vol`
- `fail_vol`
- `success_rt_avg`
- `fail_rt_avg`

---

## 📡 API Format

### Request

```json
[
  {
    "timestamp": "2025-04-01 10:00:00",
    "operation": "checkout",
    "success_vol": 8000,
    "fail_vol": 300,
    "success_rt_avg": 150,
    "fail_rt_avg": 120
  }
]
```

### Response
```json
[
  {
    "operation": "checkout",
    "Status": "Anomaly",
    "Root_Cause": "success_vol",
    "Severity": 2.89,
    "Severity_Label": "🚨 Critical"
  }
]
```

--- 

## 🤖 Model (XGBoost Residual-Based)

### 🔍 Approach

- Train regression models for each SLA metric
- Predict expected values
- Compute residuals (actual vs predicted)
- Apply threshold-based anomaly detection

### ⚙️ Pipeline

"""
Features → XGBoost → Prediction → Residual → Threshold → Alert
"""

### 📈 Strengths

- Detects minor deviations precisely
- Provides root cause (metric-level)
- Interpretable outputs

### ⚠️ Limitations

- Requires threshold tuning
- Depends on consistent input schema

### 🔁 Thresholding Strategy

- Residual-based detection
- Combination of:
    - percentage deviation
    - absolute deviation

### 🧪 Data Simulation

Synthetic SLA data includes:
- Realistic traffic patterns (peak & off-peak)
- Load-based latency increases
- Failure rate correlation with load

### 🚨 Injected Anomalies

- Traffic spike
- Traffic drop
- Latency spike
- Failure spike

--- 

## 🚀 Running the Project

1️⃣ Clone Repository
git clone https://github.com/KoushikRama/ECOM-SLA-Anomaly-Detection-Dashboard.gitcd ECOM-SLA-Anomaly-Detection-Dashboard

2️⃣ Create Virtual Environment
python -m venv .venv.\.venv\Scripts\Activate.ps1

3️⃣ Install Dependencies
pip install -r requirements.txt

4️⃣ Run Streamlit App
streamlit run app.py

---

## 🌐 Deployment

**Frontend**

- Streamlit Cloud

**Backend**

- AWS API Gateway
- SageMaker Serverless Endpoint

---

## 📊 Dashboard Features

- 📈 SLA metric visualization
- 🚨 Anomaly detection display
- 🔍 Root cause identification
- 📊 Severity analysis

---

## 🧠 Key Capabilities

- Detect subtle SLA anomalies
- Provide metric-level root cause
- Enable interactive exploration
- Fully serverless ML inference

---

## 🚨 Known Issues

- Missing timestamp causes failure
- Cold start latency (~1–3 sec)
- Strict input schema required

---

## 🔮 Future Improvements

- Real-time streaming data
- Drift detection
- Auto threshold tuning
- Alerting system (Slack / Email)
- Hybrid anomaly models

---

## 💡 Summary
This project provides a production-ready anomaly detection system for SLA monitoring by combining:

- ML precision (XGBoost residual model)
- Cloud scalability (Serverless SageMaker)
- Interactive UI (Streamlit)

---

## 👨‍💻 Author
### Koushik Rama


