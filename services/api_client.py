import requests

def call_api(payload, url):
    
    API_URL = url

    response = requests.post(API_URL, json=payload)

    if response.status_code != 200:
        raise Exception(f"API Error: {response.text}")

    data = response.json()

    if isinstance(data, dict):
        data = [data]

    return data