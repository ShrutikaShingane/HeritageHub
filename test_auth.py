import requests

# 1. Test Signup
print("--- Testing Signup ---")
signup_data = {
    "name": "Vedan",
    "email": "vedan@test.com",
    "password": "mysecretpassword",
    "role": "user"
}
res = requests.post('http://127.0.0.1:5000/api/signup', json=signup_data)
print(res.status_code, res.json())

# 2. Test Login (Sahi Password)
print("\n--- Testing Login (Correct Password) ---")
login_data = {
    "email": "vedan@test.com",
    "password": "mysecretpassword",
    "role": "user"
}
res = requests.post('http://127.0.0.1:5000/api/login', json=login_data)
print(res.status_code, res.json())

# 3. Test Login (Galat Password)
print("\n--- Testing Login (Wrong Password) ---")
login_data_wrong = {
    "email": "vedan@test.com",
    "password": "wrongpassword",
    "role": "user"
}
res = requests.post('http://127.0.0.1:5000/api/login', json=login_data_wrong)
print(res.status_code, res.json())