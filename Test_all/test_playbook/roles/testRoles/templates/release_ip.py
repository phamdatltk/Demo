import requests

url = 'https://console-api-stg.fptcloud.com/api/v1/vmware/vpc/f072bf85-334b-49c4-bae2-b67878abadc0/internal/floating-ips/release'
headers = {
    'Content-Type': 'application/json',
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzb21lIjoicGF5bG9hZCJ9.Joh1R2dYzkRvDkqv3sygm5YyK8Gi4ShZqbhK2gxcs2U'
}

body = {
   "ip_address": "100.73.255."
}

# Send request
response = requests.post(url, headers=headers, json=body)
