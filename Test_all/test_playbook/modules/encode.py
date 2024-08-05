from ansible.module_utils.encode import encode
from ansible.module_utils.basic import AnsibleModule

ENCODE_OPERATION = ['encode']

def encode_operation_argument_spec():
    return dict(
        data=dict(type='str', required=True),
        operation=dict(choices=ENCODE_OPERATION, required=False, default="encode"),
    )

class EncodeAnsibleModule(AnsibleModule):
    def __init__(self, **kwargs):
        argument_spec = encode_operation_argument_spec()
        argument_spec.update(kwargs.get('argument_spec', dict()))
        kwargs['argument_spec'] = argument_spec

        super(EncodeAnsibleModule, self).__init__(**kwargs)

    def manage_operation(self):    
        operation = self.params.get('operation')
        if operation == "encode":
            return self.encode()

    def encode(self):
        params = self.params
        data = params.get('data')

        response = dict()

        response['changed'] = True
        response['data_encode'] = encode(data)

        return response 

def main():
    argument_spec = encode_operation_argument_spec()
    response = dict(msg=dict(type='str'), data_encode=str)
    module = EncodeAnsibleModule(argument_spec=argument_spec, supports_check_mode=True)

    try:
        if module.check_mode:
            response = dict()
            response['changed'] = False
            response['msg'] = "skipped, running in check mode"
            response['skipped'] = True
        elif module.params.get('operation'):
            response = module.manage_operation()
        else:
            raise Exception('Please provide state for resource')
    except Exception as error:
        response['msg'] = error
        module.fail_json(**response)
    else:
        module.exit_json(**response)
    
if __name__ == '__main__':
    main()
