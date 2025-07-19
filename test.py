import requests

url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=AIzaSyC3E6_KGyRnaYWxWOVMomoSgqdVYzM4V7Q"

payload = {
    "email": "gouravagarwal014@gmail.com",
    "password": "12345678",
    "returnSecureToken": True
}

response = requests.post(url, json=payload)
response=response.json()

print(response['idToken'])
