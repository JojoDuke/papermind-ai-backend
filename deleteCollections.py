import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def delete_collection(collection_id):
    url = "https://api.wetrocloud.com/v1/collection/delete/"
    headers = {
        "Authorization": f"Token {os.getenv('WETRO_API_TOKEN')}",
        "Content-Type": "application/json"
    }
    payload = {
        "collection_id": collection_id
    }

    try:
        response = requests.delete(url, headers=headers, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.json()
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

if __name__ == "__main__":
    collection_id = input("Enter collection ID to delete: ")
    delete_collection(collection_id)