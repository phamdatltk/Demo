# !/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'phongvd8@fpt.com.vn'
}

DOCUMENTATION = '''
---
module: make_body_callback
short_description: Make bode POST request to callback
version_added: "1.0"
description:
    - Make bode POST request to callback

options:
    cluster_id:
        description:
            - id of K8S cluster
        required: true
    status:
        description:
            - status of action with cluster
        required: true
    type:
        description:
            - action type with cluster
        required: true
    # message:
    #     description:
    #         - message of callback request
    #     required: true
    # request_user_id:
    #     description:
    #         - ID of request user
    #     required: true
    client_id:
        description:
            - id of client
        required: true
    client_secret:
        description:
            - secret of client
        required: true
    state:
        description:
            - state of operation
        required: false

author:
    - phongvd8@fpt.com.vn
'''

EXAMPLES = '''
- name: make body POST request
  make_body_callback:
    cluster_id: "123456"
    status: "SUCCEEDED"
    type: "create"
    client_id: "4564321"
    client_secret: "21654987"
  register: output
- name: print client_id
  debug:
    msg: "{{output.body.client_id}}"
'''

RETURN = '''
msg: success/failure message corresponding to Anti Affinity rule state/operation
changed: true if resource has been changed else false
'''

from ansible.module_utils.basic import AnsibleModule

STATUS_STATES = ["SUCCEEDED", "CREATE ERROR", "ERROR"]
TYPE_STATES = ["create", "delete", "scale", "upgrade", "nfs"]
STATES = ["present"]

def make_body_request_argument_spec():
    return dict(
        cluster_id=dict(type='str', required=True),
        status=dict(choices=STATUS_STATES, required=True),
        type=dict(choices=TYPE_STATES, required=True),
        # message=dict(type='str', required=True),
        # request_user_id=dict(type='str', required=True),
        client_id=dict(type='str', required=True),
        client_secret=dict(type='str', required=True),
        state=dict(choices=STATES, required=False, default='present'),
    )

class Body_request(AnsibleModule):
    def __init__(self, **kwargs):
        argument_spec = make_body_request_argument_spec()
        argument_spec.update(kwargs.get('argument_spec', dict()))
        kwargs['argument_spec'] = argument_spec
        super(Body_request, self).__init__(**kwargs)

    def manage_states(self):
        state = self.params.get('state')
        if state == 'present':
            return self.make_body_request()


    def make_body_request(self):
        params = self.params
        cluster_id=params.get('cluster_id')
        status=params.get('status')
        type=params.get('type')
        # message=params.get('message')
        # request_user_id=params.get('request_user_id')
        client_id=params.get('client_id')
        client_secret=params.get('client_secret')
        response = dict()
        response['changed'] = True
        response['body'] = dict()
        response['body']['cluster_id'] = cluster_id
        response['body']['status'] = status
        response['body']['type'] = type
        # more_info = dict()
        # more_info['message']=message
        # more_info['request_user_id']=request_user_id
        # response['body']['more_info'] = more_info
        response['body']['client_id'] = client_id
        response['body']['client_secret'] = client_secret
        
        return response


def main():
    argument_spec = make_body_request_argument_spec()
    response = dict(
        msg=dict(type='str'),
        body=dict(cluster_id='str', status='str', type='str', 
            client_id='str', client_secret='str'
        ),
        )
    module = Body_request(argument_spec=argument_spec, supports_check_mode=True)

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