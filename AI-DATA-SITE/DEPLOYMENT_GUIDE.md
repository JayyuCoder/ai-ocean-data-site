# 🚀 FINAL DEPLOYMENT & RUN GUIDE

## Quick Start (3 Steps)

### Step 1: Start Services
```bash
docker-compose up -d
```

This launches:
- ✅ PostgreSQL + PostGIS (port 5432)
- ✅ FastAPI Backend (port 8000)  
- ✅ APScheduler (6 AM daily execution)

Verify:
```bash
docker-compose ps
docker logs ocean_api
docker logs ocean_db
```

### Step 2: Initialize Database
```bash
# Option A: Docker exec
docker exec ocean_api python -c "from backend.database import init_db; init_db()"

# Option B: Direct Python
python -c "from backend.database import init_db; init_db()"
```

### Step 3: Launch Dashboard
```bash
streamlit run frontend/app.py
```

Access:
- 🌊 Dashboard: `http://localhost:8501`
- 📡 API Docs: `http://localhost:8000/docs`
- 📊 API: `http://localhost:8000`

---

## Manual Pipeline Execution (Testing)

```bash
# Run pipeline immediately (don't wait for 6 AM)
python pipeline/run_pipeline.py
```

Output:
```
Step 1: Fetching NOAA CRW data...
Step 2: Fetching Allen Coral Atlas...
Step 3: Cleaning data...
Step 4: Integrating pH data...
Step 5: Spatial merge with coral reefs...
Step 6: Running ML predictions...
Step 7: Storing to PostgreSQL...
✅ Pipeline completed successfully!
```

---

## Scheduler Configuration

The scheduler is pre-configured to run daily at **6:00 AM IST** (Asia/Kolkata timezone).

To change timing, edit `scheduler/scheduler.py`:
```python
scheduler.add_job(
    run_daily_pipeline,
    trigger="cron",
    hour=6,        # Change to desired hour (0-23)
    minute=0       # Change to desired minute (0-59)
)
```

---

## Data Pipeline Verification

### 1. Check Database Connection
```bash
docker exec ocean_db psql -U ocean_user -d ocean_db -c "\dt"
```

### 2. Verify Tables
```bash
docker exec ocean_db psql -U ocean_user -d ocean_db -c "SELECT COUNT(*) FROM ocean_metrics;"
```

### 3. Check Latest Data
```bash
curl http://localhost:8000/data/latest
```

### 4. Test API
```bash
# Get statistics
curl http://localhost:8000/stats

# Get time-series (last 7 days)
curl "http://localhost:8000/data/timeseries?days=7"

# Get anomalies
curl http://localhost:8000/data/anomalies
```

---

## Cloud Deployment (AWS Example)

### AWS Architecture
```
EC2 (Docker Host)
   ├── FastAPI Container (port 8000)
   ├── Scheduler Container (6 AM trigger)
   └── PostgreSQL RDS (PostGIS enabled)

EventBridge Rule: "6 AM UTC"
   └── Lambda → EC2 Restart Pipeline

S3 Bucket: ocean-data-noaa
   └── Store downloaded NOAA NetCDF files

CloudWatch: Logs & Monitoring
   └── Alert on anomalies
```

### AWS Deployment Commands
```bash
# 1. Push to ECR
aws ecr get-login-password | docker login --username AWS --password-stdin <ECR_URL>
docker tag ai-ocean-data:latest <ECR_URL>/ai-ocean:latest
docker push <ECR_URL>/ai-ocean:latest

# 2. Create RDS PostgreSQL with PostGIS
aws rds create-db-instance \
  --db-instance-identifier ocean-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --engine-version 15.2 \
  --allocated-storage 100

# 3. Enable PostGIS
# (Done in RDS parameter group - enable pg_extensions)

# 4. Deploy to ECS/EC2
# (Use CloudFormation or CDK)
```

---

## Azure Deployment (Alternative)

### Azure Architecture
```
AKS Cluster
   ├── FastAPI Pod
   ├── Scheduler Pod
   └── PostgreSQL Flexible Server

Azure Data Factory: Scheduler
   └── 6 AM UTC Pipeline

Blob Storage: NOAA Data Lake

Application Insights: Monitoring
```

---

## Monitoring & Logging

### Docker Logs
```bash
# API logs
docker logs -f ocean_api

# Scheduler logs
docker logs -f ocean_scheduler

# Database logs
docker logs -f ocean_db
```

### PostgreSQL Monitoring
```bash
docker exec ocean_db psql -U ocean_user -d ocean_db -c "
SELECT 
  COUNT(*) as total_records,
  COUNT(CASE WHEN anomaly=true THEN 1 END) as anomalies,
  AVG(sst) as avg_sst,
  AVG(ph) as avg_ph,
  AVG(health_score) as avg_health
FROM ocean_metrics;
"
```

### Real-time Dashboard Monitoring
Dashboard automatically refreshes and shows:
- ✅ Latest metrics
- ✅ Trend charts
- ✅ Anomaly alerts
- ✅ Health scores

---

## Troubleshooting

### Issue: Database Connection Failed
```bash
# Check if PostgreSQL is running
docker ps | grep ocean_db

# Reset database
docker-compose down
docker volume rm ai-data-site_postgres_data
docker-compose up -d
```

### Issue: NOAA Files Not Found
```bash
# Ensure files exist in working directory
ls -la *.nc

# Or download from NOAA:
# https://coralreefwatch.noaa.gov/product/5km/index.php
```

### Issue: API Returns 500 Error
```bash
# Check API logs
docker logs ocean_api

# Verify database initialization
docker exec ocean_api python backend/database.py
```

### Issue: Streamlit Won't Connect to API
```bash
# Verify API is running
curl http://localhost:8000/health

# Check firewall/ports
netstat -an | grep 8000
```

---

## Performance Optimization

### Database Indexing
```sql
CREATE INDEX idx_date ON ocean_metrics(date);
CREATE INDEX idx_location ON ocean_metrics(latitude, longitude);
CREATE INDEX idx_anomaly ON ocean_metrics(anomaly);
```

### Query Optimization
```python
# Use pagination for large datasets
@app.get("/data/timeseries")
async def get_timeseries(skip: int = 0, limit: int = 1000):
    return db.query(OceanMetrics).offset(skip).limit(limit).all()
```

---

## Security Checklist

- [ ] Change default PostgreSQL password in `.env`
- [ ] Use environment variables for API keys
- [ ] Enable HTTPS in production
- [ ] Set up firewall rules for database
- [ ] Enable authentication on FastAPI
- [ ] Use secrets manager for credentials
- [ ] Enable API rate limiting
- [ ] Set up VPN for database access

---

## Maintenance Schedule

- **Daily**: Monitor anomaly alerts
- **Weekly**: Check data quality metrics
- **Monthly**: Validate model accuracy
- **Quarterly**: Retrain LSTM models
- **Annually**: Full system audit

