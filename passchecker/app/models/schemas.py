from pydantic import BaseModel, Field
from typing import Dict, List

class PasswordAnalysisRequest(BaseModel):
    password: str = Field(min_length=1, max_length=1000)

class PasswordGenerateRequest(BaseModel):
    length: int = Field(default=16, ge=4, le=128)
    uppercase: bool = True
    lowercase: bool = True
    digits: bool = True
    symbols: bool = True
    exclude_ambiguous: bool = False

class PatternResult(BaseModel):
    sequential: list[str]
    repeated: list[str]
    keyboard_walks: list[str]
    dictionary_words: list[str]
    leetspeak: list[str]
    has_patterns: bool

class CrackTimeResult(BaseModel):
    online_1k: str
    fast_online_1m: str
    offline_100m: str
    massive_10b: str

class FeedbackItem(BaseModel):
    type: str
    message: str
    priority: str

class MLPrediction(BaseModel):
    strength_label: str
    strength_index: int
    confidence: float
    probabilities: dict[str, float]

class PasswordAnalysisResponse(BaseModel):
    length: int
    uppercase_count: int
    lowercase_count: int
    digit_count: int
    special_count: int
    unique_char_ratio: float
    char_diversity: int
    shannon_entropy: float
    search_space_entropy: float
    complexity_score: float
    patterns: PatternResult
    crack_times: CrackTimeResult
    ml_prediction: MLPrediction
    feedback: list[FeedbackItem]
    overall_strength: str
    overall_score: float

class PasswordGenerateResponse(BaseModel):
    password: str
    length: int
    entropy: float
    strength: str

class HealthResponse(BaseModel):
    status: str
    version: str
    model_loaded: bool

class ModelInfoResponse(BaseModel):
    model_type: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    feature_count: int
    feature_names: list[str]
    training_date: str
    training_samples: int
    classes: list[str]
