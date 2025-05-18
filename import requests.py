import requests

url = "http://127.0.0.1:8000/ecommerce/v1/register_user"
data = {
    "first_name": "Raza",
    "last_name": "110",
    "email": "raza110@example.com",  # Added proper email format with @ symbol
    "password": "Raza110!@#",        # Added special characters and made it longer
    "timezone": "Asia/Karachi"
}

response = requests.put(url, json=data)
print(response.status_code)
print(response.json())