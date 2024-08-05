import requests
from ansible.module_utils.requestInfo import RequestInfo


def connect_orgVdcNetwork_to_Vapp(client, vapp_id, orgVdcNetwork):
    params = RequestInfo(client)
    data = f"""<?xml version="1.0" encoding="UTF-8"?>
<root:NetworkConfigSection xmlns:root="http://www.vmware.com/vcloud/v1.5" xmlns:ns1="http://schemas.dmtf.org/ovf/envelope/1">
    <ns1:Info>The configuration parameters for logical networks</ns1:Info>
    <root:NetworkConfig networkName="{orgVdcNetwork['name']}">
        <root:Description>"{orgVdcNetwork['description']}"</root:Description>
        <root:Configuration>
            <root:IpScopes>
                <root:IpScope>
                    <root:IsInherited>true</root:IsInherited>
                    <root:Gateway>{orgVdcNetwork['subnets']['values'][0]['gateway']}</root:Gateway>
                    <root:SubnetPrefixLength>{orgVdcNetwork['subnets']['values'][0]['prefixLength']}</root:SubnetPrefixLength>
                    <root:Dns1>{orgVdcNetwork['subnets']['values'][0]['dnsServer1']}</root:Dns1>
                    <root:Dns2>{orgVdcNetwork['subnets']['values'][0]['dnsServer2']}</root:Dns2>
                    <root:DnsSuffix>{orgVdcNetwork['subnets']['values'][0]['dnsSuffix']}</root:DnsSuffix>
                    <root:IsEnabled>true</root:IsEnabled>
                </root:IpScope>
            </root:IpScopes>
            <root:ParentNetwork href="{params.api_url}/admin/network/{orgVdcNetwork['uuid']}" id="{orgVdcNetwork['id']}" name="{orgVdcNetwork['name']}" />
            <root:FenceMode>bridged</root:FenceMode>
            <root:AdvancedNetworkingEnabled>true</root:AdvancedNetworkingEnabled>
        </root:Configuration>
        <root:IsDeployed>false</root:IsDeployed>
    </root:NetworkConfig>
</root:NetworkConfigSection>"""

    resp = requests.put(
        f"{params.api_url}/vApp/{vapp_id}/networkConfigSection/",
        headers=params.xml_networkConfigSection_headers,
        data=data,
        verify=False
    )
    if not resp.ok:
        raise Exception(resp.content)
    return True
