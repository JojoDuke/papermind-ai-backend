import requests

url = "https://api.wetrocloud.com/v1/collection/chat/"
headers = {
        "Authorization": "Token wtc-sk-ff86dcf1bdf90981a679044600396edfab43bf01"
    }

data = {
    "collection_id": "6f5b8378-87eb-40a1-9fd3-cce05eb12515",
    "message": "Tell me more",
    "chat_history": [{"role":"user","content":"What is this all about?"}, 
    {"role":"system","content":"This is about Queen Elizabeth_II of England"}]
}


response = requests.post(url, data=data, headers=headers)
print(response.text)