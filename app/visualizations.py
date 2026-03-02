"""
Generate performance charts and visualizations
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import func
from app.database import SessionLocal
from app.models import RequestMetric
import io
import base64

class MetricsVisualizer:
    """Generate charts from metrics data"""
    
    @staticmethod
    def generate_response_time_chart(hours: int = 1) -> str:
        """Generate response time over time chart"""
        db = SessionLocal()

        since = datetime.utcnow() - timedelta(hours=hours)
        metrics = db.query(RequestMetric).filter(
            RequestMetric.timestamp >= since
        ).order_by(RequestMetric.timestamp).all()
        
        db.close()
        
        if not metrics:
            return None

        df = pd.DataFrame([
            {
                'timestamp': m.timestamp,
                'response_time': m.response_time,
                'endpoint': m.endpoint
            }
            for m in metrics
        ])

        plt.figure(figsize=(12, 6))
        
        for endpoint in df['endpoint'].unique():
            endpoint_df = df[df['endpoint'] == endpoint]
            plt.plot(endpoint_df['timestamp'], endpoint_df['response_time'], 
                    label=endpoint, alpha=0.7, marker='o', markersize=3)
        
        plt.xlabel('Time')
        plt.ylabel('Response Time (ms)')
        plt.title(f'API Response Times - Last {hours} Hour(s)')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()

        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=100)
        img_buffer.seek(0)
        img_str = base64.b64encode(img_buffer.read()).decode()
        plt.close()
        
        return img_str
    
    @staticmethod
    def generate_status_code_chart(hours: int = 1) -> str:
        """Generate status code distribution chart"""
        db = SessionLocal()
        
        since = datetime.utcnow() - timedelta(hours=hours)

        status_counts = db.query(
            RequestMetric.status_code,
            func.count(RequestMetric.id).label('count')
        ).filter(
            RequestMetric.timestamp >= since
        ).group_by(RequestMetric.status_code).all()
        
        db.close()
        
        if not status_counts:
            return None

        plt.figure(figsize=(10, 6))
        
        labels = [f"{sc[0]}" for sc in status_counts]
        sizes = [sc[1] for sc in status_counts]
        colors = ['#28a745' if sc[0] < 300 else '#dc3545' if sc[0] >= 400 else '#ffc107' 
                 for sc in status_counts]
        
        plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        plt.title(f'HTTP Status Code Distribution - Last {hours} Hour(s)')
        plt.axis('equal')

        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=100)
        img_buffer.seek(0)
        img_str = base64.b64encode(img_buffer.read()).decode()
        plt.close()
        
        return img_str
    
    @staticmethod
    def generate_endpoint_performance_chart(hours: int = 1) -> str:
        """Generate average response time per endpoint"""
        db = SessionLocal()
        
        since = datetime.utcnow() - timedelta(hours=hours)

        endpoint_stats = db.query(
            RequestMetric.endpoint,
            func.avg(RequestMetric.response_time).label('avg_time'),
            func.count(RequestMetric.id).label('count')
        ).filter(
            RequestMetric.timestamp >= since
        ).group_by(RequestMetric.endpoint).all()
        
        db.close()
        
        if not endpoint_stats:
            return None

        plt.figure(figsize=(10, 6))
        
        endpoints = [e[0] for e in endpoint_stats]
        avg_times = [e[1] for e in endpoint_stats]
        counts = [e[2] for e in endpoint_stats]
        
        bars = plt.bar(endpoints, avg_times, color='#007bff', alpha=0.7)

        for bar, count in zip(bars, counts):
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'n={count}', ha='center', va='bottom', fontsize=9)
        
        plt.xlabel('Endpoint')
        plt.ylabel('Average Response Time (ms)')
        plt.title(f'Endpoint Performance - Last {hours} Hour(s)')
        plt.xticks(rotation=45, ha='right')
        plt.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()

        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=100)
        img_buffer.seek(0)
        img_str = base64.b64encode(img_buffer.read()).decode()
        plt.close()
        
        return img_str
