import json
import os
from typing import Dict, Any

try:
    import joblib
    JOBLIB_AVAILABLE = True
except ImportError:
    JOBLIB_AVAILABLE = False

from app.ml.feature_engineering import FeatureExtractor

class PasswordPredictor:
    """Predicts password strength using a trained ML model (Singleton)."""
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(PasswordPredictor, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.extractor = FeatureExtractor()
        self.model = None
        self.metadata = None
        self.classes = ["Very Weak", "Weak", "Medium", "Strong", "Very Strong"]
        
        model_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "saved_model", "password_strength_model.joblib")
        meta_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "saved_model", "model_metadata.json")
        
        if JOBLIB_AVAILABLE and os.path.exists(model_path):
            try:
                self.model = joblib.load(model_path)
            except Exception as e:
                print(f"Failed to load model: {e}")
                
        if os.path.exists(meta_path):
            try:
                with open(meta_path, 'r', encoding='utf-8') as f:
                    self.metadata = json.load(f)
                    if "classes" in self.metadata:
                        self.classes = self.metadata["classes"]
            except Exception as e:
                print(f"Failed to load metadata: {e}")

    def _rule_based_fallback(self, features: list) -> int:
        """Simple rule-based fallback if model is not available."""
        # features[14] is complexity_score
        score = features[14]
        if score < 20: return 0
        if score < 40: return 1
        if score < 60: return 2
        if score < 80: return 3
        return 4

    def predict(self, password: str) -> Dict[str, Any]:
        """Predicts the strength of the given password."""
        features = self.extractor.extract_features(password)
        
        if self.model:
            # Predict using model — wrap in DataFrame to provide feature names
            try:
                import pandas as pd
                feature_names = self.extractor.get_feature_names()
                features_df = pd.DataFrame([features], columns=feature_names)
                prediction_idx = int(self.model.predict(features_df)[0])
                probs = self.model.predict_proba(features_df)[0]
                confidence = float(probs[prediction_idx])
                
                probabilities = {self.classes[i]: float(probs[i]) for i in range(len(self.classes))}
            except Exception:
                # Fallback on error
                prediction_idx = self._rule_based_fallback(features)
                confidence = 1.0
                probabilities = {self.classes[i]: (1.0 if i == prediction_idx else 0.0) for i in range(len(self.classes))}
        else:
            # Fallback when no model loaded
            prediction_idx = self._rule_based_fallback(features)
            confidence = 1.0
            probabilities = {self.classes[i]: (1.0 if i == prediction_idx else 0.0) for i in range(len(self.classes))}
            
        return {
            "strength_label": self.classes[prediction_idx],
            "strength_index": prediction_idx,
            "confidence": confidence,
            "probabilities": probabilities
        }

# Optional testing if run directly
if __name__ == "__main__":
    predictor = PasswordPredictor()
    print(predictor.predict("password123"))
    print(predictor.predict("CorrectHorseBatteryStaple123!"))
