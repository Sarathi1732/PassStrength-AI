import pytest
from fastapi.testclient import TestClient
from app.services.password_analyzer import PasswordAnalyzer
from app.services.pattern_detector import PatternDetector
from app.services.password_generator import PasswordGenerator
from app.services.crack_time_estimator import CrackTimeEstimator

@pytest.fixture
def analyzer():
    return PasswordAnalyzer()

@pytest.fixture
def pattern_detector():
    return PatternDetector()

@pytest.fixture
def generator():
    return PasswordGenerator()

@pytest.fixture
def crack_estimator():
    return CrackTimeEstimator()

@pytest.fixture
def client():
    from main import app
    return TestClient(app)
