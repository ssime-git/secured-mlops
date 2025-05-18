#!/usr/bin/env python3
"""
Train a machine learning model and save it to the models directory.
The ML API will automatically load the model from the shared volume.
"""

import os
import pickle
import pandas as pd
import numpy as np
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Configuration
MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models')
MODEL_FILENAME = 'iris_model.pkl'
MODEL_PATH = os.path.join(MODEL_DIR, MODEL_FILENAME)

def load_data():
    """Load the Iris dataset."""
    print("Loading Iris dataset...")
    iris = load_iris()
    X = pd.DataFrame(iris.data, columns=iris.feature_names)
    y = pd.Series(iris.target, name='target')
    return X, y, iris.target_names

def train_model(X, y):
    """Train a RandomForest classifier."""
    print("Training model...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Model trained with accuracy: {accuracy:.4f}")
    
    return model, accuracy

def save_model(model, model_path=MODEL_PATH):
    """Save the trained model to disk."""
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    print(f"Model saved to {model_path}")

def main():
    # Load and prepare data
    X, y, target_names = load_data()
    
    # Train model
    model, accuracy = train_model(X, y)
    
    # Save model
    save_model(model)
    
    print("\nTraining complete!")
    print(f"- Model saved to: {os.path.abspath(MODEL_PATH)}")
    print(f"- Model accuracy: {accuracy:.4f}")
    print("\nThe ML API will automatically load the new model from the shared volume.")

if __name__ == "__main__":
    main()
