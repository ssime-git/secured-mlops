#!/usr/bin/env python3
"""
Client script to test the ML API
"""

import requests
import json
from sklearn.datasets import load_iris

# API configuration
API_BASE = "https://api.localhost"
# For local testing without certificates:
# import urllib3
# urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_token():
    """Get authentication token"""
    response = requests.post(f"{API_BASE}/token", verify=False)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        raise Exception(f"Failed to get token: {response.text}")

def make_prediction(token, features):
    """Make a prediction with the API"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    data = {"features": features}
    response = requests.post(
        f"{API_BASE}/predict",
        json=data,
        headers=headers,
        verify=False
    )
    
    return response

def test_api():
    """Test the ML API with sample data"""
    print("Testing ML API...")
    
    # Get token
    print("1. Getting authentication token...")
    token = get_token()
    print(f"✓ Token obtained: {token[:20]}...")
    
    # Load sample data
    iris = load_iris()
    sample_idx = 0
    sample_features = iris.data[sample_idx].tolist()
    actual_class = iris.target[sample_idx]
    
    print(f"\n2. Making prediction...")
    print(f"Sample features: {sample_features}")
    print(f"Actual class: {actual_class} ({iris.target_names[actual_class]})")
    
    # Make prediction
    response = make_prediction(token, sample_features)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Prediction successful!")
        print(f"Predicted class: {result['prediction']} ({iris.target_names[result['prediction']]})")
        print(f"Probabilities: {[f'{p:.3f}' for p in result['probability']]}")
        print(f"Model version: {result['model_version']}")
        print(f"Timestamp: {result['timestamp']}")
    else:
        print(f"❌ Prediction failed: {response.status_code}")
        print(response.text)
    
    # Test rate limiting
    print(f"\n3. Testing rate limiting...")
    for i in range(3):
        response = make_prediction(token, sample_features)
        print(f"Request {i+1}: {response.status_code}")
    
    # Get model info
    print(f"\n4. Getting model information...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_BASE}/model/info", headers=headers, verify=False)
    
    if response.status_code == 200:
        info = response.json()
        print(f"✓ Model info retrieved:")
        for key, value in info.items():
            print(f"  {key}: {value}")

if __name__ == "__main__":
    try:
        test_api()
        print("\n🎉 API test completed!")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        exit(1)