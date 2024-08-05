# !/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'phongvd8@fpt.com.vn'
}

DOCUMENTATION = '''
---
module: create_vm
short_description: create vm in vCloud Director
version_added: "1.0"
description:
    - Create vm in vCloud Director

options:
    user:
        description:
            - vCloud Director user name
        required: false
    password:
        description:
            - vCloud Director user password
        required: false
    host:
        description:
            - vCloud Director host address
        required: false
    org:
        description:
            - Organization name on vCloud Director to access
        required: false
    api_version:
        description:
            - Pyvcloud API version
        required: false
    verify_ssl_certs:
        description:
            - whether to use secure connection to vCloud Director host
        required: false
    org_name:
        description:
            - target org name
            - required for service providers to create resources in other orgs
            - default value is module level / environment level org
        required: false
    vdc:
        description:
            - Org Vdc where this VAPP gets created
        required: true
    vapp_name:
        description:
            - name of vapp which contains VMs
        required: true
    catalogName:
        description:
            - name of catalog
        required: true
    vapp_template_name:
        description:
            - name of vApp template
        required: true
    vm_password:
        description:
            - password of VM
        required: true
    cluster_name:
        description:
            - name of K8S cluster
        required: true
    cluster_id:
        description:
            - id of K8S cluster
        required: true
    network_name:
        description:
            - name of internal network
        required: true
    vm_type:
        description:
            - type of VM (master, worker, installer, nfs)
        required: true
    vm_count:
        description:
            - count of VM
        required: true
    vm_add:
        description:
            - count of VM addition
        required: false       
    operation:
        description:
            - operation of Create_vm_parallel.
        required: false
    state:
        description:
            - state of Create_vm_parallel.
        required: false

author:
    - phongvd8@fpt.com.vn
'''

EXAMPLES = '''
- name: create VM parrallel
  create_vm:
    vapp_name: "phong"
    vm_master_count: 1
    vm_worker_count: 1
    vm_password: "12345678a"
    cluster_name: "phongvd8"
    cluster_id: "abcxyz"
    catalogName: "fke-prod"
    vapp_template_master_name: "fke-120-master-v1-1-08122021"
    vapp_template_worker_name: "fke-120-worker-v1-1-08122021"
    vapp_template_installer_name: "fke-installer-v1-29112021"
    network_name: "fke-pilot-72gexaso"
    state: "present"

- name: scale up VM
  create_vm:
    vapp_name: "phong"
    vm_worker_count: 1
    vm_worker_add: 1
    vm_password: "12345678a"
    cluster_name: "phongvd8"
    cluster_id: "abcxyz"
    catalogName: "fke-prod"
    vapp_template_worker_name: "fke-120-worker-v1-1-08122021"
    vapp_template_installer_name: "fke-installer-v1-29112021"
    network_name: "fke-pilot-72gexaso"
    operation: "scale"
'''

RETURN = '''
msg: success/failure message corresponding to Create_VM_parrallel state/operation
changed: true if resource has been changed else false
'''
from ansible.module_utils.vcd import VcdAnsibleModule
from ansible.module_utils.create_clickhouse import create_vm
import time
from ansible.module_utils.get_vapp_vm import get_vm_status
from ansible.module_utils.get_vapp_vm import check_busy_vcd
from ansible.module_utils.get_vapp_id import get_vapp_uuid
from ansible.module_utils.util import list_vm_clickhouse
import http.client
http.client._MAXHEADERS = 1000

CREATE_VM_OPERATIONS = ['scale']
CREATE_VM_STATES = ['present']

CREATE_VM_OPERATIONS = ['create', 'scale', 'reserve']
CREATE_VM_STATES = ['present']


def create_vm_argument_spec():
    return dict(
        cluster_name=dict(type='str', required=True),
        cluster_id=dict(type='str', required=True),
        is_cluster=dict(type='str', required=True),
        number_of_shard=dict(type=int, required=True),
        from_catalogName=dict(type='str', required=False),
        from_vappName=dict(type='str', required=False),
        network_name=dict(type='str', required=True),
        storage_profile_name=dict(type='str', required=True),
        operation=dict(choices=CREATE_VM_OPERATIONS, required=False),
        state=dict(choices=CREATE_VM_STATES, required=False),
        placement_policy_name=dict(type='str', required=False)
    )

class Create_VM(VcdAnsibleModule):
    def __init__(self, **kwargs):
        super(Create_VM, self).__init__(**kwargs)

    def manage_states(self):
        state = self.params.get('state')
        if state == 'present':
            return self.create_vm()

    def manage_operations(self):
        operation = self.params.get('operation')
        if operation == 'create':
            return self.create_vm()

    def create_vm(self):
        params = self.params
        cluster_name = params.get('cluster_name')
        cluster_id = params.get('cluster_id')
        catalogName = params.get('from_catalogName')
        vapp_template_name = params.get('from_vappName')
        storage_profile_name = params.get('storage_profile_name')
        network_name = params.get('network_name')
        placement_policy_name = params.get('placement_policy_name')
        vdc = params.get('vdc')
        response = dict()
        vapp_name = f"{cluster_name}-{cluster_id}"
        response['changed'] = True
        is_cluster = params.get('is_cluster')
        number_of_shard = params.get('number_of_shard')
        vms_list = list_vm_clickhouse(cluster_name, cluster_id, is_cluster,number_of_shard)
        create_vm(self.client, vdc, catalogName, vapp_template_name, vapp_name, vms_list, network_name, storage_profile_name, placement_policy_name)
        time.sleep(10)
        vms_status = list()
        non_busy_vms = list()
        num_VM_powerOff = 0
        num_VM_powerOff_non_busy = 0
        vapp_uuid = get_vapp_uuid(self.client, vapp_name, vdc)
        for i in range(400):
            for vm in vms_list:
                vm_status = get_vm_status(self.client, vapp_uuid, vm)
                vms_status.append(vm_status)
                non_busy_vm = check_busy_vcd(self.client, vapp_uuid, vm)
                non_busy_vms.append(non_busy_vm)
            for status in vms_status:
                if status == "POWERED_OFF":
                    num_VM_powerOff += 1
            for busy in non_busy_vms:
                if busy == "false":
                    num_VM_powerOff_non_busy += 1
            if num_VM_powerOff == len(vms_status) and num_VM_powerOff_non_busy == len(non_busy_vms):
                time.sleep(3)
                break
            else:
                num_VM_powerOff = 0
                num_VM_powerOff_non_busy = 0
                vms_status = list()
                non_busy_vms = list()
                time.sleep(5)
                continue
        return response
def main():
    argument_spec = create_vm_argument_spec()
    response = dict(
        msg=dict(type='str')
    )
    module = Create_VM(argument_spec=argument_spec, supports_check_mode=True)
    try:
        if module.check_mode:
            response = dict()
            response['changed'] = False
            response['msg'] = "skipped, running in check mode"
            response['skipped'] = True
        elif module.params.get('state'):
            response = module.manage_states()
        elif module.params.get('operation'):
            response = module.manage_operations()
        else:
            raise Exception('Please provide state for resource')
    except Exception as error:
        response['msg'] = error
        module.fail_json(**response)
    else:
        module.exit_json(**response)

if __name__ == '__main__':
    main()
