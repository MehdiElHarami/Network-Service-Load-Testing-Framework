"""
Enhanced test report generator with metrics integration
Generates comprehensive HTML reports with:
- Test results
- Performance metrics
- Charts and visualizations
- Fault injection logs
"""
import pytest
import requests
import json
from datetime import datetime
from pathlib import Path

def generate_enhanced_report():
    """Generate enhanced HTML test report with metrics"""
    
    try:
        summary = requests.get("http://localhost:8000/metrics/summary").json()
        endpoints = requests.get("http://localhost:8000/metrics/endpoints").json()
        fault_logs = requests.get("http://localhost:8000/fault-injection/logs?limit=20").json()
    except Exception as e:
        print(f"Warning: Could not fetch metrics: {e}")
        summary = {}
        endpoints = {}
        fault_logs = {}
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            }}
            h1 {{
                color: #333;
                border-bottom: 3px solid #667eea;
                padding-bottom: 10px;
            }}
            h2 {{
                color: #555;
                margin-top: 30px;
                border-left: 4px solid #667eea;
                padding-left: 15px;
            }}
            .metric-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin: 20px 0;
            }}
            .metric-card {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                border-radius: 8px;
                text-align: center;
            }}
            .metric-value {{
                font-size: 36px;
                font-weight: bold;
                margin: 10px 0;
            }}
            .metric-label {{
                font-size: 14px;
                opacity: 0.9;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }}
            th, td {{
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }}
            th {{
                background-color: #667eea;
                color: white;
            }}
            tr:hover {{
                background-color: #f5f5f5;
            }}
            .status-success {{
                color: #28a745;
                font-weight: bold;
            }}
            .status-error {{
                color: #dc3545;
                font-weight: bold;
            }}
            .timestamp {{
                color: #666;
                font-size: 14px;
            }}
            .badge {{
                display: inline-block;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 12px;
                font-weight: bold;
            }}
            .badge-success {{
                background-color: #28a745;
                color: white;
            }}
            .badge-warning {{
                background-color: #ffc107;
                color: #333;
            }}
            .badge-danger {{
                background-color: #dc3545;
                color: white;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Network Service Test Report</h1>
            <div class="timestamp">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
            
            <h2>📊 Performance Metrics Summary</h2>
            <div class="metric-grid">
                <div class="metric-card">
                    <div class="metric-label">Total Requests</div>
                    <div class="metric-value">{summary.get('total_requests', 0)}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Success Rate</div>
                    <div class="metric-value">{summary.get('success_rate', 0)}%</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Avg Response Time</div>
                    <div class="metric-value">{summary.get('avg_response_time_ms', 0):.1f}ms</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Error Rate</div>
                    <div class="metric-value">{summary.get('error_rate', 0):.1f}%</div>
                </div>
            </div>
            
            <h2>⚡ Endpoint Performance</h2>
            <table>
                <thead>
                    <tr>
                        <th>Endpoint</th>
                        <th>Total Requests</th>
                        <th>Avg Response (ms)</th>
                        <th>Min/Max (ms)</th>
                        <th>Success Rate</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    for ep in endpoints.get('endpoints', []):
        success_rate = ep.get('success_rate', 0)
        status_class = 'success' if success_rate >= 95 else 'warning' if success_rate >= 80 else 'danger'
        
        html += f"""
                    <tr>
                        <td><strong>{ep.get('endpoint', 'N/A')}</strong></td>
                        <td>{ep.get('total_requests', 0)}</td>
                        <td>{ep.get('avg_response_time_ms', 0):.2f}</td>
                        <td>{ep.get('min_response_time_ms', 0):.2f} / {ep.get('max_response_time_ms', 0):.2f}</td>
                        <td>{success_rate:.1f}%</td>
                        <td><span class="badge badge-{status_class}">{status_class.upper()}</span></td>
                    </tr>
        """
    
    html += """
                </tbody>
            </table>
            
            <h2>💥 Fault Injection Events</h2>
            <table>
                <thead>
                    <tr>
                        <th>Type</th>
                        <th>Severity</th>
                        <th>Description</th>
                        <th>Timestamp</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    for log in fault_logs.get('logs', [])[:10]:
        severity = log.get('severity', 'low')
        badge_class = 'danger' if severity == 'high' else 'warning' if severity == 'medium' else 'success'
        
        html += f"""
                    <tr>
                        <td>{log.get('fault_type', 'N/A')}</td>
                        <td><span class="badge badge-{badge_class}">{severity.upper()}</span></td>
                        <td>{log.get('description', 'N/A')}</td>
                        <td>{log.get('timestamp', 'N/A')}</td>
                    </tr>
        """
    
    html += """
                </tbody>
            </table>
            
            <h2>🎯 Test Recommendations</h2>
            <ul>
    """
    
    if summary.get('error_rate', 0) > 5:
        html += "<li class='status-error'>⚠️ Error rate is above 5%. Investigate failing endpoints.</li>"
    else:
        html += "<li class='status-success'>✅ Error rate is within acceptable limits.</li>"
    
    if summary.get('avg_response_time_ms', 0) > 1000:
        html += "<li class='status-error'>⚠️ Average response time exceeds 1 second. Consider optimization.</li>"
    elif summary.get('avg_response_time_ms', 0) > 500:
        html += "<li>⚡ Response times could be improved. Monitor under load.</li>"
    else:
        html += "<li class='status-success'>✅ Response times are excellent.</li>"
    
    if summary.get('total_requests', 0) < 100:
        html += "<li>📊 Consider running more tests for better statistical significance.</li>"
    else:
        html += "<li class='status-success'>✅ Sufficient test coverage achieved.</li>"
    
    html += """
            </ul>
            
            <h2>📈 Visualizations</h2>
            <p>
                View detailed performance charts at:
                <a href="http://localhost:8000/dashboard" target="_blank">Performance Dashboard</a>
            </p>
            
            <h2>📝 Next Steps</h2>
            <ol>
                <li>Review failing endpoints and investigate root causes</li>
                <li>Run load tests to validate scalability</li>
                <li>Enable fault injection to test resilience</li>
                <li>Monitor metrics over extended periods</li>
                <li>Integrate with CI/CD pipeline</li>
            </ol>
            
            <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; text-align: center; color: #666;">
                <p><strong>Network Service Load & Reliability Testing Framework</strong></p>
                <p>
                    <a href="http://localhost:8000/docs" target="_blank">API Docs</a> |
                    <a href="http://localhost:8000/dashboard" target="_blank">Dashboard</a> |
                    <a href="http://localhost:8000/metrics/summary" target="_blank">Metrics API</a>
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    
    report_path = Path("enhanced_test_report.html")
    report_path.write_text(html, encoding='utf-8')
    
    print(f"✅ Enhanced report generated: {report_path.absolute()}")
    print(f"📊 Open in browser: file://{report_path.absolute()}")
    
    return str(report_path)


if __name__ == "__main__":
    print("Generating enhanced test report...")
    report_path = generate_enhanced_report()
    print(f"\n✨ Report saved to: {report_path}")
