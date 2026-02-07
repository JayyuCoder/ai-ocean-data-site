# AI Ocean Data Site

Real-time coral reef health monitoring using AI, NOAA data, and machine learning.

## 🏗️ Architecture

```
NOAA CRW API ──┐
               ├──► Data Ingestion (6 AM)
Allen Coral ───┤
               └──► Data Pipeline
                    │
                    ├──► Cleaning + Transformation
                    ├──► PostGIS Spatial Merge
                    └──► ML Pipeline
                         ├── LSTM Forecasting
                         └── Anomaly Detection
                         │
                         └──► PostgreSQL + PostGIS
                              │
                              ├──► FastAPI Backend
                              └──► Streamlit Dashboard
```

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.10+
- PostgreSQL + PostGIS

### Installation

1. **Clone & Setup**
```bash
cd AI-DATA-SITE
pip install -r requirements.txt
```

2. **Configure Environment**
```bash
cp .env.example .env
# Edit .env with your credentials
```

3. **Docker Deployment**
```bash
docker-compose up -d
```

This starts:
- PostgreSQL + PostGIS on port 5432
- FastAPI Backend on port 8000
- Scheduler service (6 AM daily)

4. **Frontend Dashboard**
```bash
streamlit run frontend/app.py
```

Access at `http://localhost:8501`

## 🛠️ Lightweight Scheduler & Services

This repo includes a lightweight scheduler that will run the pipeline daily.

To start all services (backend, frontend, scheduler) in background:

```bash
./scripts/run_services.sh
```

If you don't want the full TensorFlow/Postgres pipeline, the scheduler will automatically prefer the `run_pipeline_light.py` runner which uses only local SQLite and lighter deps.

## 🚢 Local Monitoring with Docker Compose

To run Prometheus + Grafana locally (provisioned to scrape the app and metrics server):

```bash
cd deploy
docker-compose -f docker-compose-grafana.yml up -d
```

Grafana: http://localhost:3000 (admin/admin)
Prometheus: http://localhost:9090

The Grafana dashboard is pre-provisioned and will appear after Grafana starts.

## ⚙️ Automated Kubernetes Deploy

To enable automated deploys to your Kubernetes cluster, set a repository secret `KUBE_CONFIG` containing your kubeconfig file base64-encoded.

Then pushes to `main` will trigger `.github/workflows/deploy-to-k8s.yml` which applies manifests under `deploy/k8s/`.


## 📊 Project Structure

```
AI-DATA-SITE/
├── pipeline/              # Data fetching & processing
│   ├── fetch_noaa.py      # NOAA CRW API (SST, pH, DHW)
│   ├── fetch_allen.py     # Allen Coral Atlas
│   ├── clean_transform.py # Data cleaning
│   ├── merge_data.py      # PostGIS spatial merge
│   └── run_pipeline.py    # Master orchestrator
│
├── ml/                    # Machine Learning
│   └── model.py           # LSTM + Anomaly Detection
│
├── backend/               # FastAPI API
│   ├── main.py            # API endpoints
│   ├── database.py        # PostgreSQL connection
│   └── models.py          # SQLAlchemy ORM models
│
├── frontend/              # Streamlit Dashboard
│   └── app.py             # Interactive visualization
│
├── scheduler/             # Daily Pipeline Trigger
│   └── scheduler.py       # 6 AM APScheduler
│
├── Dockerfile             # Container image
├── docker-compose.yml     # Multi-service orchestration
└── requirements.txt       # Python dependencies
```

## 🔌 API Endpoints

### GET /
Health check & service info

### GET /health
Server status

### GET /data/latest
Latest ocean metrics

### GET /data/timeseries?days=30
Historical time-series data

### GET /data/anomalies
Detected anomalies

### GET /stats
Aggregate statistics

## 📈 ML Models

### 1. Health Score
```
score = reef_baseline - (SST × 1.5 + DHW × 5)
```

### 2. LSTM Forecasting
- **Input**: 30-day time window
- **Output**: 7-day pH/SST forecast
- **Architecture**: 64→32 LSTM layers + Dense

### 3. Anomaly Detection
- **Algorithm**: Isolation Forest
- **Contamination**: 10%
- **Input**: SST/pH series

## ☁️ Cloud Deployment

### AWS
```
EC2 (Docker) → RDS (PostgreSQL+PostGIS)
EventBridge (6 AM trigger) → Lambda (Pipeline)
S3 (NOAA files)
CloudWatch (Monitoring)
```

### Azure
```
AKS (Kubernetes) → Azure PostgreSQL
Azure Data Factory (Scheduler)
Blob Storage (Data lake)
Application Insights (Monitoring)
```

## 📝 IEEE Project Report Structure

1. **Abstract** - Brief overview of system & results
2. **Introduction** - Problem statement, motivation
3. **Related Work** - Similar projects, literature review
4. **Data Sources**
   - NOAA Coral Reef Watch (SST, DHW)
   - Allen Coral Atlas (Reef shapes)
   - Global Ocean Acidification Network (pH)
5. **System Architecture** - Pipeline diagram, components
6. **Data Pipeline**
   - Ingestion, cleaning, transformation
   - PostGIS spatial merging
7. **ML Models**
   - LSTM architecture & training
   - Anomaly detection methodology
8. **Experimental Results**
   - Model accuracy, precision, recall
   - Forecast validation
9. **Dashboard Visualization**
   - Real-time monitoring
   - Interactive maps
10. **Conclusion & Future Work**

### Keywords
Ocean Health Monitoring, Coral Bleaching, LSTM, PostGIS, NOAA CRW, Machine Learning, Real-time AI Dashboard, Time-Series Forecasting

## 🔧 Configuration

### Database Schema
```sql
CREATE TABLE ocean_metrics (
  id SERIAL PRIMARY KEY,
  date DATE,
  latitude FLOAT,
  longitude FLOAT,
  sst FLOAT,
  dhw FLOAT,
  ph FLOAT,
  health_score FLOAT,
  anomaly BOOLEAN,
  forecast_ph FLOAT
);
```

### PostGIS Spatial Tables
```sql
CREATE TABLE coral_reefs (
  id SERIAL PRIMARY KEY,
  reef_type TEXT,
  geom GEOMETRY(POLYGON, 4326)
);
```

## 📊 Dashboard Features

- **📍 Real-time Map**: Interactive Pydeck visualization
- **📈 Time-Series Charts**: SST, pH, Health trends
- **⚠️ Anomaly Detection**: Highlighted warnings
- **📊 Statistics**: Aggregate metrics & KPIs
- **🎯 Predictions**: 7-day forecasts

## 🛠️ Development

### Running Locally
```bash
# Terminal 1: Backend
uvicorn backend.main:app --reload

# Terminal 2: Scheduler
python scheduler/scheduler.py

# Terminal 3: Frontend
streamlit run frontend/app.py
```

### Testing Pipeline
```bash
python pipeline/run_pipeline.py
```

## 📜 License

MIT

## 👥 Contributors

AI Ocean Data Team

---

🌊 **Real-time Coral Reef Health Monitoring with AI**
