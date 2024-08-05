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

def get_vdc_id(client, VDC_name):
    params = RequestInfo(client)

    resp = handle_get(
        # f"{params.version_url}/vdcs", headers=params.headers
        f"{params.version_url}/vdcs?pageSize=1000", headers=params.headers
    )
    # print(resp.json())
    # print(resp.json()["values"])
    vdc_id = ""
    for i in resp.json()["values"]:
        if i["name"] == VDC_name:
            i["id"] = i["id"].replace('urn:vcloud:vdc:', '')
        # print(i["id"])
            vdc_id = i["id"]
    return vdc_id

def get_vdc_urn(client, VDC_name):
    params = RequestInfo(client)

    resp = handle_get(
        f"{params.version_url}/vdcs?pageSize=1000", headers=params.headers
    )
    vdc_urn = ""
    for i in resp.json()["values"]:
        if i["name"] == VDC_name:
            vdc_urn = i["id"]
    return vdc_urn