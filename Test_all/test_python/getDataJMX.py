import requests
import json

response = requests.get('http://10.138.244.3:7071')
print(response.text != 0)