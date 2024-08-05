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

def get_edge_gateway_nat_rule(client, gateway_urn, name):
    #name is name of nat rule
    params = RequestInfo(client)

    resp = handle_get(
        f"{params.version_url}/edgeGateways/{gateway_urn}/nat/rules?page=1&pageSize=10000", headers=params.headers
    )
    edge_gw_nat_rule_id = ""
    for i in resp.json()["values"]:
        if i["name"] == name:
            edge_gw_nat_rule_id = i["id"]
    # print(edge_gw_nat_rule_id)
    return edge_gw_nat_rule_id

