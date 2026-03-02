from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from datetime import datetime
from app.database import Base

class RequestMetric(Base):
    __tablename__ = "request_metrics"

    id = Column(Integer, primary_key=True, index=True)
    endpoint = Column(String, index=True)
    method = Column(String)
    status_code = Column(Integer)
    response_time = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    error_message = Column(String, nullable=True)
    
class LoadTestResult(Base):
    __tablename__ = "load_test_results"
    
    id = Column(Integer, primary_key=True, index=True)
    test_name = Column(String)
    total_requests = Column(Integer)
    failed_requests = Column(Integer)
    avg_response_time = Column(Float)
    min_response_time = Column(Float)
    max_response_time = Column(Float)
    requests_per_second = Column(Float)
    error_rate = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
    passed = Column(Boolean)

class FaultInjectionLog(Base):
    __tablename__ = "fault_injection_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    fault_type = Column(String)
    severity = Column(String)
    duration = Column(Float)
    affected_endpoints = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    description = Column(String)
