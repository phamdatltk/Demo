# !/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'phongvd8@fpt.com.vn'
}

DOCUMENTATION = '''
---
module: getway_dnat_rule_service
short_description: Manage Affinity_rule's states/operations in vCloud Director
version_added: "1.0"
description:
    - Manage Affinity_rule's states/operations in vCloud Director

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
    vcd_url:
        description:
            - url of vCD
        required: true
    vdc:
        description:
            - Org Vdc where this VAPP gets created
        required: true
    anti_affinity_rule_name:
        description:
            - name of anti affinity rule
        required: true
    vapp_name:
        description:
            - name of vapp which container VM in vm_list
        required: false
    cluster_name:
        description:
            - name of K8S cluster
        required: true
    cluster_id:
        description:
            - id of K8S cluster
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
    vm_remove:
        description:
            - count of VM remove
        required: false
    state:
        description:
            - state of Edge Gateway DNAT rule (present/absent).
            - One from state or operation has to be provided.
        required: true

author:
    - phongvd8@fpt.com.vn
'''

EXAMPLES = '''
- name: create "test" anti-affinity rule
  anti_affinity_rule_service:
    vcd_url: "https://hn01vcd.fptcloud.com"
    anti_affinity_rule_name: "phongtest"
    vapp_name: "phong"
    vm_type: "master"
    vm_count: 3
    cluster_name: "phongvd8"
    cluster_id: "abcxyz"
    state: "present"

- name: delete "test" affinity rule
  anti_affinity_rule_service:
    vcd_url: "https://hn01vcd.fptcloud.com"
    anti_affinity_rule_name: "phongtest"
    state: "absent"

- name: udpate "phongtest" anti-affinity rule
  anti_affinity_rule_service:
    vcd_url: "https://hn01vcd.fptcloud.com"
    anti_affinity_rule_name: "phongtest"
    vapp_name: "phong"
    vm_type: "master"
    vm_count: 3
    vm_remove: 1
    cluster_name: "phongvd8"
    cluster_id: "abcxyz"
    state: "update"

- name: udpate "phongtest" anti-affinity rule
  anti_affinity_rule_service:
    vcd_url: "https://hn01vcd.fptcloud.com"
    anti_affinity_rule_name: "phongtest"
    vapp_name: "phong"
    vm_type: "master"
    vm_count: 2
    vm_add: 1
    cluster_name: "phongvd8"
    cluster_id: "abcxyz"
    state: "update"
'''

RETURN = '''
msg: success/failure message corresponding to Anti Affinity rule state/operation
changed: true if resource has been changed else false
'''

from ansible.module_utils.vcd import VcdAnsibleModule

from ansible.module_utils.get_vdc_id import get_vdc_id
from ansible.module_utils.get_vapp_id import get_vapp_uuid

from ansible.module_utils.anti_affinity_vm import create_anti_affinity_rule
from ansible.module_utils.anti_affinity_vm import update_anti_affinity_rule
from ansible.module_utils.get_anti_affinity_rule_id import get_anti_affinity_rule_id
from ansible.module_utils.delete_anti_affinity_rule import delete_anti_affinity_rule
import time

AFFINITY_RULE_STATES = ['present', 'absent', 'update']

def affinity_rule_argument_spec():
    return dict(
        vapp_name=dict(type='str', required=False),
        vcd_url=dict(type='str', required=True),
        vm_type=dict(type='str', required=False),
        vm_count=dict(type=int, required=False),
        vm_add=dict(type=int, required=False),
        vm_remove=dict(type=int, required=False),
        cluster_name=dict(type='str', required=False),
        cluster_id=dict(type='str', required=False),
        anti_affinity_rule_name=dict(type='str', required=True),
        state=dict(choices=AFFINITY_RULE_STATES, required=True),
    )

class Affinity_Rule(VcdAnsibleModule):
    def __init__(self, **kwargs):
        super(Affinity_Rule, self).__init__(**kwargs)
        self.vdc_id = get_vdc_id(self.client, self.params['vdc'])
        self.vapp_uuid = get_vapp_uuid(self.client, self.params['vapp_name'], self.params['vdc'])

    def manage_states(self):
        state = self.params.get('state')
        if state == 'absent':
            return self.delete()
        if state == 'present':
            return self.create()
        if state == 'update':
            return self.update()

    def create(self):
        params = self.params
        vapp_name=params.get('vapp_name')
        vcd_url=params.get('vcd_url')
        vm_type = params.get('vm_type')
        vm_count = params.get('vm_count')
        cluster_name = params.get('cluster_name')
        cluster_id = params.get('cluster_id')
        vdc_name = params.get('vdc')
        vms_list=list()
        anti_affinity_rule_name=params.get('anti_affinity_rule_name')
        response = dict()
        response['changed'] = False
        anti_affinity_rule_id = get_anti_affinity_rule_id(self.client, vcd_url, self.vdc_id, anti_affinity_rule_name)
        if anti_affinity_rule_id != "":
            delete_anti_affinity_rule(self.client, vcd_url, anti_affinity_rule_id)
            time.sleep(5)
        if vm_count == 1:
            response['warnings'] = "Count of {} VMs must be greater than 1.".format(vm_type)
        elif vm_count > 1:
            for i in range(1, vm_count + 1):
                vm = f"{cluster_name}-{cluster_id}-{vm_type}{i}"
                vms_list.append(vm)
            create_anti_affinity_rule(self.client, self.vdc_id, self.vapp_uuid, vapp_name, anti_affinity_rule_name, vms_list, vdc_name)
            response['msg'] = 'Anti Affinity Rule {} has been created.'.format(anti_affinity_rule_name)
            response['changed'] = True
        time.sleep(5)
        return response

    def delete(self):
        response = dict()
        response['changed'] = False
        params = self.params
        anti_affinity_rule_name=params.get('anti_affinity_rule_name')
        vcd_url=params.get('vcd_url')
        anti_affinity_rule_id = get_anti_affinity_rule_id(self.client, vcd_url, self.vdc_id, anti_affinity_rule_name)
        if anti_affinity_rule_id == "":
            response['warnings'] = "Anti Affinity Rule {} is not present.".format(anti_affinity_rule_name)
        else:
            delete_anti_affinity_rule(self.client, vcd_url, anti_affinity_rule_id)
            response['msg'] = 'Anti Affinity Rule {} has been deleted.'.format(anti_affinity_rule_name)
            response['changed'] = True
        return response

    def update(self):
        params = self.params
        vapp_name=params.get('vapp_name')
        vcd_url=params.get('vcd_url')
        vm_type = params.get('vm_type')
        vm_count = params.get('vm_count')
        vm_add = params.get('vm_add')
        vm_remove = params.get('vm_remove')
        cluster_name = params.get('cluster_name')
        cluster_id = params.get('cluster_id')
        vdc_name = params.get('vdc')
        vms_list=list()
        anti_affinity_rule_name=params.get('anti_affinity_rule_name')
        response = dict()
        response['changed'] = False
        if vm_count == 1 and vm_add != None:
            for i in range(1, vm_count + vm_add + 1):
                vm = f"{cluster_name}-{cluster_id}-{vm_type}{i}"
                vms_list.append(vm)
            create_anti_affinity_rule(self.client, self.vdc_id, self.vapp_uuid, vapp_name, anti_affinity_rule_name, vms_list, vdc_name)
            response['msg'] = 'Anti Affinity Rule {} has been created.'.format(anti_affinity_rule_name)
            response['changed'] = True
            time.sleep(5)
        if vm_remove != None and (vm_count - vm_remove) == 1:
            anti_affinity_rule_id = get_anti_affinity_rule_id(self.client, vcd_url, self.vdc_id, anti_affinity_rule_name)
            if anti_affinity_rule_id == "":
                response['warnings'] = "Anti Affinity Rule {} is not present.".format(anti_affinity_rule_name)
            else:
                delete_anti_affinity_rule(self.client, vcd_url, anti_affinity_rule_id)
                response['msg'] = 'Anti Affinity Rule {} has been deleted.'.format(anti_affinity_rule_name)
                response['changed'] = True
                time.sleep(5)
        if vm_count > 1 and vm_add != None:
            for i in range(1, vm_count + vm_add + 1):
                vm = f"{cluster_name}-{cluster_id}-{vm_type}{i}"
                vms_list.append(vm)
            anti_affinity_rule_id = get_anti_affinity_rule_id(self.client, vcd_url, self.vdc_id, anti_affinity_rule_name)
            if anti_affinity_rule_id == "":
                msg = "Anti Affinity Rule {} is not present"
                response['warnings'] = msg.format(anti_affinity_rule_name)
            else:
                update_anti_affinity_rule(self.client, self.vapp_uuid, vapp_name, anti_affinity_rule_name, anti_affinity_rule_id, vms_list, vdc_name)
                msg = 'Anti Affinity Rule {} has been updated'
                response['msg'] = msg.format(anti_affinity_rule_name)
                response['changed'] = True
                time.sleep(5)
        if vm_remove != None and (vm_count - vm_remove) > 1:
            for i in range(1, vm_count - vm_remove + 1):
                vm = f"{cluster_name}-{cluster_id}-{vm_type}{i}"
                vms_list.append(vm)
            anti_affinity_rule_id = get_anti_affinity_rule_id(self.client, vcd_url, self.vdc_id, anti_affinity_rule_name)
            if anti_affinity_rule_id == "":
                msg = "Anti Affinity Rule {} is not present"
                response['warnings'] = msg.format(anti_affinity_rule_name)
            else:
                update_anti_affinity_rule(self.client, self.vapp_uuid, vapp_name, anti_affinity_rule_name, anti_affinity_rule_id, vms_list, vdc_name)
                msg = 'Anti Affinity Rule {} has been updated'
                response['msg'] = msg.format(anti_affinity_rule_name)
                response['changed'] = True
                time.sleep(5)
        return response

def main():
    argument_spec = affinity_rule_argument_spec()
    response = dict(msg=dict(type='str'))
    module = Affinity_Rule(argument_spec=argument_spec, supports_check_mode=True)

    try:
        if module.check_mode:
            response = dict()
            response['changed'] = False
            response['msg'] = "skipped, running in check mode"
            response['skipped'] = True
        elif module.params.get('state'):
            response = module.manage_states()
        else:
            raise Exception('Please provide state for resource')
    except Exception as error:
        response['msg'] = error
        module.fail_json(**response)
    else:
        module.exit_json(**response)
    
if __name__ == '__main__':
    main()