import requests
import json
from requests.packages import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from ansible.module_utils.requestInfo import RequestInfo
import http.client
http.client._MAXHEADERS = 1000

def handle_get(url, headers):
    print(url)
    resp = requests.get(url, headers=headers, verify=False)
    if not resp.ok:
        raise Exception(resp.content)
    return resp


def get_vdc_group_urn(client, vdc_id, edge_gw_id):
    params = RequestInfo(client)
    resp = handle_get(
            f"{params.api_url}/query?type=edgeGateway&page=1&pageSize=25&format=records&links=true&filter=(vdc=={vdc_id})&sortAsc=name",
            headers=params.json_special_headers,
        )
    if not resp.ok:
        raise Exception(resp.content)
    vdcGroup_uuid = ""
    vdcGroup_urn = ""

    for i in resp.json()["record"]:
        for j in i["link"]:
            if edge_gw_id in j["href"]:
                vdcGroup_uuid = i["vdcGroupId"]
                vdcGroup_urn = "urn:vcloud:vdcGroup:" + vdcGroup_uuid
    return vdcGroup_urn

def get_vdc_group_id(client, vdc_id, vcd_url):
    params = RequestInfo(client)
    resp = handle_get(
            f"{params.api_url}/query?type=edgeGateway&page=1&pageSize=25&format=records&links=true&filter=(vdc=={vdc_id})&sortAsc=name",
            headers=params.json_special_headers,
        )
    if not resp.ok:
        raise Exception(resp.content)
    vdcGroup_id = ""
    for i in resp.json()["record"]:
        for j in i["link"]:
            if "cloudapi/1.0.0/vdcGroups/urn:vcloud:vdcGroup" in j["href"]:
                j["href"] = j["href"].replace(f"{vcd_url}/cloudapi/1.0.0/vdcGroups/urn:vcloud:vdcGroup:", '')
                vdcGroup_id = j["href"]
    # print(vdcGroup_id)
    return vdcGroup_id

def check_vdc_group_enable(client,vdc_id, edge_gw_id):
    params = RequestInfo(client)
    resp = handle_get(
            f"{params.api_url}/query?type=edgeGateway&page=1&pageSize=25&format=records&links=true&filter=(vdc=={vdc_id})&sortAsc=name",
            headers=params.json_special_headers,
        )
    if not resp.ok:
        raise Exception(resp.content)
    vdcGroup_id = ""
    for i in resp.json()["record"]:
        for j in i["link"]:
            # print(j)
            if edge_gw_id in j["href"]:
                vdcGroup_id = i["vdcGroupId"]
    if vdcGroup_id != "" and vdcGroup_id != None:
        return True
    print(vdcGroup_id)
    return False