import requests
import json
from ansible.module_utils.requestInfo import RequestInfo


def create_dnat_rule(client, dnat_rule_name, name_app_port_profile, edge_gateway_urn, nat_rule, app_port_profile_urn):
    # name is name of dnat rule
    ip_address = nat_rule["ip_address"]
    ip_address_internal = nat_rule["ip_address_internal"]
    translated_port = nat_rule["translated_port"]
    rule_obj = {
        "name": dnat_rule_name,
        "enabled": True,
        "ruleType": "DNAT",
        "externalAddresses": ip_address,
        "internalAddresses": ip_address_internal,
        "applicationPortProfile": {
            "name": name_app_port_profile,
            "id": app_port_profile_urn
        },
        "dnatExternalPort": translated_port
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
