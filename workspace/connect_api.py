#!/usr/bin/env python3
"""
Helper module for connecting to the ML API from the code-server
This handles DNS resolution issues by using the correct IP address
"""

import requests
import json
from typing import Dict, Any, Optional, Union

# The correct IP address for the ML API container
ML_API_IP = "172.19.0.5"
ML_API_PORT = 8000
ML_API_BASE_URL = f"http://{ML_API_IP}:{ML_API_PORT}"

def get_health() -> Dict[str, Any]:
    """Get the health status of the ML API"""
    response = requests.get(f"{ML_API_BASE_URL}/health")
    return response.json()

def predict(data: Dict[str, Any]) -> Dict[str, Any]:
    """Send prediction request to the ML API"""
    response = requests.post(f"{ML_API_BASE_URL}/predict", json=data)
    return response.json()

def get_model_info() -> Dict[str, Any]:
    """Get information about the loaded model"""
    response = requests.get(f"{ML_API_BASE_URL}/model/info")
    return response.json()

if __name__ == "__main__":
    # Simple test to verify connectivity
    try:
        health = get_health()
        print(f"ML API Health: {json.dumps(health, indent=2)}")
        
        if health.get("model_loaded"):
            model_info = get_model_info()
            print(f"\nModel Info: {json.dumps(model_info, indent=2)}")
        
        print("\n✅ Connection to ML API successful!")
    except Exception as e:
        print(f"\n❌ Connection failed: {e}")
