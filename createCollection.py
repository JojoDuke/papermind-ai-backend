import requests

url = "https://api.wetrocloud.com/v1/resource/insert/"
headers = {
        "Authorization": "Token wtc-sk-ff86dcf1bdf90981a679044600396edfab43bf01"
    }

data = {
    "collection_id": "test5",
    "resource": "https://pkuymxykjsobcunjabod.supabase.co/storage/v1/object/sign/test4bucket/Founder%20Stock%20Board%20Consent.pdf?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1cmwiOiJ0ZXN0NGJ1Y2tldC9Gb3VuZGVyIFN0b2NrIEJvYXJkIENvbnNlbnQucGRmIiwiaWF0IjoxNzQzMDkxNjMzLCJleHAiOjE3NDU2ODM2MzN9.UzVBdqf-9aii_GZsBJwSIDsqT7LpHRgarGAetTqFB9w",
    "type":"file"
}


response = requests.post(url, data=data, headers=headers)
print(response.text)

