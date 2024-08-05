# !/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'phongvd8@fpt.com.vn'
}

DOCUMENTATION = '''
---
module: getway_snat_rule_service
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
    vdc:
        description:
            - Org Vdc where this VAPP gets created
        required: true
    edge_gw_id:
        description:
            - id of edge gateway
        required: True
    name_snat_rule:
        description:
            - name of Edge Gateway SNAT rule
        required: true
    internal_network_name:
        description:
            - name of internal network
        required: false
    translated_address:
        description:
            - IP public address
        required: false
    state:
        description:
            - state of Edge Gateway SNAT rule (present/absent).
            - One from state or operation has to be provided.
        required: false

author:
    - phongvd8@fpt.com.vn
'''

EXAMPLES = '''
- name: create SNAT rule
  gateway_snat_rule_service:
    edge_gw_id: "EG"
    name_snat_rule: "phongvd8"
    internal_network_name: "han-xplat-10-subnet1"
    translated_address: "103.160.78.87""
    destination_address: "8.8.8.8"
    state: 'present'
'''

RETURN = '''
msg: success/failure message corresponding to Edge Gateway SNAT rule state/operation
changed: true if resource has been changed else false
'''

from ansible.module_utils.vcd import VcdAnsibleModule

from ansible.module_utils.get_edge_gw_id import get_edge_gw_urn
from ansible.module_utils.get_vdc_id import get_vdc_id, get_vdc_urn
from ansible.module_utils.create_snat import create_snat_rule
from ansible.module_utils.delete_nat import delete_nat_rule
from ansible.module_utils.get_nat_id import get_edge_gateway_nat_rule
from ansible.module_utils.get_orgVdcNetwork import get_orgVdcNetwork
import time

EG_NAT_RULE_STATES = ['present', 'absent']

def eg_dnat_rule_argument_spec():
    return dict(
        edge_gw_id=dict(type='str', required=True),
        name_snat_rule=dict(type='str', required=True),
        internal_network_name=dict(type='str', required=False),
        translated_address=dict(type='str', required=False),
        destination_address=dict(type='str', required=False),
        priority=dict(type='str', required=False),
        state=dict(choices=EG_NAT_RULE_STATES, required=False),
    )

class SNAT_Rule(VcdAnsibleModule):
    def __init__(self, **kwargs):
        super(SNAT_Rule, self).__init__(**kwargs)
        self.vdc_id = get_vdc_id(self.client, self.params['vdc'])
        self.vdc_urn = get_vdc_urn(self.client, self.params['vdc'])
        # self.edge_gw_urn = get_edge_gw_urn(self.client, self.vdc_id, self.params['vcd_url'], self.vdc_id, self.params['edge_gw_name'])
        self.rule_id = ''


    def manage_states(self):    
        state = self.params.get('state')
        if state == 'absent':
                return self.delete()

        if state == 'present':
            return self.create()

    def create(self):
        params = self.params
        name_snat_rule=params.get('name_snat_rule')
        edge_gw_id = params.get('edge_gw_id')
        internal_network_name=params.get('internal_network_name')
        translated_address=params.get('translated_address')
        destination_address=params.get('destination_address')
        priority=params.get('priority')
        response = dict()
        response['changed'] = False

        # if get_edge_gateway_nat_rule(self.client, self.edge_gw_urn, self.params['name_snat_rule']) != "":
        #     msg = "Edge Gateway SNAT Rule {} is already present"
        #     response['warnings'] = msg.format(name_snat_rule)
        # else:
        #     create_snat_rule(self.client, name_snat_rule, self.edge_gw_urn, {"ip_address": translated_address,  "ip_address_internal": original_address})
        #     msg = 'Edge Gateway SNAT Rule {} has been created'
        #     response['msg'] = msg.format(name_snat_rule)
        #     response['changed'] = True
        time.sleep(5)
        if get_edge_gateway_nat_rule(self.client, edge_gw_id, name_snat_rule) != "":
            delete_nat_rule(self.client, edge_gw_id, get_edge_gateway_nat_rule(self.client, edge_gw_id, name_snat_rule))
            time.sleep(5)
        orgVdcNetwork = get_orgVdcNetwork(self.client, internal_network_name)
        create_snat_rule(self.client, name_snat_rule, edge_gw_id, {"ip_address": translated_address,  "ip_address_internal": orgVdcNetwork['subnet_cidr'],"ip_address_destination": destination_address,"snat_priority": priority})
        msg = 'Edge Gateway SNAT Rule {} has been created'
        response['msg'] = msg.format(name_snat_rule)
        response['changed'] = True

        return response


    def delete(self):
        params = self.params
        name_snat_rule=params.get('name_snat_rule')
        edge_gw_id = params.get('edge_gw_id')
        response = dict()
        response['changed'] = False
        time.sleep(5)
        if get_edge_gateway_nat_rule(self.client, edge_gw_id, name_snat_rule) == "":
            response['warnings'] = "Edge Gateway SNAT Rule {} is not present.".format(name_snat_rule)
        else:
            #time.sleep(5)
            self.rule_id = get_edge_gateway_nat_rule(self.client, edge_gw_id, name_snat_rule)
            delete_nat_rule(self.client, edge_gw_id, self.rule_id)
            response['msg'] = 'Edge Gateway DNAT Rule {} has been deleted.'.format(name_snat_rule)
            response['changed'] = True
        return response

def main():
    argument_spec = eg_dnat_rule_argument_spec()
    response = dict(msg=dict(type='str'))
    module = SNAT_Rule(argument_spec=argument_spec, supports_check_mode=True)

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
