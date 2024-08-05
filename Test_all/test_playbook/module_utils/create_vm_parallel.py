import requests

from ansible.module_utils.requestInfo import RequestInfo

from ansible.module_utils.get_vapp_template import get_vapp_template_uuid
from ansible.module_utils.get_vapp_vm_template import get_vapp_vm_template_href
from ansible.module_utils.get_vapp_vm_template import get_vapp_vm_template_uuid
from ansible.module_utils.get_storage_profile import get_storagae_profile_href
from ansible.module_utils.get_compute_policy import get_compute_policy_href
from ansible.module_utils.get_vdc_id import get_vdc_id
from ansible.module_utils.get_vapp_template import get_vapp_template_uuid
from ansible.module_utils.get_vapp_id import get_vapp_id

def create_vm(client, vdc_name, catalogName, vapp_template_name, vapp_name, password, vm_list, network_name):
    vapp_id = get_vapp_id(client, vapp_name, vdc_name)
    uri = client.get_api_uri()
    url = f"{uri}/vApp/{vapp_id}/action/recomposeVApp"
    
    write_payload_to_file(client, vdc_name, catalogName, vapp_template_name, password, vm_list, network_name)

    file = open(r"payload.xml", "r")
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

def write_payload_to_file(client, vdc_name, catalogName, vapp_template_name, password, vm_list, network_name):
    vapp_template_uuid = get_vapp_template_uuid(client, catalogName, vapp_template_name)
    vapp_vm_template_href = get_vapp_vm_template_href(client, vapp_template_uuid)
    vapp_vm_template_uuid = get_vapp_vm_template_uuid(client, vapp_template_uuid)
    vdc_id = get_vdc_id(client, vdc_name)
    storagae_profile_href = get_storagae_profile_href(client, vdc_id)
    compute_policy_href = get_compute_policy_href(client, vdc_id)

    payload = f"""<?xml version="1.0" encoding="UTF-8"?>
<root:RecomposeVAppParams xmlns:root="http://www.vmware.com/vcloud/v1.5" xmlns:ns1="http://schemas.dmtf.org/ovf/envelope/1">
"""
    file= open(r'payload.xml', 'w')
    file.write(payload)
    file.close()
    for vm in vm_list:
        payload = f"""<root:SourcedItem>
        <root:Source href="{vapp_vm_template_href}" id="{vapp_vm_template_uuid}" name="{vm}" type="application/vnd.vmware.vcloud.vm+xml" />
        <root:InstantiationParams>
            <root:GuestCustomizationSection>
                <ns1:Info />
                <root:Enabled>true</root:Enabled>
                <root:ChangeSid>false</root:ChangeSid>
                <root:JoinDomainEnabled>false</root:JoinDomainEnabled>
                <root:UseOrgSettings>false</root:UseOrgSettings>
                <root:AdminPasswordEnabled>true</root:AdminPasswordEnabled>
                <root:AdminPasswordAuto>false</root:AdminPasswordAuto>
                <root:AdminPassword>{password}</root:AdminPassword>
                <root:AdminAutoLogonEnabled>false</root:AdminAutoLogonEnabled>
                <root:AdminAutoLogonCount>0</root:AdminAutoLogonCount>
                <root:ResetPasswordRequired>false</root:ResetPasswordRequired>
                <root:ComputerName>{vm}</root:ComputerName>
            </root:GuestCustomizationSection>
            <root:NetworkConnectionSection>
                <ns1:Info />
                <root:PrimaryNetworkConnectionIndex>0</root:PrimaryNetworkConnectionIndex>
                <root:NetworkConnection network="{network_name}">
                    <root:NetworkConnectionIndex>0</root:NetworkConnectionIndex>
                    <root:IsConnected>true</root:IsConnected>
                    <root:IpAddressAllocationMode>POOL</root:IpAddressAllocationMode>
                    <root:NetworkAdapterType>VMXNET3</root:NetworkAdapterType>
                </root:NetworkConnection>
            </root:NetworkConnectionSection>
        </root:InstantiationParams>
        <root:StorageProfile href="{storagae_profile_href}" type="application/vnd.vmware.vcloud.vdcStorageProfile+xml" />
    </root:SourcedItem>
"""
        file = open(r"payload.xml", "a")
        file.write("\t")
        file.write(payload)
        file.close()
    payload = """    <root:AllEULAsAccepted>true</root:AllEULAsAccepted>
</root:RecomposeVAppParams>"""
    file = open(r"payload.xml", "a")
    file.write(payload)
    file.close()
