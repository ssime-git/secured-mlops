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
# Using internal Docker network address for container-to-container communication
BASE_URL = "http://ml-api:8000"  # Using container name and internal port
VERIFY_SSL = False  # Using HTTP for internal communication

# Sample data for prediction
SAMPLE_DATA = {
    "features": [5.1, 3.5, 1.4, 0.2]  # Example Iris flower features
}

class MLAPIClient:
    def __init__(self, base_url: str, verify_ssl: bool = False):
        self.base_url = base_url
        self.verify_ssl = verify_ssl
        self.token = None
        self.session = requests.Session()
        self.session.verify = verify_ssl
        
        # Disable SSL warnings if not verifying SSL
        if not verify_ssl:
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    def get_token(self) -> Optional[str]:
        """Get an authentication token from the API"""
        try:
            # In a real application, you would send username/password or API key
            # For this demo, we're using a simple token endpoint without credentials
            response = self.session.post(
                f"{self.base_url}/token",
                headers={"Content-Type": "application/json"},
                verify=self.verify_ssl
            )
            response.raise_for_status()
            
            token_data = response.json()
            self.token = token_data.get("access_token")
            return self.token
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to get token: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            return None
    
    def make_prediction(self, features: list) -> Optional[Dict[str, Any]]:
        """Make a prediction using the ML API"""
        if not self.token:
            print("❌ No authentication token available. Call get_token() first.")
            return None
            
        try:
            response = self.session.post(
                f"{self.base_url}/predict",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.token}"
                },
                json={"features": features},
                verify=self.verify_ssl
            )
            
            # Handle successful response
            if response.status_code == 200:
                return response.json()
                
            # Handle rate limiting
            elif response.status_code == 429:
                print("⚠️  Rate limit exceeded. Please try again later.")
                return None
                
            # Handle authentication errors
            elif response.status_code in (401, 403):
                print(f"🔒 Authentication failed: {response.text}")
                # Try to get a new token and retry once
                print("🔄 Attempting to get a new token...")
                self.token = self.get_token()
                if self.token:
                    return self.make_prediction(features)
                return None
                
            # Handle other errors
            else:
                print(f"❌ Prediction failed with status {response.status_code}: {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            return None
    
    def get_model_info(self) -> Optional[Dict[str, Any]]:
        """Get information about the loaded model"""
        if not self.token:
            print("❌ No authentication token available. Call get_token() first.")
            return None
            
        try:
            response = self.session.get(
                f"{self.base_url}/model/info",
                headers={"Authorization": f"Bearer {self.token}"},
                verify=self.verify_ssl
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to get model info: {e}")
            return None

def main():
    print("🔍 ML API Authentication Test\n" + "="*50 + "\n")
    
    # Initialize the client
    client = MLAPIClient(BASE_URL, VERIFY_SSL)
    
    # Step 1: Get authentication token
    print("🔑 Getting authentication token...")
    token = client.get_token()
    
    if not token:
        print("❌ Failed to authenticate. Exiting.")
        sys.exit(1)
        
    print(f"✅ Successfully authenticated. Token: {token[:15]}...\n")
    
    # Step 2: Get model information
    print("📊 Getting model information...")
    model_info = client.get_model_info()
    
    if model_info:
        print(f"✅ Model Info:")
        print(json.dumps(model_info, indent=2))
    else:
        print("⚠️  Could not retrieve model information\n")
    
    # Step 3: Make a prediction
    print("\n🤖 Making prediction...")
    print(f"📤 Sending features: {SAMPLE_DATA['features']}")
    
    prediction = client.make_prediction(SAMPLE_DATA["features"])
    
    if prediction:
        print("✅ Prediction successful!")
        print("\n📊 Prediction Results:")
        print(json.dumps(prediction, indent=2))
    else:
        print("❌ Prediction failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
