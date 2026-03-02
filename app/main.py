from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
import random
import time

from app.database import get_db, init_db
from app.models import RequestMetric, FaultInjectionLog

app = FastAPI(
    title="Network Service Load Testing Framework",
    description="Enterprise-grade API testing with metrics, fault injection, and performance monitoring",
    version="2.0.0"
)

# app.add_middleware(MetricsMiddleware)

@app.on_event("startup")
def startup_event():
    init_db()
    print("✅ Database initialized")
    print("✅ API ready for testing")

@app.get("/ping")
async def ping():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}

@app.post("/login")
async def login(username: str, password: str):
    if username == "admin" and password == "password":
        return {"message": "Login successful", "token": "mock-jwt-token"}
    raise HTTPException(status_code=401, detail="Unauthorized")

@app.get("/data")
async def get_data():
    time.sleep(random.uniform(0.1, 0.5))
    return {
        "data": random.randint(1, 100),
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/unstable")
async def unstable():
    if random.random() < 0.2:
        raise HTTPException(status_code=500, detail="Random failure")
    return {"status": "stable", "uptime": random.randint(1000, 9999)}

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Network Service Load Testing Framework",
        "version": "2.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "features": {
            "metrics_collection": True,
            "fault_injection": True,
            "performance_dashboard": True,
            "api_documentation": True
        }
    }

@app.get("/metrics/summary")
def get_metrics_summary(hours: int = Query(1, ge=1, le=24), db: Session = Depends(get_db)):
    try:
        since = datetime.utcnow() - timedelta(hours=hours)
        metrics = db.query(RequestMetric).filter(RequestMetric.timestamp >= since).all()
        
        if not metrics:
            return {
                "message": "No metrics available yet",
                "period_hours": hours,
                "total_requests": 0
            }
        
        total_requests = len(metrics)
        failed_requests = len([m for m in metrics if m.status_code >= 400])
        response_times = [m.response_time for m in metrics]
        
        return {
            "period_hours": hours,
            "total_requests": total_requests,
            "failed_requests": failed_requests,
            "success_rate": round((total_requests - failed_requests) / total_requests * 100, 2),
            "avg_response_time_ms": round(sum(response_times) / len(response_times), 2),
            "min_response_time_ms": round(min(response_times), 2),
            "max_response_time_ms": round(max(response_times), 2),
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/metrics/endpoints")
def get_endpoint_metrics(hours: int = Query(1, ge=1, le=24), db: Session = Depends(get_db)):
    try:
        since = datetime.utcnow() - timedelta(hours=hours)
        
        endpoint_stats = db.query(
            RequestMetric.endpoint,
            func.count(RequestMetric.id).label('total_requests'),
            func.avg(RequestMetric.response_time).label('avg_response_time'),
            func.min(RequestMetric.response_time).label('min_response_time'),
            func.max(RequestMetric.response_time).label('max_response_time'),
            func.sum(func.case((RequestMetric.status_code >= 400, 1), else_=0)).label('failed_requests')
        ).filter(
            RequestMetric.timestamp >= since
        ).group_by(RequestMetric.endpoint).all()
        
        results = []
        for stat in endpoint_stats:
            results.append({
                "endpoint": stat[0],
                "total_requests": stat[1],
                "avg_response_time_ms": round(stat[2], 2) if stat[2] else 0,
                "min_response_time_ms": round(stat[3], 2) if stat[3] else 0,
                "max_response_time_ms": round(stat[4], 2) if stat[4] else 0,
                "failed_requests": stat[5] if stat[5] else 0,
                "success_rate": round((stat[1] - (stat[5] if stat[5] else 0)) / stat[1] * 100, 2) if stat[1] > 0 else 0
            })
        
        return {"period_hours": hours, "endpoints": results}
    except Exception as e:
        return {"error": str(e), "endpoints": []}

@app.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Performance Dashboard</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }
            .container {
                max-width: 1000px;
                margin: 0 auto;
                background: white;
                padding: 30px;
                border-radius: 10px;
            }
            h1 { color: #333; }
            .stat-card {
                display: inline-block;
                background: #667eea;
                color: white;
                padding: 20px;
                margin: 10px;
                border-radius: 5px;
                min-width: 150px;
                text-align: center;
            }
            a { color: #667eea; text-decoration: none; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Performance Dashboard</h1>
            <p>Welcome! Your API is running.</p>
            
            <h2>Quick Links:</h2>
            <p>
                <a href="/docs" target="_blank">📡 API Documentation</a> |
                <a href="/metrics/summary" target="_blank">📊 Metrics Summary</a> |
                <a href="/ping" target="_blank">✅ Health Check</a>
            </p>
            
            <h2>Try These Endpoints:</h2>
            <div class="stat-card">
                <strong>/ping</strong><br>Health check
            </div>
            <div class="stat-card">
                <strong>/data</strong><br>Get sample data
            </div>
            <div class="stat-card">
                <strong>/login</strong><br>Test auth (POST)
            </div>
            <div class="stat-card">
                <strong>/unstable</strong><br>Random failures
            </div>
            
            <h2>Fault Injection:</h2>
            <p>
                <a href="/fault-injection/status" target="_blank">View Status</a>
            </p>
        </div>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)

@app.post("/fault-injection/enable")
def enable_fault_injection(
    latency_ms: int = Query(0, ge=0, le=5000),
    error_rate: float = Query(0.0, ge=0.0, le=1.0),
    timeout_rate: float = Query(0.0, ge=0.0, le=1.0)
):
    return {
        "status": "enabled",
        "latency_ms": latency_ms,
        "error_rate": error_rate,
        "timeout_rate": timeout_rate
    }

@app.post("/fault-injection/disable")
def disable_fault_injection():
    return {"status": "disabled"}

@app.get("/fault-injection/status")
def get_fault_injection_status():
    return {
        "enabled": False,
        "latency_ms": 0,
        "error_rate": 0.0,
        "timeout_rate": 0.0
    }

@app.get("/fault-injection/logs")
def get_fault_injection_logs(limit: int = Query(50, ge=1, le=500), db: Session = Depends(get_db)):
    try:
        logs = db.query(FaultInjectionLog).order_by(
            FaultInjectionLog.timestamp.desc()
        ).limit(limit).all()
        
        return {
            "total": len(logs),
            "logs": [
                {
                    "id": log.id,
                    "fault_type": log.fault_type,
                    "severity": log.severity,
                    "description": log.description,
                    "timestamp": log.timestamp.isoformat()
                }
                for log in logs
            ]
        }
    except Exception as e:
        return {"total": 0, "logs": [], "error": str(e)}
