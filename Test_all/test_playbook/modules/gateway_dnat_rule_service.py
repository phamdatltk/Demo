# !/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'phongvd8@fpt.com.vn'
}

DOCUMENTATION = '''
---
module: getway_dnat_rule_service
short_description: Manage NAT_rule's states/operations in vCloud Director
version_added: "1.0"
description:
    - Manage NAT_rule's states/operations in vCloud Director

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
    isEnableVDCGroup:
        description:
            - check if vDC Group is enabled
            - default value is True
            - type: bool
            - isEnableVDCGroup can be got from module 'check_enable_vdc_group'
        required: false
    vdc:
        description:
            - Org Vdc where this VAPP gets created
        required: true
    edge_gw_id:
        description:
            - id of edge gateway
        required: True
    name_dnat_rule:
        description:
            - name of Edge Gateway DNAT rule
        required: true
    app_port_profile_name:
        description:
            - name of Application Port Profile
        required: true
    original_address:
        description:
            - internal IP address
        required: false
    translated_address:
        description:
            - IP public address
        required: false
    original_port:
        description:
            - port of application which VM in vCD use.
        required: false
    translated_port:
        description:
            - port which to be used to access to application from outbound
        required: false
    protocol:
        description:
            - protocol of application use to connect such as TCP, UDP
        required: false
    scope:
        description:
            - scope of applicaion port profile
            - value is 'SYSTEM'/'TENANT'
        required: True
    state:
        description:
            - state of Edge Gateway DNAT rule (present/absent).
            - One from state or operation has to be provided.
        required: false

author:
    - phongvd8@fpt.com.vn
'''

EXAMPLES = '''
- name: create DNAT rule
  gateway_dnat_rule_service:
    isEnableVDCGroup: false
    edge_gw_id: "urn:vcloud:gateway:8f251440-b3d5-4e73-a6b5-d14a23cf43fe"
    app_port_profile_name: "SSH"
    name_dnat_rule: "phongvd8"
    original_address: "172.16.200.2"
    translated_address: "103.160.78.87"
    original_port: "22"
    translated_port: "2022"
    protocol: "TCP"
    scope: 'SYSTEM'
    state: 'present'

- name: create Dnat rule
  gateway_dnat_rule_service:
    isEnableVDCGroup: false
    edge_gw_id: "urn:vcloud:gateway:8f251440-b3d5-4e73-a6b5-d14a23cf43fe"
    name_dnat_rule: "phongvd8-test"
    app_port_profile_name: "fke-api-6443"
    original_address: "10.0.1.22"
    translated_address: "103.160.78.88"
    original_port: "6443"
    translated_port: "6443"
    protocol: "TCP"
    scope: 'TENANT'
    state: 'present'
'''

RETURN = '''
msg: success/failure message corresponding to Edge Gateway DNAT rule state/operation
changed: true if resource has been changed else false
'''

from ansible.module_utils.vcd import VcdAnsibleModule

from ansible.module_utils.get_vdc_group_id import get_vdc_group_urn
from ansible.module_utils.get_app_port_profile_id import get_app_port_profile_urn
from ansible.module_utils.get_edge_gw_id import get_edge_gw_urn
from ansible.module_utils.get_vdc_id import get_vdc_id, get_vdc_urn
from ansible.module_utils.create_dnat import create_dnat_rule
from ansible.module_utils.delete_nat import delete_nat_rule
from ansible.module_utils.get_nat_id import get_edge_gateway_nat_rule
import time

EG_NAT_RULE_STATES = ['present', 'absent']
EG_NAT_RULE_SCOPE = ['SYSTEM', 'TENANT']

def eg_dnat_rule_argument_spec():
    return dict(
        isEnableVDCGroup=dict(type=bool, required=False, default=True),
        edge_gw_id=dict(type='str', required=True),
        name_dnat_rule=dict(type='str', required=True),
        app_port_profile_name=dict(type='str', required=False),
        original_address=dict(type='str', required=False),
        translated_address=dict(type='str', required=False),
        original_port=dict(type='str', required=False),
        translated_port=dict(type='str', required=False),
        protocol=dict(type='str', required=False),
        scope=dict(choices=EG_NAT_RULE_SCOPE, required=False),
        state=dict(choices=EG_NAT_RULE_STATES, required=False),
    )

class DNAT_Rule(VcdAnsibleModule):
    def __init__(self, **kwargs):
        super(DNAT_Rule, self).__init__(**kwargs)
        self.vdc_id = get_vdc_id(self.client, self.params['vdc'])
        self.vdc_urn = get_vdc_urn(self.client, self.params['vdc'])
        # self.edge_gw_urn = get_edge_gw_urn(self.client, self.vdc_id, self.params['vcd_url'], self.params['edge_gw_name'])
        self.vdc_group_urn = ''
        self.app_port_profile_urn = ''
        self.rule_id = ''
        
    def manage_states(self):    
        state = self.params.get('state')
        isEnableVDCGroup = self.params.get('isEnableVDCGroup')
        if state == 'absent':
            return self.delete()

        if isEnableVDCGroup:
            if state == 'present':
                return self.create_dnat_vdcgroup()
        else:
            if state == 'present':
                return self.create_dnat_no_vdcgroup()


    def create_dnat_vdcgroup(self):
        params = self.params
        # vcd_url=params.get('vcd_url')
        name_dnat_rule=params.get('name_dnat_rule')
        edge_gw_id = params.get('edge_gw_id')
        app_port_profile_name=params.get('app_port_profile_name')
        original_address=params.get('original_address')
        translated_address=params.get('translated_address')
        original_port=params.get('original_port')
        translated_port=params.get('translated_port')
        protocol=params.get('protocol')
        scope=params.get('scope')
        response = dict()
        response['changed'] = False

        # if get_edge_gateway_nat_rule(self.client, self.edge_gw_urn, self.params['name_dnat_rule']) != "":
        #     msg = "Edge Gateway DNAT Rule {} is already present"
        #     response['warnings'] = msg.format(name_dnat_rule)
        # else:
        #     self.vdc_group_urn = get_vdc_group_urn(self.client, self.vdc_id, self.params['vcd_url'])
        #     self.app_port_profile_urn = get_app_port_profile_urn(self.client, original_port, protocol, self.vdc_group_urn, scope)
        #     create_dnat_rule(self.client, name_dnat_rule, self.edge_gw_urn, {"ip_address": translated_address, "ip_address_internal": original_address, "translated_port": translated_port}, self.app_port_profile_urn)
        #     msg = 'Edge Gateway DNAT Rule {} has been created'
        #     response['msg'] = msg.format(name_dnat_rule)
        #     response['changed'] = True
        time.sleep(10)
        if get_edge_gateway_nat_rule(self.client, edge_gw_id, name_dnat_rule) != "":
            delete_nat_rule(self.client, edge_gw_id, get_edge_gateway_nat_rule(self.client, edge_gw_id, name_dnat_rule))
            time.sleep(10)
        self.vdc_group_urn = get_vdc_group_urn(self.client, self.vdc_id, edge_gw_id)
        self.app_port_profile_urn = get_app_port_profile_urn(self.client, app_port_profile_name, original_port, protocol, self.vdc_group_urn, scope)
        create_dnat_rule(self.client, name_dnat_rule, app_port_profile_name, edge_gw_id, {"ip_address": translated_address, "ip_address_internal": original_address, "translated_port": translated_port}, self.app_port_profile_urn)
        msg = 'Edge Gateway DNAT Rule {} has been created'
        response['msg'] = msg.format(name_dnat_rule)
        response['changed'] = True

        return response

    def create_dnat_no_vdcgroup(self):
        params = self.params
        # vcd_url=params.get('vcd_url')
        name_dnat_rule=params.get('name_dnat_rule')
        edge_gw_id = params.get('edge_gw_id')
        app_port_profile_name=params.get('app_port_profile_name')
        original_address=params.get('original_address')
        translated_address=params.get('translated_address')
        original_port=params.get('original_port')
        translated_port=params.get('translated_port')
        protocol=params.get('protocol')
        scope=params.get('scope')
        response = dict()
        response['changed'] = False

        # if get_edge_gateway_nat_rule(self.client, self.edge_gw_urn, self.params['name_dnat_rule']) != "":
        #     msg = "Edge Gateway DNAT Rule {} is already present"
        #     response['warnings'] = msg.format(name_dnat_rule)
        # else:
        #     self.app_port_profile_urn = get_app_port_profile_urn(self.client, original_port, protocol, self.vdc_urn, scope)
        #     create_dnat_rule(self.client, name_dnat_rule, self.edge_gw_urn, {"ip_address": translated_address, "ip_address_internal": original_address, "translated_port": translated_port}, self.app_port_profile_urn)
        #     msg = 'Edge Gateway DNAT Rule {} has been created'
        #     response['msg'] = msg.format(name_dnat_rule)
        #     response['changed'] = True
        time.sleep(10)
        if get_edge_gateway_nat_rule(self.client, edge_gw_id, name_dnat_rule) != "":
            delete_nat_rule(self.client, edge_gw_id, get_edge_gateway_nat_rule(self.client, edge_gw_id, name_dnat_rule))
            time.sleep(10)
        self.app_port_profile_urn = get_app_port_profile_urn(self.client, app_port_profile_name, original_port, protocol, self.vdc_urn, scope)
        create_dnat_rule(self.client, name_dnat_rule, app_port_profile_name, edge_gw_id, {"ip_address": translated_address, "ip_address_internal": original_address, "translated_port": translated_port}, self.app_port_profile_urn)
        msg = 'Edge Gateway DNAT Rule {} has been created'
        response['msg'] = msg.format(name_dnat_rule)
        response['changed'] = True

        return response

    def delete(self):
        params = self.params
        name_dnat_rule=params.get('name_dnat_rule')
        edge_gw_id = params.get('edge_gw_id')
        response = dict()
        response['changed'] = False
        time.sleep(10)
        if get_edge_gateway_nat_rule(self.client, edge_gw_id, name_dnat_rule) == "":
            response['warnings'] = "Edge Gateway DNAT Rule {} is not present.".format(name_dnat_rule)
        else:
            self.rule_id = get_edge_gateway_nat_rule(self.client, edge_gw_id, name_dnat_rule)
            delete_nat_rule(self.client, edge_gw_id, self.rule_id)
            response['msg'] = 'Edge Gateway DNAT Rule {} has been deleted.'.format(name_dnat_rule)
            response['changed'] = True
        return response

def main():
    argument_spec = eg_dnat_rule_argument_spec()
    response = dict(msg=dict(type='str'))
    module = DNAT_Rule(argument_spec=argument_spec, supports_check_mode=True)

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
