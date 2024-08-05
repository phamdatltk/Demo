import requests

from ansible.module_utils.requestInfo import RequestInfo
from ansible.module_utils.get_vapp_vm import get_vm_id
from ansible.module_utils.get_vapp_id import get_vapp_uuid
from ansible.module_utils.get_vdc_id import get_vdc_id
from ansible.module_utils.get_storage_profile import get_storage_profile_href
from ansible.module_utils.get_compute_policy import get_system_default_compute_policy_href, get_placement_policy

def reconfigure_vm_cpu(client, vdc_name, vapp_name, vm_name, num_cpus, storage_profile_name, hardware_version):
    uri = client.get_api_uri()
    vapp_uuid = get_vapp_uuid(client, vapp_name, vdc_name)
    vm_id = get_vm_id(client, vapp_uuid, vm_name)
    vm_uuid = vm_id.replace("vm-", '')
    vdc_id = get_vdc_id(client, vdc_name)
    storage_profile_href = get_storage_profile_href(client, vdc_id, storage_profile_name)

    compute_policy_href = ""
    compute_policy_href = get_system_default_compute_policy_href(client, vdc_id)
    VmSizingPolicy = f"""<root:VmSizingPolicy href="{compute_policy_href}"/>"""


    placement_policy_href = get_placement_policy(client, vdc_id)
    if placement_policy_href == "":
        VmPlacementPolicy = ""
    else:
        VmPlacementPolicy = f"""<root:VmPlacementPolicy href="{placement_policy_href}" id="{placement_policy_href}"/>"""


    url = f"{uri}/vApp/{vm_id}/action/reconfigureVm"

    payload = f"""<?xml version="1.0" encoding="UTF-8"?>
<root:Vm xmlns:root="http://www.vmware.com/vcloud/v1.5" xmlns:ns4="http://schemas.dmtf.org/ovf/envelope/1" xmlns:ns5="http://www.vmware.com/schema/ovf" id="urn:vcloud:vm:{vm_uuid}" name="{vm_name}">
    <ns4:OperatingSystemSection ns4:id="102" ns5:osType="ubuntu64Guest">
        <ns4:Info>Specifies the operating system installed</ns4:Info>
        <ns4:Description>Ubuntu Linux (64-bit)</ns4:Description>
    </ns4:OperatingSystemSection>
    <root:VmSpecSection Modified="true">
        <ns4:Info>Virtual hardware requirements (simplified)</ns4:Info>
        <root:OsType>ubuntu64Guest</root:OsType>
        <root:NumCpus>{num_cpus}</root:NumCpus>
        <root:NumCoresPerSocket>1</root:NumCoresPerSocket>
        <root:CpuResourceMhz>
            <root:Configured>2</root:Configured>
        </root:CpuResourceMhz>
        <root:MediaSection>
            <root:MediaSettings>
                <root:DeviceId>3000</root:DeviceId>
                <root:MediaType>ISO</root:MediaType>
                <root:MediaState>DISCONNECTED</root:MediaState>
                <root:UnitNumber>0</root:UnitNumber>
                <root:BusNumber>0</root:BusNumber>
            </root:MediaSettings>
            <root:MediaSettings>
                <root:DeviceId>8000</root:DeviceId>
                <root:MediaType>FLOPPY</root:MediaType>
                <root:MediaState>DISCONNECTED</root:MediaState>
                <root:UnitNumber>0</root:UnitNumber>
                <root:BusNumber>0</root:BusNumber>
            </root:MediaSettings>
        </root:MediaSection>
        <root:HardwareVersion>{hardware_version}</root:HardwareVersion>
        <root:VirtualCpuType>VM64</root:VirtualCpuType>
    </root:VmSpecSection>
    <root:VmCapabilities>
        <root:MemoryHotAddEnabled>true</root:MemoryHotAddEnabled>
        <root:CpuHotAddEnabled>true</root:CpuHotAddEnabled>
    </root:VmCapabilities>
    <root:StorageProfile href="{storage_profile_href}" name="{storage_profile_name}" />
    <root:ComputePolicy>
		{VmPlacementPolicy}
		{VmSizingPolicy}
	</root:ComputePolicy>
    <root:BootOptions>
        <root:BootDelay>0</root:BootDelay>
        <root:EnterBIOSSetup>false</root:EnterBIOSSetup>
    </root:BootOptions>
</root:Vm>"""

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


def reconfigure_vm_memory(client, vdc_name, vapp_name, vm_name, memory_resource, storage_profile_name, hardware_version, placement_policy_name):
    uri = client.get_api_uri()
    vapp_uuid = get_vapp_uuid(client, vapp_name, vdc_name)
    vm_id = get_vm_id(client, vapp_uuid, vm_name)
    vm_uuid = vm_id.replace("vm-", '')
    vdc_id = get_vdc_id(client, vdc_name)
    storage_profile_href = get_storage_profile_href(client, vdc_id, storage_profile_name)

    compute_policy_href = ""
    compute_policy_href = get_system_default_compute_policy_href(client, vdc_id)
    placement_policy_href = get_placement_policy(client, vdc_id, placement_policy_name)
    VmSizingPolicy = f"""<root:VmSizingPolicy href="{compute_policy_href}"/>"""

    # placement_policy_href = get_placement_policy(client, vdc_id)
    if placement_policy_href == "":
        VmPlacementPolicy = ""
    else:
        VmPlacementPolicy = f"""<root:VmPlacementPolicy href="{placement_policy_href}" id="{placement_policy_href}"/>"""

    url = f"{uri}/vApp/{vm_id}/action/reconfigureVm"
    payload = f"""<?xml version="1.0" encoding="UTF-8"?>
<root:Vm xmlns:root="http://www.vmware.com/vcloud/v1.5" xmlns:ns4="http://schemas.dmtf.org/ovf/envelope/1" xmlns:ns5="http://www.vmware.com/schema/ovf" id="urn:vcloud:vm:{vm_uuid}" name="{vm_name}">
    <ns4:OperatingSystemSection ns4:id="102" ns5:osType="ubuntu64Guest">
        <ns4:Info>Specifies the operating system installed</ns4:Info>
        <ns4:Description>Ubuntu Linux (64-bit)</ns4:Description>
    </ns4:OperatingSystemSection>
    <root:VmSpecSection Modified="true">
        <ns4:Info>Virtual hardware requirements (simplified)</ns4:Info>
        <root:OsType>ubuntu64Guest</root:OsType>
        <root:MemoryResourceMb>
            <root:Configured>{memory_resource}</root:Configured>
        </root:MemoryResourceMb>
        <root:MediaSection>
            <root:MediaSettings>
                <root:DeviceId>3000</root:DeviceId>
                <root:MediaType>ISO</root:MediaType>
                <root:MediaState>DISCONNECTED</root:MediaState>
                <root:UnitNumber>0</root:UnitNumber>
                <root:BusNumber>0</root:BusNumber>
            </root:MediaSettings>
            <root:MediaSettings>
                <root:DeviceId>8000</root:DeviceId>
                <root:MediaType>FLOPPY</root:MediaType>
                <root:MediaState>DISCONNECTED</root:MediaState>
                <root:UnitNumber>0</root:UnitNumber>
                <root:BusNumber>0</root:BusNumber>
            </root:MediaSettings>
        </root:MediaSection>
        <root:HardwareVersion>{hardware_version}</root:HardwareVersion>
        <root:VirtualCpuType>VM64</root:VirtualCpuType>
    </root:VmSpecSection>
    <root:VmCapabilities>
        <root:MemoryHotAddEnabled>true</root:MemoryHotAddEnabled>
        <root:CpuHotAddEnabled>true</root:CpuHotAddEnabled>
    </root:VmCapabilities>
    <root:StorageProfile href="{storage_profile_href}" name="{storage_profile_name}" />
    <root:ComputePolicy>
		{VmPlacementPolicy}
		{VmSizingPolicy}
	</root:ComputePolicy>
    <root:BootOptions>
        <root:BootDelay>0</root:BootDelay>
        <root:EnterBIOSSetup>false</root:EnterBIOSSetup>
    </root:BootOptions>
</root:Vm>"""

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

def reconfigure_vm_cpu_memory(client, vdc_name, vapp_name, vm_name, num_cpus, memory_resource, storage_profile_name, hardware_version, placement_policy_name):
    uri = client.get_api_uri()
    vapp_uuid = get_vapp_uuid(client, vapp_name, vdc_name)
    vm_id = get_vm_id(client, vapp_uuid, vm_name)
    vm_uuid = vm_id.replace("vm-", '')
    vdc_id = get_vdc_id(client, vdc_name)
    storage_profile_href = get_storage_profile_href(client, vdc_id, storage_profile_name)

    compute_policy_href = ""
    compute_policy_href = get_system_default_compute_policy_href(client, vdc_id)
    VmSizingPolicy = f"""<root:VmSizingPolicy href="{compute_policy_href}"/>"""

    # placement_policy_href = get_placement_policy(client, vdc_id)
    placement_policy_href = get_placement_policy(client, vdc_id, placement_policy_name)

    if placement_policy_href == "":
        VmPlacementPolicy = ""
    else:
        VmPlacementPolicy = f"""<root:VmPlacementPolicy href="{placement_policy_href}" id="{placement_policy_href}"/>"""

    url = f"{uri}/vApp/{vm_id}/action/reconfigureVm"

    payload = f"""<?xml version="1.0" encoding="UTF-8"?>
<root:Vm xmlns:root="http://www.vmware.com/vcloud/v1.5" xmlns:ns4="http://schemas.dmtf.org/ovf/envelope/1" xmlns:ns5="http://www.vmware.com/schema/ovf" id="urn:vcloud:vm:{vm_uuid}" name="{vm_name}">
    <ns4:OperatingSystemSection ns4:id="102" ns5:osType="ubuntu64Guest">
        <ns4:Info>Specifies the operating system installed</ns4:Info>
        <ns4:Description>Ubuntu Linux (64-bit)</ns4:Description>
    </ns4:OperatingSystemSection>
    <root:VmSpecSection Modified="true">
        <ns4:Info>Virtual hardware requirements (simplified)</ns4:Info>
        <root:OsType>ubuntu64Guest</root:OsType>
        <root:NumCpus>{num_cpus}</root:NumCpus>
        <root:NumCoresPerSocket>1</root:NumCoresPerSocket>
        <root:CpuResourceMhz>
            <root:Configured>2</root:Configured>
        </root:CpuResourceMhz>
        <root:MemoryResourceMb>
            <root:Configured>{memory_resource}</root:Configured>
        </root:MemoryResourceMb>
        <root:MediaSection>
            <root:MediaSettings>
                <root:DeviceId>3000</root:DeviceId>
                <root:MediaType>ISO</root:MediaType>
                <root:MediaState>DISCONNECTED</root:MediaState>
                <root:UnitNumber>0</root:UnitNumber>
                <root:BusNumber>0</root:BusNumber>
            </root:MediaSettings>
            <root:MediaSettings>
                <root:DeviceId>8000</root:DeviceId>
                <root:MediaType>FLOPPY</root:MediaType>
                <root:MediaState>DISCONNECTED</root:MediaState>
                <root:UnitNumber>0</root:UnitNumber>
                <root:BusNumber>0</root:BusNumber>
            </root:MediaSettings>
        </root:MediaSection>
        <root:HardwareVersion>{hardware_version}</root:HardwareVersion>
        <root:VirtualCpuType>VM64</root:VirtualCpuType>
    </root:VmSpecSection>
    <root:VmCapabilities>
        <root:MemoryHotAddEnabled>true</root:MemoryHotAddEnabled>
        <root:CpuHotAddEnabled>true</root:CpuHotAddEnabled>
    </root:VmCapabilities>
    <root:StorageProfile href="{storage_profile_href}" name="{storage_profile_name}" />
    <root:ComputePolicy>
		{VmPlacementPolicy}
		{VmSizingPolicy}
	</root:ComputePolicy>
    <root:BootOptions>
        <root:BootDelay>0</root:BootDelay>
        <root:EnterBIOSSetup>false</root:EnterBIOSSetup>
    </root:BootOptions>
</root:Vm>"""
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