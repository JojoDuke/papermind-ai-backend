import requests

response = requests.get(
"https://api.wetrocloud.com/v1/collection/all/",
headers = {
        "Authorization": "Token wtc-sk-ff86dcf1bdf90981a679044600396edfab43bf01"
    }
)


try:
    print(response.json())
except ValueError:
    print(response.text)