"""
Test script to verify connectivity to the ML API.
This script demonstrates how to connect to the ML API from within the code-server container.
"""

import requests
import os
import sys

def test_ml_api_connection():
    """Test connection to the ML API"""
    try:
        # Try direct container-to-container communication
        response = requests.get("http://ml-api:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Successfully connected to ML API")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"❌ ML API returned status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to connect to ML API: {e}")
        return False

def test_direct_ip_connection():
    """Test direct IP connection to the ML API"""
    try:
        # Try direct IP connection (useful if DNS resolution fails)
        response = requests.get("http://172.19.0.5:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Successfully connected to ML API via direct IP")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"❌ ML API (direct IP) returned status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to connect to ML API via direct IP: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Testing ML API Connectivity")
    print("=" * 50 + "\n")
    
    print("1. Testing connection via container name (ml-api:8000)")
    container_name_success = test_ml_api_connection()
    
    print("\n2. Testing connection via direct IP (172.19.0.5:8000)")
    direct_ip_success = test_direct_ip_connection()
    
    print("\n" + "=" * 50)
    if container_name_success or direct_ip_success:
        print("✅ Connectivity tests completed successfully")
        if not container_name_success:
            print("   Note: Container name resolution failed, but direct IP works")
        sys.exit(0)
    else:
        print("❌ Connectivity tests failed")
        sys.exit(1)
