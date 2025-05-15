#!/usr/bin/env python3
"""
Training script for the Iris classification model
Includes data validation, model versioning, and integrity checks
"""

import os
import json
import pickle
import hashlib
from datetime import datetime
import numpy as np
import pandas as pd
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, classification_report

def validate_data(X, y):
    """Validate training data integrity"""
    # Check for expected shape
    if X.shape[1] != 4:
        raise ValueError(f"Expected 4 features, got {X.shape[1]}")
    
    # Check for missing values
    if np.isnan(X).any() or np.isnan(y).any():
        raise ValueError("Data contains missing values")
    
    # Check target classes
    unique_classes = np.unique(y)
    if len(unique_classes) != 3:
        raise ValueError(f"Expected 3 classes, got {len(unique_classes)}")
    
    print(f"✓ Data validation passed: {X.shape[0]} samples, {X.shape[1]} features")

def train_model():
    """Train model with comprehensive validation"""
    print("Loading Iris dataset...")
    data = load_iris()
    X, y = data.data, data.target
    
    # Validate data
    validate_data(X, y)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print("Training Random Forest model...")
    model = RandomForestClassifier(
        n_estimators=100,
        random_state=42,
        max_depth=5,
        min_samples_split=2,
        min_samples_leaf=1
    )
    
    # Train with cross-validation
    cv_scores = cross_val_score(model, X_train, y_train, cv=5)
    print(f"Cross-validation scores: {cv_scores}")
    print(f"Mean CV accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
    
    # Final training
    model.fit(X_train, y_train)
    
    # Evaluate on test set
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"Test accuracy: {accuracy:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=data.target_names))
    
    # Model integrity checks
    if accuracy < 0.8:
        raise ValueError(f"Model accuracy too low: {accuracy}")
    
    # Save model
    os.makedirs("/config/models", exist_ok=True)
    model_path = "/config/models/iris_model.pkl"
    
    # Serialize and save
    model_bytes = pickle.dumps(model)
    with open(model_path, 'wb') as f:
        f.write(model_bytes)
    
    # Create integrity hash
    model_hash = hashlib.sha256(model_bytes).hexdigest()
    with open(f"{model_path}.hash", 'w') as f:
        f.write(model_hash)
    
    # Save metadata
    metadata = {
        "version": "1.0.0",
        "accuracy": float(accuracy),
        "cv_mean": float(cv_scores.mean()),
        "cv_std": float(cv_scores.std()),
        "created_at": datetime.utcnow().isoformat(),
        "model_hash": model_hash,
        "feature_names": data.feature_names.tolist(),
        "target_names": data.target_names.tolist(),
        "n_samples": int(X.shape[0]),
        "n_features": int(X.shape[1])
    }
    
    with open("/config/models/model_metadata.json", 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"\n✓ Model saved successfully")
    print(f"✓ Model hash: {model_hash[:16]}...")
    print(f"✓ Metadata saved")
    
    return model, metadata

if __name__ == "__main__":
    try:
        model, metadata = train_model()
        print("\n🎉 Training completed successfully!")
    except Exception as e:
        print(f"❌ Training failed: {e}")
        exit(1)