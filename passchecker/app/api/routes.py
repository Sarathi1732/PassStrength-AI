"""
API routes for PassStrength AI.

Provides endpoints for password analysis, prediction, generation,
health check, and model information.
"""

import json
import os
from fastapi import APIRouter, HTTPException
from app.models.schemas import (
    PasswordAnalysisRequest,
    PasswordGenerateRequest,
    PasswordAnalysisResponse,
    PasswordGenerateResponse,
    HealthResponse,
    ModelInfoResponse,
    MLPrediction,
    PatternResult,
    CrackTimeResult,
    FeedbackItem,
)

from app.services.password_analyzer import PasswordAnalyzer
from app.services.pattern_detector import PatternDetector
from app.services.crack_time_estimator import CrackTimeEstimator
from app.services.feedback_engine import FeedbackEngine
from app.services.password_generator import PasswordGenerator
from app.ml.predictor import PasswordPredictor

router = APIRouter(prefix="/api", tags=["Password Analysis"])


@router.post("/analyze", response_model=PasswordAnalysisResponse)
async def analyze_password(request: PasswordAnalysisRequest):
    """Full password analysis: metrics, patterns, crack time, ML prediction, feedback."""
    pwd = request.password.strip()

    analyzer = PasswordAnalyzer()
    analysis = analyzer.analyze(pwd)

    detector = PatternDetector()
    patterns_raw = detector.detect_all(pwd)

    estimator = CrackTimeEstimator()
    crack_raw = estimator.estimate(pwd)

    predictor = PasswordPredictor()
    prediction_raw = predictor.predict(pwd)

    engine = FeedbackEngine()
    feedback_raw = engine.generate_feedback(analysis, patterns_raw)

    # Build pattern result
    has_patterns = any(
        len(v) > 0
        for v in [
            patterns_raw.get("sequential", []),
            patterns_raw.get("repeated", []),
            patterns_raw.get("keyboard_walks", []),
            patterns_raw.get("dictionary_words", []),
            patterns_raw.get("leetspeak", []),
        ]
    )
    patterns = PatternResult(
        sequential=patterns_raw.get("sequential", []),
        repeated=patterns_raw.get("repeated", []),
        keyboard_walks=patterns_raw.get("keyboard_walks", []),
        dictionary_words=patterns_raw.get("dictionary_words", []),
        leetspeak=patterns_raw.get("leetspeak", []),
        has_patterns=has_patterns,
    )

    # Map crack time keys to schema fields
    crack_times = CrackTimeResult(
        online_1k=crack_raw.get("1K_guesses_per_sec", "N/A"),
        fast_online_1m=crack_raw.get("1M_guesses_per_sec", "N/A"),
        offline_100m=crack_raw.get("100M_guesses_per_sec", "N/A"),
        massive_10b=crack_raw.get("10B_guesses_per_sec", "N/A"),
    )

    # ML prediction
    ml_prediction = MLPrediction(
        strength_label=prediction_raw["strength_label"],
        strength_index=prediction_raw["strength_index"],
        confidence=prediction_raw["confidence"],
        probabilities=prediction_raw["probabilities"],
    )

    # Feedback items
    feedback = [
        FeedbackItem(
            type=f.get("type", "info"),
            message=f.get("message", ""),
            priority=f.get("priority", "low"),
        )
        for f in feedback_raw
    ]

    # Overall strength: combine ML prediction with rule-based complexity
    complexity = analysis.get("complexity_score", 0)
    overall_score = (complexity + prediction_raw["strength_index"] * 25) / 2
    overall_strength = prediction_raw["strength_label"]

    return PasswordAnalysisResponse(
        length=analysis["length"],
        uppercase_count=analysis["uppercase_count"],
        lowercase_count=analysis["lowercase_count"],
        digit_count=analysis["digit_count"],
        special_count=analysis["special_count"],
        unique_char_ratio=round(analysis["unique_char_ratio"], 4),
        char_diversity=analysis["character_diversity"],
        shannon_entropy=round(analysis["shannon_entropy"], 4),
        search_space_entropy=round(analysis["search_space_entropy"], 4),
        complexity_score=round(complexity, 2),
        patterns=patterns,
        crack_times=crack_times,
        ml_prediction=ml_prediction,
        feedback=feedback,
        overall_strength=overall_strength,
        overall_score=round(overall_score, 2),
    )


@router.post("/predict", response_model=MLPrediction)
async def predict_password(request: PasswordAnalysisRequest):
    """ML-only password strength prediction."""
    pwd = request.password.strip()
    predictor = PasswordPredictor()
    result = predictor.predict(pwd)
    return MLPrediction(**result)


@router.post("/generate", response_model=PasswordGenerateResponse)
async def generate_password(request: PasswordGenerateRequest):
    """Generate a secure password with the given options."""
    try:
        gen = PasswordGenerator()
        pwd = gen.generate(
            length=request.length,
            uppercase=request.uppercase,
            lowercase=request.lowercase,
            digits=request.digits,
            symbols=request.symbols,
            exclude_ambiguous=request.exclude_ambiguous,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    analyzer = PasswordAnalyzer()
    analysis = analyzer.analyze(pwd)

    predictor = PasswordPredictor()
    prediction = predictor.predict(pwd)

    return PasswordGenerateResponse(
        password=pwd,
        length=len(pwd),
        entropy=round(analysis["shannon_entropy"], 4),
        strength=prediction["strength_label"],
    )


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    model_loaded = False
    try:
        predictor = PasswordPredictor()
        model_loaded = predictor.model is not None
    except Exception:
        pass

    return HealthResponse(
        status="ok",
        version="1.0.0",
        model_loaded=model_loaded,
    )


@router.get("/model-info", response_model=ModelInfoResponse)
async def model_info():
    """Return ML model metadata."""
    meta_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "saved_model",
        "model_metadata.json",
    )
    try:
        with open(meta_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return ModelInfoResponse(
                model_type=data.get("model_type", "Unknown"),
                accuracy=data.get("accuracy", 0.0),
                precision=data.get("precision", 0.0),
                recall=data.get("recall", 0.0),
                f1_score=data.get("f1_score", 0.0),
                feature_count=data.get("num_features", 0),
                feature_names=data.get("feature_names", []),
                training_date=data.get("training_date", "Unknown"),
                training_samples=data.get("training_samples", 0),
                classes=data.get("classes", []),
            )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Model metadata not found. Train the model first.")
