import requests
# import fitz
import time
import json

payload = open('G:\\Dokumente\\Uni\\2023\\Digital_Libraries\\Projekt\\test_data\\war-and-peace.pdf', 'rb')
url_post = "http://127.0.0.1:8080/test_post"
url_get = "http://127.0.0.1:8080/test_get"


#print(payload)

responce = requests.post(url_post, data=payload)
test_json = json.loads(responce.text)
#print(test_json)
# time.sleep(3)
payload = json.dumps(test_json)
responce = requests.get(url_get, data=payload)
print(responce.text)