import requests
import json

from ansible.module_utils.requestInfo import RequestInfo

def handle_get(url, headers):
    print(url)
    resp = requests.get(url, headers=headers, verify=False)
    if not resp.ok:
        raise Exception(resp.content)
    return resp

def delete_anti_affinity_rule(client, vcd_url, anti_affinity_rule_id):
    rule_obj = {}

    params = RequestInfo(client)
    resp = requests.delete(
        f"{vcd_url}/api/vmAffinityRule/{anti_affinity_rule_id}",
        headers=params.xml_headers,
        data=json.dumps(rule_obj),
        verify=False
    )
    if not resp.ok:
        raise Exception(resp.content)
    return rule_obj
