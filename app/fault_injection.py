import random
import time
import asyncio
from typing import Optional
from fastapi import HTTPException
from datetime import datetime
from app.database import SessionLocal
from app.models import FaultInjectionLog

class FaultInjector:
    
    def __init__(self):
        self.enabled = False
        self.latency_ms = 0
        self.error_rate = 0.0
        self.timeout_rate = 0.0
        
    def enable(self, latency_ms: int = 0, error_rate: float = 0.0, timeout_rate: float = 0.0):
        self.enabled = True
        self.latency_ms = latency_ms
        self.error_rate = error_rate
        self.timeout_rate = timeout_rate
        
        self._log_fault(
            fault_type="network_simulation",
            severity="medium" if latency_ms < 1000 else "high",
            description=f"Latency: {latency_ms}ms, Error rate: {error_rate*100}%, Timeout rate: {timeout_rate*100}%"
        )
        
    def disable(self):
        self.enabled = False
        self.latency_ms = 0
        self.error_rate = 0.0
        self.timeout_rate = 0.0
        
    async def inject(self, endpoint: str):
        if not self.enabled:
            return
            
        if self.latency_ms > 0:
            jitter = random.uniform(-0.2, 0.2) * self.latency_ms
            delay = (self.latency_ms + jitter) / 1000
            await asyncio.sleep(delay)
            
        if random.random() < self.error_rate:
            self._log_fault(
                fault_type="injected_error",
                severity="high",
                description=f"Random error injected on {endpoint}"
            )
            raise HTTPException(status_code=503, detail="Injected network error")
            
        if random.random() < self.timeout_rate:
            self._log_fault(
                fault_type="timeout",
                severity="high",
                description=f"Timeout injected on {endpoint}"
            )
            await asyncio.sleep(30)
            
    def _log_fault(self, fault_type: str, severity: str, description: str):
        try:
            db = SessionLocal()
            log = FaultInjectionLog(
                fault_type=fault_type,
                severity=severity,
                duration=0,
                affected_endpoints="all",
                timestamp=datetime.utcnow(),
                description=description
            )
            db.add(log)
            db.commit()
            db.close()
        except Exception as e:
            print(f"Failed to log fault injection: {e}")

fault_injector = FaultInjector()
