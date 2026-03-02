import requests
import time
import pytest
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"


def test_ping():
    """Test basic health check"""
    response = requests.get(f"{BASE_URL}/ping")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert "timestamp" in response.json()

def test_login_success():
    """Test successful authentication"""
    response = requests.post(
        f"{BASE_URL}/login",
        params={"username": "admin", "password": "password"}
    )
    assert response.status_code == 200
    assert "token" in response.json()

def test_login_fail():
    """Test failed authentication"""
    response = requests.post(
        f"{BASE_URL}/login",
        params={"username": "wrong", "password": "wrong"}
    )
    assert response.status_code == 401

def test_data():
    """Test data endpoint"""
    response = requests.get(f"{BASE_URL}/data")
    assert response.status_code == 200
    assert "data" in response.json()
    assert "timestamp" in response.json()
    assert isinstance(response.json()["data"], int)

def test_unstable():
    """Test unstable endpoint (may randomly fail)"""
    success_count = 0
    for _ in range(10):
        response = requests.get(f"{BASE_URL}/unstable")
        if response.status_code == 200:
            success_count += 1

    assert success_count > 0


def test_metrics_summary():
    """Test metrics summary endpoint"""
    requests.get(f"{BASE_URL}/ping")
    requests.get(f"{BASE_URL}/data")
    
    time.sleep(1)
    
    response = requests.get(f"{BASE_URL}/metrics/summary")
    assert response.status_code == 200
    data = response.json()
    assert "total_requests" in data
    assert "avg_response_time_ms" in data
    assert "success_rate" in data

def test_metrics_endpoints():
    """Test per-endpoint metrics"""
    requests.get(f"{BASE_URL}/ping")
    requests.get(f"{BASE_URL}/data")
    
    time.sleep(1)
    
    response = requests.get(f"{BASE_URL}/metrics/endpoints")
    assert response.status_code == 200
    data = response.json()
    assert "endpoints" in data
    assert isinstance(data["endpoints"], list)

def test_dashboard():
    """Test dashboard endpoint"""
    response = requests.get(f"{BASE_URL}/dashboard")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Performance Dashboard" in response.text


def test_fault_injection_enable():
    """Test enabling fault injection"""
    response = requests.post(
        f"{BASE_URL}/fault-injection/enable",
        params={"latency_ms": 500, "error_rate": 0.1}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "enabled"

def test_fault_injection_status():
    """Test fault injection status"""
    response = requests.get(f"{BASE_URL}/fault-injection/status")
    assert response.status_code == 200
    assert "enabled" in response.json()

def test_fault_injection_with_latency():
    """Test that fault injection adds latency"""
    requests.post(
        f"{BASE_URL}/fault-injection/enable",
        params={"latency_ms": 500, "error_rate": 0.0}
    )
    
    start = time.time()
    response = requests.get(f"{BASE_URL}/ping")
    duration = time.time() - start

    assert duration >= 0.5
    assert response.status_code == 200

    requests.post(f"{BASE_URL}/fault-injection/disable")

def test_fault_injection_disable():
    """Test disabling fault injection"""
    requests.post(f"{BASE_URL}/fault-injection/enable", params={"latency_ms": 100})
    
    response = requests.post(f"{BASE_URL}/fault-injection/disable")
    assert response.status_code == 200
    assert response.json()["status"] == "disabled"

    start = time.time()
    requests.get(f"{BASE_URL}/ping")
    duration = time.time() - start
    assert duration < 0.5

def test_fault_injection_logs():
    """Test fault injection logs"""
    requests.post(f"{BASE_URL}/fault-injection/enable", params={"latency_ms": 100})
    requests.post(f"{BASE_URL}/fault-injection/disable")
    
    response = requests.get(f"{BASE_URL}/fault-injection/logs")
    assert response.status_code == 200
    data = response.json()
    assert "logs" in data
    assert "total" in data


def test_response_time_under_load():
    """Test response times under moderate load"""
    response_times = []
    
    for _ in range(50):
        start = time.time()
        response = requests.get(f"{BASE_URL}/ping")
        duration = (time.time() - start) * 1000
        
        if response.status_code == 200:
            response_times.append(duration)
    
    avg_response_time = sum(response_times) / len(response_times)

    assert avg_response_time < 100
    assert len(response_times) == 50

def test_concurrent_requests():
    """Test handling concurrent requests"""
    import concurrent.futures
    
    def make_request():
        return requests.get(f"{BASE_URL}/ping")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(make_request) for _ in range(20)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]

    assert all(r.status_code == 200 for r in results)
    assert len(results) == 20


def test_health_check():
    """Test comprehensive health check"""
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "features" in data
    assert data["features"]["metrics_collection"] is True
    assert data["features"]["fault_injection"] is True


def test_invalid_endpoint():
    """Test 404 for invalid endpoints"""
    response = requests.get(f"{BASE_URL}/invalid-endpoint")
    assert response.status_code == 404

def test_invalid_login_parameters():
    """Test invalid login parameters"""
    response = requests.post(f"{BASE_URL}/login")
    assert response.status_code == 422


@pytest.fixture(autouse=True)
def cleanup():
    """Cleanup after each test"""
    yield
    try:
        requests.post(f"{BASE_URL}/fault-injection/disable", timeout=1)
    except:
        pass
