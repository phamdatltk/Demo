import requests

from ansible.module_utils.requestInfo import RequestInfo
from ansible.module_utils.get_vdc_id import get_vdc_id
from ansible.module_utils.get_vapp_vm import get_vm_href
from ansible.module_utils.get_vapp_vm import get_vm_id
from ansible.module_utils.get_vapp_vm import get_list_vm_info
from ansible.module_utils.get_vapp_id import get_vapp_uuid

def write_payload_to_file(client, vapp_uuid, vapp_name, vm_list, affinity_rule_name, vdc_name):
    vapp_uuid = get_vapp_uuid(client, vapp_name, vdc_name)
    payload = f"""<?xml version="1.0" encoding="UTF-8"?>
<root:VmAffinityRule
    xmlns:root=\"http://www.vmware.com/vcloud/v1.5\">
    <root:Name>{affinity_rule_name}</root:Name>
    <root:IsEnabled>true</root:IsEnabled>
    <root:IsMandatory>true</root:IsMandatory>
    <root:Polarity>Anti-Affinity</root:Polarity>
    <root:VmReferences>
    """
    file= open(r'payload.txt', 'w')
    file.write(payload)
    file.close()
    for vm in vm_list:
        vm_href = get_vm_href(client, vapp_uuid, vm)
        vm_id = get_vm_id(client, vapp_uuid, vm)
        payload = f"""<root:VmReference href="{vm_href}" id="{vm_id}" name="{vm}" type="com.vmware.vcloud.entity.vm" />
    """
        file = open(r"payload.txt", "a")
        file.write("\t")
        file.write(payload)
        file.close()
    payload = """</root:VmReferences>
</root:VmAffinityRule>"""
    file = open(r"payload.txt", "a")
    file.write(payload)
    file.close()

def create_anti_affinity_rule(client, vdc_id, vapp_uuid, vapp_name, affinity_rule_name, vm_list, vdc_name):
    write_payload_to_file(client, vapp_uuid, vapp_name, vm_list, affinity_rule_name, vdc_name)
    uri = client.get_api_uri()
    url = f"{uri}/vdc/{vdc_id}/vmAffinityRules/"
    
    file = open(r"payload.txt", "r")
    payload = file.read()
    file.close()

    params = RequestInfo(client)
    resp = requests.post(
        url,
        headers=params.xml_headers,
        data=payload,
        verify=False,
    )
    
    print("response...", resp)
    if not resp.ok:
        raise Exception(resp.content)
    return url

def update_anti_affinity_rule(client, vapp_uuid, vapp_name, affinity_rule_name, affinity_rule_id, vm_list, vdc_name):
    write_payload_to_file(client, vapp_uuid, vapp_name, vm_list, affinity_rule_name, vdc_name)
    uri = client.get_api_uri()
    url = f"{uri}/vmAffinityRule/{affinity_rule_id}/"
    
    file = open(r"payload.txt", "r")
    payload = file.read()
    file.close()

    params = RequestInfo(client)
    resp = requests.put(
        url,
        headers=params.xml_headers,
        data=payload,
        verify=False,
    )
    
    print("response...", resp)
    if not resp.ok:
        raise Exception(resp.content)
    return url