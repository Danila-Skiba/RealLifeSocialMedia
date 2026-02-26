import requests  as req

# Faile test 
response = req.get(
    "http://127.0.0.1:8000",
    headers={"Accept": "application/json"}
)

print(f'Test1: {response.status_code}')
print(f'Response: {response.text}')

# Success test
response = req.get(
    "http://127.0.0.1:8000",
    headers={"Accept": "text/html"}
)

print(f'Test2: {response.status_code}')
print(f'Response: {response.text}')

