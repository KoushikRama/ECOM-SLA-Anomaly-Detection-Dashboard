import requests

def call_api(payload, backend, urls):
    
    API_URL = urls["fastapi"] if backend == "FastAPI" else urls["sagemaker"]

    response = requests.post(API_URL, json=payload)

    if response.status_code != 200:
        raise Exception(f"API Error: {response.text}")

    data = response.json()

    if isinstance(data, dict):
        data = [data]

    return data