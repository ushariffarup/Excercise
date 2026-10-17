import requests

URL="https://jsonplaceholder.typicode.com/users/"

response = requests.get(URL)
data = response.json()
print(response.status_code)
for user in data:
    name = user["name"]
    email = user["email"]
    company = user["company"]["name"]
    phone_ext = user["phone"].split("x")
    if len(phone_ext) > 1:
        phone_ext = phone_ext[1]
    else:
        phone_ext = ""
    print(f"Name: {name}, Email: {email}, Company: {company}, Phone Extension: {phone_ext}")