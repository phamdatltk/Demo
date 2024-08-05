# !/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'phongvd8@fpt.com.vn'
}

DOCUMENTATION = '''
---
module: s3_object
short_description: Manage object's operations in S3
version_added: "1.0"
description:
    - Manage object's operations in S3

options:
    s3_key:
        description:
            - aws access key id
        required: True
    s3_secret:
        description:
            - aws secret access key
        required: True
    s3_url:
        description:
            - endpoint url of S3
        required: True
    local_file:
        description:
            - file which will be uploaded
        required: false
    folder_achive:
        description:
            - folder what achive file
        required: false
    s3_file_upload:
        description:
            - path of s3 file in upload_folder
        required: false
    s3_source_file:
        description:
            - path of s3 file what will be archived
        required: false
    s3_dest_file:
        description:
            - path of s3 file in achive_folder
        required: false
    bucket_delete:
        description:
            - bucket will be marked delete
        required: false
    folder_delete:
        description:
            - folder will be marked delete
        required: false
    bucket_upload:
        description:
            - bucket where local file will be uploaded
        required: false
    bucket_achive:
        description:
            - bucket where s3 file will be archived
        required: false
    source_bucket:
        description:
            - bucket has file what will be archived
        required: false
    dest_bucket:
        description:
            - bucket archive s3 file
        required: false
    operation:
        description:
            - operation of s3 object
        required: true


author:
    - phongvd8@fpt.com.vn
'''

EXAMPLES = '''
- name: upload s3 object
  s3_object:
    s3_key: "s3_key"
    s3_secret: "s3_secret"
    s3_url: "s3_url"
    local_file: "/home/a-xplat/log/fke-cluster_id-create-k8s.log"
    bucket_upload: "fke_bucket"
    s3_file_upload: "cluster_id/logs/cluster_id-create.log"
    operation: "upload"

- name: archieve file
  s3_object:
    s3_key: "s3_key"
    s3_secret: "s3_secret"
    s3_url: "s3_url"
    bucket_achive: "fke_archived_bucket"
    s3_source_file: "/fke_bucket/cluster_id/cluster_id-kubeconfig"
    s3_dest_file: "cluster_id/cluster_id-kubeconfig"
    operation: "archive_file"

- name: archive folder
  s3_object:
    s3_key: "s3_key"
    s3_secret: "s3_secret"
    s3_url: "s3_url"
    source_bucket: "fke_bucket"
    dest_bucket: "fke_archived_bucket"
    folder_achive: "cluster_id/logs/"
    operation: "archive_folder"

- name: delete object
  s3_object:
    s3_key: "s3_key"
    s3_secret: "s3_secret"
    s3_url: "s3_url"
    bucket_delete: "fke_bucket"
    folder_delete: "cluster_id/"
    operation: "delete"

'''

RETURN = '''
msg: success/failure message corresponding to s3 object operation
changed: true if resource has been changed else false
'''

from ansible.module_utils.s3 import upload_to_s3
from ansible.module_utils.s3 import delete_object
from ansible.module_utils.s3 import archive_file_object
from ansible.module_utils.s3 import archive_folder_object
from ansible.module_utils.basic import AnsibleModule
import boto3
import botocore

S3_OPERATION = ['upload', 'archive_file', 'archive_folder', 'delete']

def s3_operation_argument_spec():
    return dict(
        s3_key=dict(type='str', required=True),
        s3_secret=dict(type='str', required=True),
        s3_url=dict(type='str', required=True),
        local_file=dict(type='str', required=False),
        folder_achive=dict(type='str', required=False),
        s3_file_upload=dict(type='str', required=False),
        s3_source_file=dict(type='str', required=False),
        s3_dest_file=dict(type='str', required=False),
        bucket_delete=dict(type='str', required=False),
        folder_delete=dict(type='str', required=False),
        bucket_upload=dict(type='str', required=False),
        bucket_achive=dict(type='str', required=False),
        source_bucket=dict(type='str', required=False),
        dest_bucket=dict(type='str', required=False),
        operation=dict(choices=S3_OPERATION, required=True),
    )

class S3AnsibleModule(AnsibleModule):
    def __init__(self, **kwargs):
        argument_spec = s3_operation_argument_spec()
        argument_spec.update(kwargs.get('argument_spec', dict()))
        kwargs['argument_spec'] = argument_spec

        super(S3AnsibleModule, self).__init__(**kwargs)
        self.login()

    def login(self):
        try:
            s3_key = self.params.get('s3_key')
            s3_secret = self.params.get('s3_secret')
            s3_url = self.params.get('s3_url')
            self.client = boto3.client("s3", aws_access_key_id=s3_key, aws_secret_access_key=s3_secret, endpoint_url=s3_url)
        except NoCredentialsError:
            self.fail_json("Credentials not available")
            

    def manage_operation(self):    
        operation = self.params.get('operation')
        if operation == "upload":
                return self.upload()

        if operation == 'archive_file':
            return self.archive_file()
        
        if operation == 'archive_folder':
            return self.archive_folder()
        
        else:
            return self.delete()
    
    def upload(self):
        params = self.params
        local_file = params.get('local_file')
        bucket_upload = params.get('bucket_upload')
        s3_file_upload = params.get('s3_file_upload')

        response = dict()

        upload_to_s3(self.client, local_file, bucket_upload, s3_file_upload)
    
        response['changed'] = True

        return response 

    def archive_file(self):
        params = self.params
        bucket_achive = params.get('bucket_achive')
        s3_source_file = params.get('s3_source_file')
        s3_dest_file = params.get('s3_dest_file')
        response = dict()
        archive_file_object(self.client, bucket_achive, s3_source_file, s3_dest_file)

        response['changed'] = True

        return response  

    def archive_folder(self):
        params = self.params
        source_bucket = params.get('source_bucket')
        dest_bucket = params.get('dest_bucket')
        folder_achive = params.get('folder_achive')
        response = dict()
        archive_folder_object(self.client, source_bucket, dest_bucket, folder_achive)

        response['changed'] = True

        return response 

    def delete(self):
        params = self.params
        bucket_delete = params.get('bucket_delete')
        folder_delete = params.get('folder_delete')
        delete_object(self.client, bucket_delete, folder_delete)

        response = dict()
        response['changed'] = True

        return response 

def main():
    argument_spec = s3_operation_argument_spec()
    response = dict(msg=dict(type='str'))
    module = S3AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)

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
