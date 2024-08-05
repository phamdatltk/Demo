import requests
import json
from ansible.module_utils.requestInfo import RequestInfo

def create_snat_rule(client, name, edge_gateway_urn, nat_rule):
    # name is name of snat rule
    ip_address = nat_rule["ip_address"]
    ip_address_internal = nat_rule["ip_address_internal"]
    ip_address_destination = nat_rule["ip_address_destination"]
    snat_priority = nat_rule["snat_priority"]
    rule_obj = {
        "name": name,
        "enabled": True,
        "ruleType": "SNAT",
        "externalAddresses": ip_address,
        "internalAddresses": ip_address_internal,
        "snatDestinationAddresses": ip_address_destination,
        "priority": snat_priority
    }

    params = RequestInfo(client)
    resp = requests.post(
        f"{params.version_url}/edgeGateways/{edge_gateway_urn}/nat/rules",
        headers=params.headers,
        data=json.dumps(rule_obj),
        verify=False
    )
    if not resp.ok:
        raise Exception(resp.content)
    return rule_obj
