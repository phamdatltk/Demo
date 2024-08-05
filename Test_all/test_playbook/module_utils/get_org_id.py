import requests
import json

from ansible.module_utils.requestInfo import RequestInfo
import http.client
http.client._MAXHEADERS = 1000

def handle_get(url, headers):
    print(url)
    resp = requests.get(url, headers=headers, verify=False)
    if not resp.ok:
        raise Exception(resp.content)
    return resp

def get_org_id(client):
    params = RequestInfo(client)

    resp = handle_get(
        f"{params.version_url}/orgs", headers=params.headers
    )
    org_id = ""
    for i in resp.json()["values"]:
        i["id"] = i["id"].replace('urn:vcloud:org:', '')
        org_id  = i["id"]
    return org_id

def get_org_urn(client):
    params = RequestInfo(client)

    resp = handle_get(
        f"{params.version_url}/orgs", headers=params.headers
    )
    org_urn = ""
    for i in resp.json()["values"]:
        org_urn  = i["id"]
    return org_urn

