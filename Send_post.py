import requests
# import fitz
import time
import json

payload = open('G:\\Dokumente\\Uni\\2023\\Digital_Libraries\\Projekt\\test_data\\Simple_text.pdf', 'rb')
url_post = "http://127.0.0.1:8080/test_post"
url_get = "http://127.0.0.1:8080/test_get"


# print(payload)

responce = requests.post(url_post, data=payload)
test_json = json.dumps(responce.text)
print(test_json)
responce = requests.get(url_get, data=test_json)
print(responce.text)