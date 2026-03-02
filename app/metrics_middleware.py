from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import time
from app.database import SessionLocal
from app.models import RequestMetric
from datetime import datetime
import asyncio
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=3)

class MetricsMiddleware(BaseHTTPMiddleware):
    
    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith("/metrics") or request.url.path.startswith("/docs") or request.url.path.startswith("/openapi"):
            return await call_next(request)
        
        start_time = time.time()
        
        try:
            response = await call_next(request)
            response_time = (time.time() - start_time) * 1000
            
            asyncio.create_task(
                asyncio.get_event_loop().run_in_executor(
                    executor,
                    self._store_metric,
                    request.url.path,
                    request.method,
                    response.status_code,
                    response_time,
                    None
                )
            )
            
            return response
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            
            asyncio.create_task(
                asyncio.get_event_loop().run_in_executor(
                    executor,
                    self._store_metric,
                    request.url.path,
                    request.method,
                    500,
                    response_time,
                    str(e)
                )
            )
            raise
    
    def _store_metric(self, endpoint: str, method: str, status_code: int, 
                     response_time: float, error_message: str = None):
        try:
            db = SessionLocal()
            metric = RequestMetric(
                endpoint=endpoint,
                method=method,
                status_code=status_code,
                response_time=response_time,
                timestamp=datetime.utcnow(),
                error_message=error_message
            )
            db.add(metric)
            db.commit()
            db.close()
        except Exception as e:
            print(f"Failed to store metric: {e}")
