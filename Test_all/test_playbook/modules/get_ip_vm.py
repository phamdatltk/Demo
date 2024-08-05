# !/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'phongvd8@fpt.com.vn'
}

DOCUMENTATION = '''
---
module: getway_dnat_rule_service
short_description: Get ip of vm in vCloud Director
version_added: "1.0"
description:
    - Get ip of vm in vCloud Director

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
    vm_type:
        description:
            - type of vm name in Vapp
        required: true
    vm_count:
        description:
            - count of vm name in Vapp
        required: true
    cluster_name:
        description:
            - name of K8S cluster
        required: true
    cluster_id:
        description:
            - id of K8S cluster
        required: true
    state:
        description:
            - state of lb pool member update (present).
            - One from state or operation has to be provided.
        required: false

author:
    - phongvd8@fpt.com.vn
'''

EXAMPLES = '''
- name: Get ip Worker
  get_ip_vm:
    vapp_name: "thanhtv30-78n7xl6i"
    vm_type: "worker"
    vm_count: 1
    cluster_name: "thanhtv30"
    cluster_id: "78n7xl6i"
  register: output
  tags: get-ip-worker

- name: print ip output
  debug:
    msg: "{{output.ip}}"
'''

RETURN = '''
msg: success/failure message corresponding to Get_VM_IP state/operation
changed: true if resource has been changed else false
ip: list of ip belongs to vms in vms_list
Example return value:
        "changed": true,
        "failed": false,
        "ip": [
            "10.0.0.3",
            "10.0.0.2"
        ]
'''

from ansible.module_utils.vcd import VcdAnsibleModule

from ansible.module_utils.get_vapp_id import get_vapp_uuid
from ansible.module_utils.get_vapp_vm import get_vm_ip

GET_IP_VM_STATES = ['present']

def get_ip_vm_argument_spec():
    return dict(
        vapp_name=dict(type='str', required=True),
        vm_type=dict(type='str', required=True),
        vm_count=dict(type=int, required=True),
        cluster_name=dict(type='str', required=True),
        cluster_id=dict(type='str', required=True),
        state=dict(choices=GET_IP_VM_STATES, required=False, default='present'),
    )

class Get_vm_ip(VcdAnsibleModule):
    def __init__(self, **kwargs):
        super(Get_vm_ip, self).__init__(**kwargs)
        self.vapp_uuid = get_vapp_uuid(self.client, self.params['vapp_name'], self.params['vdc'])
    
    def manage_states(self):    
        state = self.params.get('state')
        if state == 'present':
            return self.get_ip_vm()

    def get_ip_vm(self):
        params = self.params
        vm_type = params.get('vm_type')
        vm_count = params.get('vm_count')
        cluster_name = params.get('cluster_name')
        cluster_id = params.get('cluster_id')
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
        response["ip"] = list()
        for vm in vms_list:
            vm_ip = get_vm_ip(self.client, self.vapp_uuid, vm)
            response['ip'].append(vm_ip)
        return response


def main():
    argument_spec = get_ip_vm_argument_spec()
    response = dict(
        msg=dict(type='str'),
        ip=list(),
        )
    module = Get_vm_ip(argument_spec=argument_spec, supports_check_mode=True)

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
