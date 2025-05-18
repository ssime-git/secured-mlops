"""
ML API Test Script with Authentication

This script demonstrates how to:
1. Obtain an authentication token from the ML API
2. Use the token to make authenticated predictions
3. Handle errors and display results
"""

import requests
import json
import sys
from typing import Optional, Dict, Any

# Configuration
# Try both container name and direct IP for maximum compatibility
BASE_URLS = [
    "http://ml-api:8000",      # Container name
    #"http://172.19.0.5:8000"  # Direct IP
]
VERIFY_SSL = False  # Using HTTP for internal communication

class ConnectionError(Exception):
    """Custom exception for connection errors"""
    pass

# Sample data for prediction
SAMPLE_DATA = {
    "features": [5.1, 3.5, 1.4, 0.2]  # Example Iris flower features
}

class MLAPIClient:
    def __init__(self, base_urls: list, verify_ssl: bool = False):
        self.base_urls = base_urls
        self.verify_ssl = verify_ssl
        self.token = None
        self.active_url = None
        self.session = requests.Session()
        self.session.verify = verify_ssl
        
        # Disable SSL warnings if not verifying SSL
        if not verify_ssl:
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            
        # Test connections and find a working URL
        self._find_working_url()
        
    def _find_working_url(self):
        """Find a working URL from the list of base URLs"""
        for url in self.base_urls:
            try:
                response = self.session.get(f"{url}/health", timeout=2)
                if response.status_code == 200:
                    self.active_url = url
                    print(f"✅ Connected to ML API at {url}")
                    return
            except requests.exceptions.RequestException:
                continue
                
        raise ConnectionError("❌ Could not connect to ML API using any of the provided URLs")
    
    def _make_request(self, method, endpoint, **kwargs):
        """Helper method to make HTTP requests with retry logic"""
        if not self.active_url:
            self._find_working_url()
            
        url = f"{self.active_url}{endpoint}"
        
        # Add auth token if available
        if self.token and 'headers' in kwargs:
            kwargs['headers']['Authorization'] = f"Bearer {self.token}"
            
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Status code: {e.response.status_code}")
                print(f"Response: {e.response.text}")
            raise
            
    def get_token(self) -> Optional[str]:
        """Get an authentication token from the API"""
        try:
            # In a real application, you would send username/password or API key
            # For this demo, we're using a simple token endpoint without credentials
            response = self._make_request(
                'POST', 
                '/token',
                headers={"Content-Type": "application/json"}
            )
            
            token_data = response.json()
            self.token = token_data.get("access_token")
            return self.token
            
        except Exception as e:
            print(f"❌ Failed to get token: {e}")
            return None
    
    def make_prediction(self, features: list) -> Optional[Dict[str, Any]]:
        """Make a prediction using the ML API"""
        if not self.token:
            print("❌ No authentication token available. Call get_token() first.")
            return None
            
        try:
            response = self._make_request(
                'POST',
                '/predict',
                headers={"Content-Type": "application/json"},
                json={"features": features}
            )
            return response.json()
            
        except Exception as e:
            print(f"❌ Prediction failed: {e}")
            return None
    
    def get_model_info(self) -> Optional[Dict[str, Any]]:
        """Get information about the loaded model"""
        if not self.token:
            print("❌ No authentication token available. Call get_token() first.")
            return None
            
        try:
            response = self._make_request(
                'GET',
                '/model/info',
                headers={"Authorization": f"Bearer {self.token}"}
            )
            return response.json()
            
        except Exception as e:
            print(f"❌ Failed to get model info: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Status code: {e.response.status_code}")
                print(f"Response: {e.response.text}")
            return None

def main():
    print("🔐 Testing ML API Authentication and Prediction")
    print("=" * 50 + "\n")
    
    try:
        # Initialize the client with multiple connection options
        print("🔄 Testing connectivity to ML API...")
        client = MLAPIClient(BASE_URLS, verify_ssl=VERIFY_SSL)
        print("✅ Connected to ML API successfully!\n")
        
        # Step 1: Get authentication token
        print("1. Getting authentication token...")
        token = client.get_token()
        
        if not token:
            print("❌ Failed to get authentication token. Exiting...")
            return
            
        print(f"✅ Successfully obtained token: {token[:15]}...\n")
        
        # Step 2: Get model information
        print("2. Getting model information...")
        model_info = client.get_model_info()
        
        if model_info:
            print("✅ Model information:")
            print(f"   - Model Name: {model_info.get('model_name', 'N/A')}")
            print(f"   - Model Version: {model_info.get('model_version', 'N/A')}")
            print(f"   - Features: {model_info.get('feature_names', 'N/A')}")
        else:
            print("❌ Failed to get model information\n")
        
        # Step 3: Make a prediction
        print("\n3. Making a prediction...")
        print(f"   - Features: {SAMPLE_DATA['features']}")
        
        prediction = client.make_prediction(SAMPLE_DATA["features"])
        
        if prediction:
            print("✅ Prediction successful!")
            print(f"   - Predicted Class: {prediction.get('prediction', 'N/A')}")
            print(f"   - Confidence: {prediction.get('confidence', 'N/A')}")
            print(f"   - Timestamp: {prediction.get('timestamp', 'N/A')}")
        else:
            print("❌ Prediction failed\n")
            
    except ConnectionError as e:
        print(f"\n❌ {e}")
        print("\nTroubleshooting tips:")
        print("1. Make sure the ML API service is running")
        print("2. Check if the container IP address is correct (run 'docker network inspect secured-mlops_backend')")
        print("3. Verify that the ports are correctly exposed in docker-compose.yml")
        print("4. Check the logs with 'docker logs ml-api'")
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
