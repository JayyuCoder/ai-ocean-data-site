# Dashboard Update & Live Data Refresh Guide

## ✅ What Was Fixed

### Issues Found:
1. **Hardcoded Time Range** — Dashboard was stuck showing only "last 6 hours"
2. **No Dynamic Controls** — Couldn't change "Days to display" or refresh intervals
3. **Slow Scrape Interval** — Prometheus was collecting data every 15 seconds
4. **Static Dashboard** — Settings changed in UI weren't persistent

### Solutions Implemented:

#### 1. Prometheus Optimization ✓
**File**: `monitoring/prometheus.yml`
```yaml
# BEFORE: scrape_interval: 15s
# AFTER:
global:
  scrape_interval: 5s        # Data collected 3x faster
  evaluation_interval: 5s    # Alerts evaluated faster
```

**Impact**: Metrics now collected every 5 seconds (vs 15s)

#### 2. Grafana Dashboard Refresh ✓
**File**: `monitoring/grafana/dashboards/ocean-live.json` (NEW)
```json
{
  "dashboard": {
    "refresh": "5s",                    // Refreshes every 5 seconds
    "time": {"from": "now-7d", "to": "now"},  // Shows last 7 days by default
    "timepicker": {
      "refresh_intervals": [            // User can select:
        "5s", "10s", "30s",            //   - 5 seconds (live)
        "1m", "5m", "15m",             //   - 1-15 minutes
        "30m", "1h", "2h", "1d"        //   - 30m - 1 day (custom views)
      ]
    }
  }
}
```

**Impact**: Dashboard updates every 5 seconds with live data

---

## 📊 Dashboard Setup Guide

### Access Grafana:
```
URL: http://localhost:3000
Default Username: admin
Default Password: admin
```

### How to Change Time Range (Days to Display):

1. **Open Dashboard** → Click "AI Ocean Live Dashboard"
2. **Top Right Corner** → You'll see "Refresh interval" dropdown
3. **Click Time Picker** (shows current range like "Last 7 days")
4. **Select Custom Range:**
   - Quick options: 1h, 6h, 24h, 7d, 30d, 90d
   - Or click "Custom" for specific dates

**Example:**
```
• "1" = now-1h (last 1 hour - most granular/live)
• "90" = now-90d (last 90 days - full retroactive view)
• "7" = now-7d (last 7 days - default recommended)
```

### How to Change Refresh Interval:

1. **Top Left** → Dashboard title area
2. **Click Refresh Icon** (circular arrow) or **dropdown next to time picker**
3. **Select interval:**
   - `5s` — Live updates (most responsive)
   - `30s` — Balance (default REST APIs)
   - `1m` — Conservative (low bandwidth)
   - `off` — Manual refresh only

**Recommended Settings:**
```
For Live Monitoring:    refresh=5s,  timerange=now-1h
For Trend Analysis:     refresh=30s, timerange=now-7d
For Historical Review:  refresh=off, timerange=now-90d
```

---

## 🔍 How to Verify It's Working

### Check 1: Prometheus Scraping Metrics
```bash
# Should show data points collected every 5s
curl http://localhost:9090/api/v1/query?query=ocean_records_total | jq '.data.result'
```

Expected output:
```json
[{
  "metric": {
    "__name__": "ocean_records_total",
    "instance": "172.18.0.1:8002",
    "job": "ai_ocean_metrics"
  },
  "value": [1770491798, "35"]  // Timestamp should be recent (now)
}]
```

### Check 2: Metrics Being Exported
```bash
# Should show current values
curl http://localhost:8002/metrics | grep -E "^ocean_|^ai_pipeline"
```

Expected output:
```
ai_pipeline_runs_total 0.0
ai_pipeline_duration_seconds_count 0.0
ocean_avg_sst_celsius 28.3
ocean_avg_ph 8.09
ocean_avg_health_score 76.4
ocean_records_total 35.0
```

### Check 3: Grafana Datasource Connected
```bash
# Log into Grafana UI and go to:
# Settings (gear icon) → Data Sources → Prometheus
# Click "Test" → Should say "Data source is working"
```

### Check 4: Dashboard Updates
1. Open http://localhost:3000 → "AI Ocean Live Dashboard"
2. Look at **Total Records** stat (top right)
3. Watch it refresh every 5 seconds (timestamp changes)
4. If it's not updating → See Troubleshooting below

---

## 🐛 Troubleshooting

### Problem: Dashboard showing "No data"
**Solution:**
```bash
# 1. Check if Prometheus has data
curl http://localhost:9090/api/v1/query?query=ocean_records_total

# 2. If empty, check if metrics exporter is running
lsof -i :8002  # Should show python3 listening

# 3. Start metrics exporter if not running
cd AI-DATA-SITE
python3 monitoring/metrics_server.py
```

### Problem: Dashboard refresh interval not changing
**Solution:**
```bash
# 1. Force Grafana to reload fresh dashboard config
docker restart grafana

# 2. Clear browser cache (Cmd/Ctrl + Shift + R)

# 3. Check dashboard YAML was loaded
curl http://localhost:3000/api/v1/search?type=dash-db | jq '.[] | select(.title | contains("Ocean"))'
```

### Problem: Only seeing data from "6 hours ago"
**Solution:**
```bash
# This was the old dashboard with hardcoded time range
# Workaround: Manually select time picker in Grafana UI
# Permanent fix: Reload fresh dashboard

# Force reload: Settings → Dashboards → Provisioning → Reload
# Or restart Grafana:
docker restart grafana
```

### Problem: Metrics lag or update slowly
**Cause:** Prometheus scrape interval too slow
**Solution:** Already fixed! (changed from 15s → 5s)
```bash
# Verify Prometheus config
cat monitoring/prometheus.yml | grep scrape_interval
# Should show: scrape_interval: 5s

# If not updated, restart Prometheus:
docker restart prometheus
```

---

## 📈 Understanding the Dashboard

### Panels:

| Panel | Metric | Refresh | Notes |
|-------|--------|---------|-------|
| **Average SST (°C)** | `ocean_avg_sst_celsius` | 5s auto | Color-coded: Green <27, Yellow 29-29, Red >31 |
| **Average pH** | `ocean_avg_ph` | 5s auto | Healthy range: 8.0-8.2 |
| **Coral Health** | `ocean_avg_health_score` | 5s auto | % score, Green >80, Yellow 60-80, Red <60 |
| **Total Records** | `ocean_records_total` | 5s auto | Count of data points in DB |
| **SST Trend** | 7-day timeseries | 5s auto | Line chart (last 7 days) |
| **pH Trend** | 7-day timeseries | 5s auto | Line chart (last 7 days) |
| **Health Trend** | 7-day timeseries | 5s auto | Line chart (last 7 days) |

### How to Read Thresholds:

**Sea Surface Temperature:**
- 🟢 Green: 20-27°C (Healthy)
- 🟡 Yellow: 27-29°C (Warming)
- 🔴 Red: >29°C (Bleaching risk)

**pH Level:**
- 🟢 Green: 8.1-8.5 (Optimal)
- 🟡 Yellow: 8.0-8.1 (Acidifying)
- 🔴 Red: <8.0 (Dangerous)

**Coral Health Score:**
- 🟢 Green: >80% (Excellent)
- 🟡 Yellow: 60-80% (Fair)
- 🔴 Red: <60% (Poor)

---

## 🚀 Performance Tuning

### For Real-Time Monitoring (Fastest Updates):
```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 5s      # Collect every 5 seconds
  evaluation_interval: 5s

# Dashboard (in Grafana UI):
- Time Range: Last 1 hour (now-1h)
- Refresh: 5 seconds
```

### For Trend Analysis (Balanced):
```yaml
# monitoring/prometheus.yml  
global:
  scrape_interval: 15s     # Balanced approach
  evaluation_interval: 15s

# Dashboard (in Grafana UI):
- Time Range: Last 7 days (now-7d)
- Refresh: 30 seconds
```

### For Historical Review (Archive):
```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 60s     # Less frequent collection
  evaluation_interval: 60s

# Dashboard (in Grafana UI):
- Time Range: Last 90 days (now-90d)
- Refresh: Off (manual only)
```

---

## 📋 Configuration Files Changed

### 1. `monitoring/prometheus.yml`
- Changed `scrape_interval: 15s` → `5s`
- Added `evaluation_interval: 5s`

### 2. `monitoring/grafana/dashboards/ocean-live.json` (NEW)
- Updated refresh interval to `5s`
- Changed time range to `now-7d` (7 days)
- Added time picker with multiple options
- Added color thresholds to stat panels

### 3. Prometheus Container
- Restarted to apply new configuration
- Now collects metrics every 5 seconds

### 4. Grafana Container
- Restarted to load new dashboard
- Automatically provisions `ocean-live` dashboard from JSON file

---

## ✅ Verification Checklist

- [ ] Prometheus collecting data (5s interval confirmed)
- [ ] Grafana dashboard loads without errors
- [ ] Stats panels updating every 5 seconds
- [ ] Time picker allows selecting 1h, 6h, 24h, 7d, 30d, 90d
- [ ] Line charts show 7-day trend
- [ ] Colors reflect health status (green/yellow/red)
- [ ] Refresh interval dropdown working
- [ ] Manual dashboard refresh works (⟳ button)
- [ ] Historical data loads (try 90d range)
- [ ] No "No data" warnings

---

## 🔗 Related Documentation

- **Prometheus Queries**: See `/monitoring/alert_rules.yml`
- **Alerting Rules**: Check `/monitoring/README_ALERTS.md`
- **Backend API**: Visit http://localhost:8000/docs
- **Full Deployment Guide**: See `DEPLOYMENT_OPS_GUIDE.md`

---

**Last Updated**: 2026-02-07  
**Status**: ✅ Ready for Live Monitoring  
**Metrics Updated**: Every 5 seconds  
**Dashboard Refresh**: Configurable 5s - 1 day
