import requests
import json
import argparse

from ansible.module_utils.requestInfo import RequestInfo
from ansible.module_utils.get_vapp_vm import get_vm_ip
from ansible.module_utils.get_vapp_id import get_vapp_uuid

def handle_get(url, headers):
    print(url)
    resp = requests.get(url, headers=headers, verify=False)
    if not resp.ok:
        raise Exception(resp.content)
    return resp

def update_loadbalancer_pool(client, vapp_name, lb_pool_name, defaultport, algorithm, health_monitors, persistence_profile, member_count, members_list, gateway_ref_id, id_lb_pool, vdc_name):
    # name is name of lb pool
    vapp_uuid = get_vapp_uuid(client, vapp_name, vdc_name)
    members = list()
    for vm in members_list:
        vm_ip = get_vm_ip(client, vapp_uuid, vm)
        members.append({"ipAddress": vm_ip, "port": defaultport, "ratio": 1, "enabled": True, "healthStatus": ""})
    rule_obj = {
        "name": lb_pool_name,
        "description": "Automatically created by FKE. Do Not Delete",
        "enabled": "true",
        "passiveMonitoringEnabled": "true",
        "defaultPort": defaultport,
        "gracefulTimeoutPeriod": 1,
        "algorithm": algorithm,
        "healthMonitors": [ health_monitors ],
        "persistenceProfile": persistence_profile,
        "memberCount": member_count,
        "members": members,
        "gatewayRef": {
            "id": gateway_ref_id
        }
    }

    params = RequestInfo(client)
    resp = requests.put(
        f"{params.version_url}/loadBalancer/pools/{id_lb_pool}",
        headers=params.headers,
        data=json.dumps(rule_obj),
        verify=False
    )
    if not resp.ok:
        raise Exception(resp.content)
    return rule_obj