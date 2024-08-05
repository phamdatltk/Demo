# !/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'phongvd8@fpt.com.vn'
}

DOCUMENTATION = '''
---
module: check_enable_vdc_group
short_description: check if vdc group is enabled in vCloud Director
version_added: "1.0"
description:
    - Check if vdc group is enabled in vCloud Director

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
    state:
        description:
            - state of action check if vdc group is enabled
        required: false

author:
    - phongvd8@fpt.com.vn
'''

EXAMPLES = '''
- name: check enable vdc group
  check_enable_vdc_group:
    edge_gw_id: "urn:vcloud:gateway:8f251440-b3d5-4e73-a6b5-d14a23cf43fe"
  register: output

- name: print enable value of vdc group
  debug:
    msg: "{{ output.enable }}"
'''

RETURN = '''
changed: true if resource has been changed else false
enable: true if vdc group is enabled
Example for the value return:
{
    "changed": true,
    "enable": true,
    "failed": false
}
'''


from ansible.module_utils.vcd import VcdAnsibleModule

from ansible.module_utils.get_vdc_id import get_vdc_id
from ansible.module_utils.get_vdc_group_id import check_vdc_group_enable

CHECK_VDC_GROUP_ENABLE_STATES = ['present']

def check_vdc_group_argument_spec():
    return dict(
        state=dict(choices=CHECK_VDC_GROUP_ENABLE_STATES, required=False, default='present'),
        edge_gw_id=dict(type='str', required=True),
    )

class Check_vdc_group_enable(VcdAnsibleModule):
    def __init__(self, **kwargs):
        super(Check_vdc_group_enable, self).__init__(**kwargs)
        self.vdc_id = get_vdc_id(self.client, self.params['vdc'])

    def manage_states(self):    
        state = self.params.get('state')
        if state == 'present':
            return self.check_vdc_group_enable()


    def check_vdc_group_enable(self):
        params = self.params
        edge_gw_id = params.get('edge_gw_id')
        response = dict()
        response['changed'] = True
        response["enable"] = check_vdc_group_enable(self.client, self.vdc_id, edge_gw_id)
        return response

def main():
    argument_spec = check_vdc_group_argument_spec()
    response = dict(
        msg=dict(type='str'),
        enable=bool,
        )
    module = Check_vdc_group_enable(argument_spec=argument_spec, supports_check_mode=True)

    try:
        if module.check_mode:
            response = dict()
            response['changed'] = False
            response['msg'] = "skipped, running in check mode"
            response['skipped'] = True
        elif module.params.get('state'):
            response = module.check_vdc_group_enable()
        else:
            raise Exception('Please provide state for resource')
    except Exception as error:
        response['msg'] = error
        module.fail_json(**response)
    else:
        module.exit_json(**response)

if __name__ == '__main__':
    main()