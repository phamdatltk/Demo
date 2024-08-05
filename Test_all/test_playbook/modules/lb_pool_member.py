# !/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'phongvd8@fpt.com.vn'
}

DOCUMENTATION = '''
---
module: lb_pool_member
short_description: Update lb pool member in vCloud Director
version_added: "1.0"
description:
    - Update lb pool member in vCloud Director

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
    edge_gw_id:
        description:
            - id of edge gateway
        required: True
    vapp_name:
        description:
            - name of vapp which contains VMs
        required: true
    lb_pool_name:
        description:
            - name of LB pool
        required: true
    defaultport:
        description:
            - The destination server port used by the traffic sent to the member.
        required: true
    algorithm:
        description:
            - Load Balancer Algorithm
        required: false
    health_monitors:
        description:
            - health_monitors protocol such as TCP, UDP, HTTP, HTTPS, PING
            - example value: { "type": "TCP" }
        required: false
    persistence_profile:
        description:
            - specifies the Persistence profile for a Load Balancer Pool. Persistence profile will ensure that the same user sticks to the same server for a desired duration of time.
            - example value: { "type": "CLIENT_IP", "value": "" }, { "type": "HTTP Cookie", "value": "" }
        required: false
    member_count:
        description:
            - number of lb pool members
        required: true
    members:
        description:
            - list of members
            - example value: ["fke-master", "fke-worker1"]
        required: false
    state:
        description:
            - state of lb pool member update (present).
            - One from state or operation has to be provided.
        required: false

author:
    - phongvd8@fpt.com.vn
'''

EXAMPLES = '''
- name: update lb pool member
  lb_pool_member:
    edge_gw_id: "urn:vcloud:gateway:8f251440-b3d5-4e73-a6b5-d14a23cf43fe"
    vapp_name: "phongvd8"
    lb_pool_name: "gardener-pool80"
    defaultport: 80
    member_count: "2"
    members: ["fke-master", "fke-worker1"]
'''

RETURN = '''
msg: success/failure message corresponding to Edge Gateway DNAT rule state/operation
changed: true if resource has been changed else false
'''

from ansible.module_utils.vcd import VcdAnsibleModule

from ansible.module_utils.get_lb_pool_id import get_lb_pool_id
from ansible.module_utils.update_lb_pool import update_loadbalancer_pool
from ansible.module_utils.get_edge_gw_id import get_edge_gw_urn
from ansible.module_utils.get_vdc_id import get_vdc_id
import time

LB_POOL_MEMBER_STATES = ['present']

def lb_pool_member_argument_spec():
    return dict(
        edge_gw_id=dict(type='str', required=True),
        vapp_name=dict(type='str', required=True),
        lb_pool_name=dict(type='str', required=True),
        defaultport=dict(type='str', required=True),
        algorithm=dict(type='str', required=False, default="ROUND_ROBIN"),
        health_monitors=dict(type=dict, required=False, default={ "type": "TCP" }),
        persistence_profile=dict(type=dict, required=False, default={ "type": "CLIENT_IP", "value": "" }),
        member_count=dict(type='str', required=True),
        members=dict(type=list, required=True),
        state=dict(choices=LB_POOL_MEMBER_STATES, required=False, default='present'),
    )

class Lb_pool_member(VcdAnsibleModule):
    def __init__(self, **kwargs):
        super(Lb_pool_member, self).__init__(**kwargs)
        self.vdc_id = get_vdc_id(self.client, self.params['vdc'])
        # self.edge_gw_urn = get_edge_gw_urn(self.client, self.vdc_id, self.params['vcd_url'], self.params['edge_gw_name'])
        self.lb_pool_id = get_lb_pool_id(self.client, self.params['edge_gw_id'], self.params['lb_pool_name'])
    
    def manage_states(self):    
        state = self.params.get('state')
        if state == 'present':
            return self.update_lb_pool()

    def update_lb_pool(self):
        params = self.params
        edge_gw_id = params.get('edge_gw_id')
        lb_pool_name=params.get('lb_pool_name')
        vapp_name=params.get('vapp_name')
        defaultport=params.get('defaultport')
        algorithm=params.get('algorithm')
        health_monitors=params.get('health_monitors')
        persistence_profile=params.get('persistence_profile')
        member_count=params.get('member_count')
        members=params.get('members')
        vdc_name = self.params['vdc']
        response = dict()
        response['changed'] = True
        time.sleep(10)
        update_loadbalancer_pool(self.client, vapp_name, lb_pool_name, defaultport, algorithm, health_monitors, persistence_profile, member_count, members, edge_gw_id, self.lb_pool_id, vdc_name)

        return response

def main():
    argument_spec = lb_pool_member_argument_spec()
    response = dict(msg=dict(type='str'))
    module = Lb_pool_member(argument_spec=argument_spec, supports_check_mode=True)

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
