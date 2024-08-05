import requests
import json

from ansible.module_utils.requestInfo import RequestInfo


def handle_get(url, headers):
    print(url)
    resp = requests.get(url, headers=headers, verify=False)
    if not resp.ok:
        raise Exception(resp.content)
    return resp

def delete_nat_rule(client, gateway_urn, rule_id):
    rule_obj = {}

    params = RequestInfo(client)
    resp = requests.delete(
        f"{params.version_url}/edgeGateways/{gateway_urn}/nat/rules/{rule_id}",
        headers=params.headers,
        data=json.dumps(rule_obj),
        verify=False
    )
    if not resp.ok:
        raise Exception(resp.content)
    return rule_obj

