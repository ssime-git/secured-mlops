"""
Test script to verify connectivity to the ML API from the host machine.
"""

import requests
import sys

def test_connection():
    """Test connection to the ML API"""
    urls = [
        "http://localhost:8000",       # Direct port mapping
        "http://host.docker.internal:8000"  # Docker host
    ]
    
    for url in urls:
        try:
            print(f"\nTesting connection to {url}...")
            response = requests.get(f"{url}/health", timeout=5)
            if response.status_code == 200:
                print(f"✅ Successfully connected to {url}")
                print(f"Response: {response.json()}")
                return url
            else:
                print(f"❌ {url} returned status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to connect to {url}: {e}")
    
    return None

def main():
    print("🔍 Testing ML API Connectivity from Host")
    print("=" * 50 + "\n")
    
    base_url = test_connection()
    
    if not base_url:
        print("\n❌ Could not connect to the ML API using any of the available methods.")
        print("\nTroubleshooting tips:")
        print("1. Make sure the ML API container is running (docker ps)")
        print("2. Check if port 8000 is exposed (docker-compose.yml)")
        print("3. Try accessing the API directly in your browser: http://localhost:8000/health")
        print("4. Check the container logs: docker logs ml-api")
        sys.exit(1)
    
    print("\n✅ Success! You can now use the API at:", base_url)
    print("\nExample cURL command:")
    print(f"  curl -X GET {base_url}/health")

if __name__ == "__main__":
    main()
