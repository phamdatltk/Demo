import requests

from ansible.module_utils.requestInfo import RequestInfo
import json
import http.client

http.client._MAXHEADERS = 1000


def handle_get(url, headers):
    print(url)
    resp = requests.get(url, headers=headers, verify=False)
    if not resp.ok:
        raise Exception(resp.content)
    return resp


def get_storage_profile_href(client, vdc_id, storage_profile_name):
    params = RequestInfo(client)
    uri = client.get_api_uri()
    resp = handle_get(
        f"{uri}/query?type=orgVdcStorageProfile&format=records&page=1&pageSize=15&filterEncoded=true&filter=((vdc=={vdc_id}))&sortAsc=name&links=true",
        headers=params.json_special_headers
    )
    storage_profile_href = ''
    for i in resp.json()['record']:
        if i["name"] == storage_profile_name:
            storage_profile_href = i['href']
    return storage_profile_href
