import requests

url = "https://api.wetrocloud.com/v1/collection/query/"
headers = {
        "Authorization": "Token wtc-sk-ff86dcf1bdf90981a679044600396edfab43bf01"
    }

data = {
    "collection_id": "test5",
    "request_query": "Whats the name of the company, and which people hold the largest stake?",
    "model": "gpt-4o-mini"
}


response = requests.post(url, data=data, headers=headers)
print(response.text)