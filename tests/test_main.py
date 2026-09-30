from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "BMI Calculator" in response.text

def test_calculate_metric_normal():
    response = client.post("/api/calculate", json={
        "weight": 70.0,
        "height": 175.0,
        "unit": "metric"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["bmi"] == 22.9
    assert data["category"] == "Normal weight"

def test_calculate_imperial_overweight():
    response = client.post("/api/calculate", json={
        "weight": 180.0,
        "height": 70.0,
        "unit": "imperial"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["bmi"] == 25.8
    assert data["category"] == "Overweight"

def test_invalid_unit():
    response = client.post("/api/calculate", json={
        "weight": 70.0,
        "height": 175.0,
        "unit": "invalid"
    })
    assert response.status_code == 400

def test_zero_height():
    response = client.post("/api/calculate", json={
        "weight": 70.0,
        "height": 0.0,
        "unit": "metric"
    })
    assert response.status_code == 422 # Pydantic validation error for gt=0
