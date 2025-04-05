import requests

url = "https://api.wetrocloud.com/v1/collection/chat/"
headers = {
        "Authorization": "Token wtc-sk-ff86dcf1bdf90981a679044600396edfab43bf01"
    }

data = {
    "collection_id": "test5",
    "message": "Based off everything, can you tell me the valuation of the company?",
    "chat_history": [{"role":"user","content":"Whats the name of the company, and which people hold the largest stake?"}, 
    {"role":"system","content":"The name of the company is Midas Financial, Inc. The individuals holding the largest stake, each with 4,230,000 shares of Common Stock, are Duke Opoku-Amankwa and Sorkuwuli Zulkanir Abiola Braimah."}],
    "model": "gpt-4o"
}


response = requests.post(url, json=data, headers=headers)
print(response.text)