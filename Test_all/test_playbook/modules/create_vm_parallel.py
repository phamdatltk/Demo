# !/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'phongvd8@fpt.com.vn'
}

DOCUMENTATION = '''
---
module: create_vm_parallel
short_description: create vm parrallel in vCloud Director
version_added: "1.0"
description:
    - Create vm parrallel in vCloud Director

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
        required: false
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
  create_vm_parallel:
    vapp_name: "phong"
    vm_type: "master"
    vm_count: 3
    vm_password: "12345678a"
    cluster_name: "phongvd8"
    cluster_id: "abcxyz"
    catalogName: "fke-stg"
    vapp_template_name: "fke-118-master-v1-1-08122021"
    network_name: "fke-subnet-192-101"
    state: "present"

- name: scale up VM parrallel
  create_vm_parallel:
    vapp_name: "phong"
    vm_type: "master"
    vm_count: 3
    vm_add: 3
    vm_password: "12345678a"
    cluster_name: "phongvd8"
    cluster_id: "abcxyz"
    catalogName: "fke-stg"
    vapp_template_name: "fke-118-master-v1-1-08122021"
    network_name: "fke-subnet-192-101"
    operation: 'scale'
'''

RETURN = '''
msg: success/failure message corresponding to Create_VM_parrallel state/operation
changed: true if resource has been changed else false
'''

from ansible.module_utils.vcd import VcdAnsibleModule

from ansible.module_utils.create_vm_parallel import create_vm
import time
from ansible.module_utils.get_vapp_vm import get_vm_status
from ansible.module_utils.get_vapp_vm import get_vm_id
from ansible.module_utils.get_vapp_id import get_vapp_uuid

CREATE_VM_OPERATIONS = ['scale']
CREATE_VM_STATES = ['present']

def create_vm_argument_spec():
    return dict(
        vapp_name=dict(type='str', required=True),
        vm_type=dict(type='str', required=True),
        vm_password=dict(type='str', required=True),
        vm_count=dict(type=int, required=False),
        vm_add=dict(type=int, required=False),
        cluster_name=dict(type='str', required=True),
        cluster_id=dict(type='str', required=True),
        catalogName=dict(type='str', required=True),
        vapp_template_name=dict(type='str', required=True),
        network_name=dict(type='str', required=True),
        operation=dict(choices=CREATE_VM_OPERATIONS, required=False),
        state=dict(choices=CREATE_VM_STATES, required=False),
    )

class Create_VM_Parrallel(VcdAnsibleModule):
    def __init__(self, **kwargs):
        super(Create_VM_Parrallel, self).__init__(**kwargs)
    
    def manage_states(self):    
        state = self.params.get('state')

        if state == 'present':
            return self.create_vm()

    def manage_operations(self):
        operation = self.params.get('operation')
        if operation == 'scale':
            return self.scale_vm()

    def create_vm(self):
        params = self.params
        vm_type = params.get('vm_type')
        vm_count = params.get('vm_count')
        vm_password = params.get('vm_password')
        cluster_name = params.get('cluster_name')
        cluster_id = params.get('cluster_id')
        vapp_name = params.get('vapp_name')
        catalogName = params.get('catalogName')
        vapp_template_name = params.get('vapp_template_name')
        network_name = params.get('network_name')
        vdc = params.get('vdc')
        vms_list = list()
        if vm_type == "master" or vm_type == "worker":
            for i in range(1, vm_count + 1):
                vm = f"{cluster_name}-{cluster_id}-{vm_type}{i}"
                vms_list.append(vm)
        else:
            vm = f"{cluster_name}-{cluster_id}-{vm_type}"
            vms_list.append(vm)
        response = dict()
        response['changed'] = True
        vapp_uuid = get_vapp_uuid(self.client, vapp_name, vdc)
        vms_id = list()
        num_vm_id_diff_empty = 0
        
        for vm in vms_list:
            vm_id = get_vm_id(self.client, vapp_uuid, vm)
            vms_id.append(vm_id)
        for vm_id in vms_id:
            if vm_id != "":
                num_vm_id_diff_empty += 1
        if num_vm_id_diff_empty == len(vms_id):
            response['changed'] = False
            response['msg'] = 'VMs has been created.'
        else:
            create_vm(self.client, vdc, catalogName, vapp_template_name, vapp_name, vm_password, vms_list, network_name)
            time.sleep(10)
            vms_status = list()
            num_VM_powerOff = 0
            for i in range(20):
                for vm in vms_list:
                    vm_status = get_vm_status(self.client, vapp_uuid, vm)
                    vms_status.append(vm_status)
                for status in vms_status:
                    if status == "POWERED_OFF":
                        num_VM_powerOff += 1
                if num_VM_powerOff == len(vms_status):
                    time.sleep(10)
                    break
                else:
                    num_VM_powerOff = 0
                    vms_status = list()
                    time.sleep(5)
                    continue
            time.sleep(10)
            
        return response

    def scale_vm(self):
        params = self.params
        vm_type = params.get('vm_type')
        vm_count = params.get('vm_count')
        vm_add = params.get('vm_add')
        vm_password = params.get('vm_password')
        cluster_name = params.get('cluster_name')
        cluster_id = params.get('cluster_id')
        vapp_name = params.get('vapp_name')
        catalogName = params.get('catalogName')
        vapp_template_name = params.get('vapp_template_name')
        network_name = params.get('network_name')
        vdc = params.get('vdc')
        vms_list = list()
        if vm_type == "master" or vm_type == "worker":
            for i in range(vm_count + 1, vm_count + vm_add + 1):
                vm = f"{cluster_name}-{cluster_id}-{vm_type}{i}"
                vms_list.append(vm)
        else:
            vm = f"{cluster_name}-{cluster_id}-{vm_type}"
            vms_list.append(vm)
        response = dict()
        response['changed'] = True
        vapp_uuid = get_vapp_uuid(self.client, vapp_name, vdc)
        vms_id = list()
        num_vm_id_diff_empty = 0
        
        for vm in vms_list:
            vm_id = get_vm_id(self.client, vapp_uuid, vm)
            vms_id.append(vm_id)
        for vm_id in vms_id:
            if vm_id != "":
                num_vm_id_diff_empty += 1
        if num_vm_id_diff_empty == len(vms_id):
            response['changed'] = False
            response['msg'] = 'VMs has been created.'
        else:
            create_vm(self.client, vdc, catalogName, vapp_template_name, vapp_name, vm_password, vms_list, network_name)
            time.sleep(10)
            vms_status = list()
            num_VM_powerOff = 0
            for i in range(20):
                for vm in vms_list:
                    vm_status = get_vm_status(self.client, vapp_uuid, vm)
                    vms_status.append(vm_status)
                for status in vms_status:
                    if status == "POWERED_OFF":
                        num_VM_powerOff += 1
                if num_VM_powerOff == len(vms_status):
                    time.sleep(10)
                    break
                else:
                    num_VM_powerOff = 0
                    vms_status = list()
                    time.sleep(5)
                    continue
            time.sleep(10)
                    
        return response


def main():
    argument_spec = create_vm_argument_spec()
    response = dict(
        msg=dict(type='str'))
    module = Create_VM_Parrallel(argument_spec=argument_spec, supports_check_mode=True)

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
