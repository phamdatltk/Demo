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

from ansible.module_utils.create_master_slave import create_vm
import time
from ansible.module_utils.get_vapp_vm import get_vm_status
from ansible.module_utils.get_vapp_vm import get_vm_id
from ansible.module_utils.get_vapp_vm import check_busy_vcd
from ansible.module_utils.get_vapp_id import get_vapp_uuid

CREATE_VM_OPERATIONS = ['scale']
CREATE_VM_STATES = ['present']

def create_vm_argument_spec():
    return dict(
        vapp_name=dict(type='str', required=True),
        vm_password=dict(type='str', required=True),
        vm_master_count=dict(type=int, required=False),
        vm_worker_count=dict(type=int, required=False),
        vm_worker_add=dict(type=int, required=False),
        cluster_name=dict(type='str', required=True),
        cluster_id=dict(type='str', required=True),
        catalogName=dict(type='str', required=False),
        vapp_template_master_name=dict(type='str', required=False),
        vapp_template_worker_name=dict(type='str', required=False),
#        vapp_template_installer_name=dict(type='str', required=False),
#        vapp_template_keepalive_name=dict(type='str', required=False),
        network_name=dict(type='str', required=True),
        operation=dict(choices=CREATE_VM_OPERATIONS, required=False),
        state=dict(choices=CREATE_VM_STATES, required=False),
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
        if operation == 'scale':
            return self.scale_vm()

    def create_vm(self):
        params = self.params
        vm_master_count = params.get('vm_master_count')
        vm_worker_count = params.get('vm_worker_count')
        vm_password = params.get('vm_password')
        cluster_name = params.get('cluster_name')
        cluster_id = params.get('cluster_id')
        vapp_name = params.get('vapp_name')
        catalogName = params.get('catalogName')
        vapp_template_master_name = params.get('vapp_template_master_name')
        vapp_template_worker_name = params.get('vapp_template_worker_name')
#        vapp_template_installer_name = params.get('vapp_template_installer_name')
#        vapp_template_keepalive_name = params.get('vapp_template_keepalive_name')
        network_name = params.get('network_name')
        vdc = params.get('vdc')
        vms_list = list()

        for i in range(1, vm_master_count + 1):
            vm = f"{cluster_name}-{cluster_id}-master{i}"
            vms_list.append(vm)
        for i in range(1, vm_worker_count + 1):
            vm = f"{cluster_name}-{cluster_id}-slave{i}"
            vms_list.append(vm)
#        vms_list.append(f"{cluster_name}-{cluster_id}-installer")
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
            create_vm(self.client, vdc, catalogName, vapp_template_master_name, vapp_template_worker_name, vapp_name, vm_password, vms_list, network_name)
            #create_vm(self.client, vdc, catalogName, vapp_template_master_name, vapp_template_worker_name, vapp_template_installer_name, vapp_template_keepalive_name, vapp_name, vm_password, vms_list, network_name)
            time.sleep(10)
            vms_status = list()
            non_busy_vms = list()
            num_VM_powerOff = 0
            num_VM_powerOff_non_busy = 0
            for i in range(40):
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
                    time.sleep(5)
                    break
                else:
                    num_VM_powerOff = 0
                    num_VM_powerOff_non_busy = 0
                    vms_status = list()
                    non_busy_vms = list()
                    time.sleep(5)
                    continue
            
            
        return response

    def scale_vm(self):
        params = self.params
        vm_type = params.get('vm_type')
        vm_worker_count = params.get('vm_worker_count')
        vm_worker_add = params.get('vm_worker_add')
        vm_password = params.get('vm_password')
        cluster_name = params.get('cluster_name')
        cluster_id = params.get('cluster_id')
        vapp_name = params.get('vapp_name')
        catalogName = params.get('catalogName')
        vapp_template_worker_name = params.get('vapp_template_worker_name')
#        vapp_template_installer_name =  params.get('vapp_template_installer_name')
#        vapp_template_keepalive_name = params.get('vapp_template_keepalive_name')
        network_name = params.get('network_name')
        vdc = params.get('vdc')
        vms_list = list()

        for i in range(vm_worker_count + 1, vm_worker_count + vm_worker_add + 1):
            vm = f"{cluster_name}-{cluster_id}-worker{i}"
            vms_list.append(vm)

 #       vms_list.append(f"{cluster_name}-{cluster_id}-installer")
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
            create_vm_without_master(self.client, vdc, catalogName, vapp_template_worker_name, vapp_name, vm_password, vms_list, network_name)
            #create_vm_without_master(self.client, vdc, catalogName, vapp_template_worker_name, vapp_template_installer_name, vapp_template_keepalive_name, vapp_name, vm_password, vms_list, network_name)
            time.sleep(10)
            vms_status = list()
            num_VM_powerOff = 0
            non_busy_vms = list()
            num_VM_powerOff_non_busy = 0
            for i in range(40):
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
                    time.sleep(5)
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
        msg=dict(type='str'))
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
