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

def get_edge_gw_id(client, vdc_id, vcd_url, edge_gw_name):
    params = RequestInfo(client)
    resp = handle_get(
            f"{params.api_url}/query?type=edgeGateway&page=1&pageSize=25&format=records&links=true&filter=(vdc=={vdc_id})&sortAsc=name",
            headers=params.json_special_headers,
        )
    if not resp.ok:
        raise Exception(resp.content)
    edge_gw_id = ""
    for i in resp.json()["record"]:
        if i["name"] == edge_gw_name:
            for j in i["link"]:
                if "cloudapi/1.0.0/edgeGateways/urn:vcloud:gateway" in j["href"]:
                    j["href"] = j["href"].replace(f"{vcd_url}/cloudapi/1.0.0/edgeGateways/urn:vcloud:gateway:", '')
                    edge_gw_id = j["href"]
        
    return edge_gw_id

def get_edge_gw_urn(client, vdc_id, vcd_url, edge_gw_name):
    params = RequestInfo(client)
    resp = handle_get(
            f"{params.api_url}/query?type=edgeGateway&page=1&pageSize=25&format=records&links=true&filter=(vdc=={vdc_id})&sortAsc=name",
            headers=params.json_special_headers,
        )
    # print(params.api_url)
    if not resp.ok:
        raise Exception(resp.content)
    edge_gw_urn = ""
    for i in resp.json()["record"]:
        if i["name"] == edge_gw_name:
            for j in i["link"]:
                if "cloudapi/1.0.0/edgeGateways/urn:vcloud:gateway" in j["href"]:
                    j["href"] = j["href"].replace(f"{vcd_url}/cloudapi/1.0.0/edgeGateways/", '')
                    edge_gw_urn = j["href"]
    # print(edge_gw_urn)
    return edge_gw_urn