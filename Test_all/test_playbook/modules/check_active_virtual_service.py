# !/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'phongvd8@fpt.com.vn'
}

DOCUMENTATION = '''
---
module: check_active_virtual_service
short_description: check if virtual service is active in vCloud Director
version_added: "1.0"
description:
    - Check if virtual service is active in vCloud Director

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
    state:
        description:
            - state of action check if virtual service is active
        required: false
    edge_gw_id:
        description:
            - id of edge gateway
        required: True
    virtual_service_name:
        description:
            - name of LB virtual service
        required: true

author:
    - phongvd8@fpt.com.vn
'''

EXAMPLES = '''
- name: check if virtual service is active
  check_active_virtual_service:
    edge_gw_id: "urn:vcloud:gateway:8f251440-b3d5-4e73-a6b5-d14a23cf43fe"
    virtual_service_name: "gardener443"
  register: output

- name: print active value of virtual service
  debug:
    msg: "{{ output.active }}"
'''

RETURN = '''
changed: true if resource has been changed else false
active: true if virtual service is active
Example for the value return:
{
    "active": false,
    "changed": true,
    "failed": false
}
'''


from ansible.module_utils.vcd import VcdAnsibleModule

from ansible.module_utils.get_edge_gw_id import get_edge_gw_urn
from ansible.module_utils.get_vdc_id import get_vdc_id
from ansible.module_utils.get_lb_virtual_service_id import check_active_lb_virtualservice

CHECK_ACTIVE_VIRTUAL_SERVICE_STATES = ['present']

def check_vdc_group_argument_spec():
    return dict(
        edge_gw_id=dict(type='str', required=True),
        virtual_service_name=dict(type='str', required=True),
        state=dict(choices=CHECK_ACTIVE_VIRTUAL_SERVICE_STATES, required=False, default='present'),
    )

class Check_active_virtual_service(VcdAnsibleModule):
    def __init__(self, **kwargs):
        super(Check_active_virtual_service, self).__init__(**kwargs)
        self.vdc_id = get_vdc_id(self.client, self.params['vdc'])
        # self.edge_gw_urn = get_edge_gw_urn(self.client, self.vdc_id, self.params['vcd_url'], self.params['edge_gw_name'])

    def manage_states(self):    
        state = self.params.get('state')
        if state == 'present':
            return self.check_active_virtual_service()


    def check_active_virtual_service(self):
        params = self.params
        virtual_service_name=params.get('virtual_service_name')
        edge_gw_id = params.get('edge_gw_id')
        response = dict()
        response['changed'] = True
        response["active"] = check_active_lb_virtualservice(self.client, edge_gw_id, virtual_service_name)
        return response

def main():
    argument_spec = check_vdc_group_argument_spec()
    response = dict(
        msg=dict(type='str'),
        active=bool,
        )
    module = Check_active_virtual_service(argument_spec=argument_spec, supports_check_mode=True)

    try:
        if module.check_mode:
            response = dict()
            response['changed'] = False
            response['msg'] = "skipped, running in check mode"
            response['skipped'] = True
        elif module.params.get('state'):
            response = module.check_active_virtual_service()
        else:
            raise Exception('Please provide state for resource')
    except Exception as error:
        response['msg'] = error
        module.fail_json(**response)
    else:
        module.exit_json(**response)

if __name__ == '__main__':
    main()