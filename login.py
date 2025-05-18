import requests
import json

# API endpoint 
url = "http://127.0.0.1:8000/ecommerce/v1/login_user"

# Login credentials
login_data = {
    "email": "raza110@example.com",
    "password": "Raza110!@#"
}

# Request headers
headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

try:
    # Make the request with detailed error output
    response = requests.post(
        url, 
        data=json.dumps(login_data),
        headers=headers
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {response.headers}")
    
    response_data = response.json()
    print("\nResponse Body:")
    print(json.dumps(response_data, indent=2))
    
    if response.status_code == 200:
        token = response_data.get('data', {}).get('access_token')
        if token:
            print(f"\nAccess Token: {token}")
        else:
            print("\nNo access token in response")
    else:
        print(f"\nError: {response_data.get('message', 'Unknown error')}")
            
except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")
except json.JSONDecodeError as e:
    print(f"Failed to parse response JSON: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")