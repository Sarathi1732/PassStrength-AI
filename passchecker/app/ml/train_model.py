import json
import os
import time
import pandas as pd
from datetime import datetime

try:
    import joblib
    from sklearn.model_selection import train_test_split, cross_val_score
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.tree import DecisionTreeClassifier
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("Warning: scikit-learn not available. Training will not run properly.")

try:
    from xgboost import XGBClassifier
    XGB_AVAILABLE = True
except ImportError:
    XGB_AVAILABLE = False
    print("Warning: XGBoost not available, skipping XGBoost evaluation.")

from app.ml.dataset_generator import DatasetGenerator
from app.ml.feature_engineering import FeatureExtractor

def train_and_evaluate():
    if not SKLEARN_AVAILABLE:
        print("Please install scikit-learn, pandas, and joblib.")
        return

    # Generate dataset if it doesn't exist
    dataset_path = "dataset/sample_training_data.csv"
    if not os.path.exists(dataset_path):
        print("Dataset not found. Generating...")
        gen = DatasetGenerator()
        gen.generate(num_samples=10000, output_path=dataset_path)

    print("Loading dataset...")
    df = pd.read_csv(dataset_path)
    
    X = df.drop(columns=["label"])
    y = df["label"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    models = {
        "RandomForest": RandomForestClassifier(n_estimators=200, random_state=42),
        "LogisticRegression": LogisticRegression(max_iter=1000, random_state=42),
        "DecisionTree": DecisionTreeClassifier(random_state=42)
    }

    if XGB_AVAILABLE:
        models["XGBoost"] = XGBClassifier(use_label_encoder=False, eval_metric='mlogloss', random_state=42)

    best_model_name = None
    best_model = None
    best_accuracy = 0
    best_metrics = {}

    for name, model in models.items():
        print(f"\nTraining {name}...")
        start_time = time.time()
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        
        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, average='weighted', zero_division=0)
        rec = recall_score(y_test, y_pred, average='weighted', zero_division=0)
        f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
        cm = confusion_matrix(y_test, y_pred)
        
        cv_scores = cross_val_score(model, X, y, cv=5)
        cv_mean = cv_scores.mean()

        print(f"{name} Results:")
        print(f"Accuracy:  {acc:.4f}")
        print(f"Precision: {prec:.4f}")
        print(f"Recall:    {rec:.4f}")
        print(f"F1 Score:  {f1:.4f}")
        print(f"CV Mean:   {cv_mean:.4f}")
        print(f"Confusion Matrix:\n{cm}")
        print(f"Time taken: {time.time() - start_time:.2f}s")

        if acc > best_accuracy:
            best_accuracy = acc
            best_model_name = name
            best_model = model
            best_metrics = {
                "accuracy": float(acc),
                "precision": float(prec),
                "recall": float(rec),
                "f1_score": float(f1),
                "cross_val_mean": float(cv_mean)
            }

    print(f"\nBest model selected: {best_model_name} with accuracy {best_accuracy:.4f}")

    # Save model and metadata
    saved_model_dir = "saved_model"
    os.makedirs(saved_model_dir, exist_ok=True)
    
    model_path = os.path.join(saved_model_dir, "password_strength_model.joblib")
    joblib.dump(best_model, model_path)
    
    extractor = FeatureExtractor()
    feature_names = extractor.get_feature_names()
    
    metadata = {
        "model_type": best_model_name,
        "accuracy": best_metrics["accuracy"],
        "precision": best_metrics["precision"],
        "recall": best_metrics["recall"],
        "f1_score": best_metrics["f1_score"],
        "feature_names": feature_names,
        "num_features": len(feature_names),
        "classes": ["Very Weak", "Weak", "Medium", "Strong", "Very Strong"],
        "training_date": datetime.now().strftime("%Y-%m-%d"),
        "training_samples": len(df),
        "cross_val_mean": best_metrics["cross_val_mean"]
    }

    meta_path = os.path.join(saved_model_dir, "model_metadata.json")
    with open(meta_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=4)

    print(f"Model saved to {model_path}")
    print(f"Metadata saved to {meta_path}")

if __name__ == "__main__":
    train_and_evaluate()
