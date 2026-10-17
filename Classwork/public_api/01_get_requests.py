import requests

URL="https://jsonplaceholder.typicode.com/posts/1"

response = requests.get(URL)
data = response.json()
print(response.status_code)
print(data["title"])

