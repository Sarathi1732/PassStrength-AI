"""
API endpoint tests for PassStrength AI.
Tests all REST endpoints using FastAPI TestClient.
"""

import pytest


def test_health_endpoint(client):
    """GET /api/health should return 200 with status ok."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["version"] == "1.0.0"
    assert "model_loaded" in data


def test_analyze_endpoint(client):
    """POST /api/analyze with valid password returns full analysis."""
    response = client.post("/api/analyze", json={"password": "StrongPassword123!"})
    assert response.status_code == 200
    data = response.json()
    # Check all expected top-level fields
    assert "length" in data
    assert "uppercase_count" in data
    assert "lowercase_count" in data
    assert "digit_count" in data
    assert "special_count" in data
    assert "unique_char_ratio" in data
    assert "char_diversity" in data
    assert "shannon_entropy" in data
    assert "search_space_entropy" in data
    assert "complexity_score" in data
    assert "patterns" in data
    assert "crack_times" in data
    assert "ml_prediction" in data
    assert "feedback" in data
    assert "overall_strength" in data
    assert "overall_score" in data
    # Verify types
    assert data["length"] == len("StrongPassword123!")
    assert isinstance(data["shannon_entropy"], float)
    assert isinstance(data["ml_prediction"]["confidence"], float)


def test_analyze_empty_password(client):
    """POST /api/analyze with empty password returns 422 validation error."""
    response = client.post("/api/analyze", json={"password": ""})
    assert response.status_code == 422


def test_generate_endpoint(client):
    """POST /api/generate returns a password of requested length."""
    response = client.post("/api/generate", json={"length": 20})
    assert response.status_code == 200
    data = response.json()
    assert "password" in data
    assert len(data["password"]) == 20
    assert "entropy" in data
    assert "strength" in data


def test_predict_endpoint(client):
    """POST /api/predict returns ML prediction with expected fields."""
    response = client.post("/api/predict", json={"password": "Test1234!"})
    assert response.status_code == 200
    data = response.json()
    assert "strength_label" in data
    assert "strength_index" in data
    assert "confidence" in data
    assert "probabilities" in data
    assert data["strength_label"] in ["Very Weak", "Weak", "Medium", "Strong", "Very Strong"]


def test_model_info_endpoint(client):
    """GET /api/model-info returns model metadata or 404 if not trained."""
    response = client.get("/api/model-info")
    # Either 200 (model trained) or 404 (not yet trained) is acceptable
    assert response.status_code in [200, 404]
    if response.status_code == 200:
        data = response.json()
        assert "model_type" in data
        assert "accuracy" in data
        assert "feature_names" in data
