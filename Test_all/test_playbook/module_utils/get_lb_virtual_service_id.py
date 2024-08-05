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

def get_id_lb_virtualservice(client, gateway_id, name):
    # name is name of virtual service
    params = RequestInfo(client)

    resp = handle_get(
        f"{params.version_url}/edgeGateways/{gateway_id}/loadBalancer/virtualServiceSummaries?page=1&pageSize=1000&sortAsc=name&links=true", headers=params.headers
    )
    virtualservice_id = ''
    for i in resp.json()["values"]:
        if i["name"] == name:
            virtualservice_id = i["id"]
    return virtualservice_id

def check_active_lb_virtualservice(client, gateway_id, name):
    # name is name of virtual service
    params = RequestInfo(client)

    resp = handle_get(
        f"{params.version_url}/edgeGateways/{gateway_id}/loadBalancer/virtualServiceSummaries?page=1&pageSize=1000&sortAsc=name&links=true", headers=params.headers
    )
    for i in resp.json()["values"]:
        if i["name"] == name:
            return True
    return False