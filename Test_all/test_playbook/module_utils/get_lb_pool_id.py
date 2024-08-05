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

def get_lb_pool_id(client, edge_gateway_urn, name):
    # name is name of lb pool
    params = RequestInfo(client)

    resp = handle_get(
        f"{params.version_url}/edgeGateways/{ edge_gateway_urn }/loadBalancer/poolSummaries?page=1&pageSize=1000&sortAsc=name&links=true", headers=params.headers
    )
    lb_pool_id = ''
    for i in resp.json()["values"]:
        if i["name"] == name:
            lb_pool_id = i["id"]

    return lb_pool_id