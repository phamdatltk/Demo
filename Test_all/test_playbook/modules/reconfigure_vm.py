# !/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '1.3',
    'status': ['preview'],

}

DOCUMENTATION = '''
---
module: reconfigure_vm
short_description: reconfigure VM info in vCloud Director
version_added: "1.3"
description:
    - Reconfigure VM info in vCloud Director

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
        required: false
    vm_add:
        description:
            - count of VM addition
        required: false
    num_cpus:
        description:
            - number of CPU cores
        required: false
    memory_resource:
        description:
            - resource of Memory by GB
        required: false
    disk_size:
        description:
            - size of VM's disk by GB
        required: false  
    operation:
        description:
            - operation of Reconfigure_VM.
            - One from operation has to be provided.
        required: false
    state:
        description:
            - state of Reconfigure_VM.
        required: false


'''

EXAMPLES = '''
- name: Reconfigure VM (cpu + memory + disk)
  reconfigure_vm:
    vapp_name: "phong"
    vm_type: "master"
    vm_count: 3
    vm_id: ["f2whd208", "p3a60p8k", "l62ga51y"]
    cluster_name: " "
    cluster_id: "abcxyz"
    num_cpus: 4
    memory_resource: 8
    disk_size: 50
    storage_profile_name: "{{ storage_profile }}"
    state: 'present'

- name: Reconfigure VM (cpu)
  reconfigure_vm:
    vapp_name: "phong"
    vm_type: "master"
    vm_count: 3
    vm_id: ["f2whd208", "p3a60p8k", "l62ga51y"]
    cluster_name: " "
    cluster_id: "abcxyz"
    num_cpus: 8
    storage_profile_name: "{{ storage_profile }}"
    state: 'present'

- name: Reconfigure VM (memory)
  reconfigure_vm:
    vcd_url: "https://hn01vcd.fptcloud.com"
    vapp_name: " "
    vm_type: "master"
    vm_count: 3
    vm_id: ["f2whd208", "p3a60p8k", "l62ga51y"]
    cluster_name: " "
    cluster_id: "abcxyz"
    memory_resource: 4
    storage_profile_name: "{{ storage_profile }}"
    state: 'present'

- name: Reconfigure VM (disk)
  reconfigure_vm:
    vcd_url: "https://hn01vcd.fptcloud.com"
    vapp_name: " "
    vm_type: "master"
    vm_count: 3
    vm_id: ["f2whd208", "p3a60p8k", "l62ga51y"]
    cluster_name: "phongvd8"
    cluster_id: "abcxyz"
    disk_size: 60
    storage_profile_name: "{{ storage_profile }}"
    state: 'present'

- name: Reconfigure VM (cpu + memory)
  reconfigure_vm:
    vapp_name: "phong"
    vm_type: "master"
    vm_count: 3
    vm_id: ["f2whd208", "p3a60p8k", "l62ga51y"]
    cluster_name: "phongvd8"
    cluster_id: "abcxyz"
    num_cpus: 4
    memory_resource: 8
    storage_profile_name: "{{ storage_profile }}"
    state: 'present'

- name: Reconfigure VM scale up
  reconfigure_vm:
    vcd_url: "https://hn01vcd.fptcloud.com"
    vapp_name: ""
    vm_type: "master"
    vm_count: "3"
    vm_id: ["f2whd208", "p3a60p8k", "l62ga51y"]
    vm_add: 3
    cluster_name: "phongvd8"
    cluster_id: "abcxyz"
    num_cpus: 4
    memory_resource: 8
    disk_size: 50
    storage_profile_name: "{{ storage_profile }}"
    operation: 'scale'
'''

RETURN = '''
msg: success/failure message corresponding to Reconfigure_VM state/operation
changed: true if resource has been changed else false
'''

from ansible.module_utils.vcd import VcdAnsibleModule

# from ansible.module_utils.reconfigure_vm import reconfigure_vm_cpu_memory_disk
from ansible.module_utils.reconfigure_vm import reconfigure_vm_cpu_memory
# from ansible.module_utils.reconfigure_vm import reconfigure_vm_cpu_disk
# from ansible.module_utils.reconfigure_vm import reconfigure_vm_memory_disk
from ansible.module_utils.reconfigure_vm import reconfigure_vm_cpu
from ansible.module_utils.reconfigure_vm import reconfigure_vm_memory

import time
from ansible.module_utils.util import list_vm


RECONFIGURE_VM_OPERATIONS = ['scale']
RECONFIGURE_VM_STATES = ['present', 'update_slave', 'update_master']


def reconfigure_vm_argument_spec():
    return dict(
        vdc_name=dict(type='str', required=True),
        vm_type=dict(type='str', required=False),
        cluster_name=dict(type='str', required=False),
        cluster_id=dict(type='str', required=False),
        is_cluster=dict(type='str', required=True),
        num_cpus=dict(type=int, required=False),
        memory_resource=dict(type=int, required=False),
        disk_size=dict(type=int, required=False),
        storage_profile_name=dict(type='str', required=False),
        hardware_version=dict(type='str', required=True),
        operation=dict(choices=RECONFIGURE_VM_OPERATIONS, required=False),
        state=dict(choices=RECONFIGURE_VM_STATES, required=False),
        placement_policy_name=dict(type='str', required=False)

    )


class Reconfigure_VM_Parrallel(VcdAnsibleModule):
    def __init__(self, **kwargs):
        super(Reconfigure_VM_Parrallel, self).__init__(**kwargs)

    def manage_states(self):
        state = self.params.get('state')

        if state == 'present':
            return self.reconfigure_vm_create()

        if state == 'update_slave':
            return self.reconfigure_slave()

        if state == 'update_master':
            return self.reconfigure_master()
    def reconfigure_slave(self):
        params = self.params
        cluster_name = params.get('cluster_name')
        cluster_id = params.get('cluster_id')
        is_cluster = params.get('is_cluster')
        num_cpus = params.get('num_cpus')
        memory_resource = params.get('memory_resource')
        disk_size = params.get('disk_size')
        storage_profile_name = params.get('storage_profile_name')
        vdc_name = params.get('vdc_name')
        hardware_version = params.get('hardware_version')
        vapp_name = cluster_name + "-" + cluster_id
        vms_list = list_vm(cluster_name, cluster_id, is_cluster)
        response = dict()
        response['changed'] = True
        placement_policy_name = params.get('placement_policy_name')
        print("print hardware_version:", hardware_version)
        for vm in vms_list:
            if "slave" in vm:
                if num_cpus != None and memory_resource != None and disk_size == None:
                    reconfigure_vm_cpu_memory(self.client, vdc_name, vapp_name, vm, num_cpus, memory_resource,
                                              storage_profile_name, hardware_version, placement_policy_name)
                elif num_cpus != None and memory_resource == None and disk_size == None:
                    reconfigure_vm_cpu(self.client, vdc_name, vapp_name, vm, num_cpus, storage_profile_name, hardware_version, placement_policy_name)
                elif num_cpus == None and memory_resource != None and disk_size == None:
                    reconfigure_vm_memory(self.client, vdc_name, vapp_name, vm, memory_resource, storage_profile_name, hardware_version, placement_policy_name)
        time.sleep(15)
        return response


    def reconfigure_master(self):
        params = self.params
        cluster_name = params.get('cluster_name')
        cluster_id = params.get('cluster_id')
        is_cluster = params.get('is_cluster')
        num_cpus = params.get('num_cpus')
        memory_resource = params.get('memory_resource')
        disk_size = params.get('disk_size')
        storage_profile_name = params.get('storage_profile_name')
        vdc_name = params.get('vdc_name')
        hardware_version = params.get('hardware_version')
        vapp_name = cluster_name + "-" + cluster_id
        vms_list = list_vm(cluster_name, cluster_id, is_cluster)
        response = dict()
        response['changed'] = True
        placement_policy_name = params.get('placement_policy_name')
        print("print hardware_version:", hardware_version)
        for vm in vms_list:
            if "master" in vm:
                if num_cpus != None and memory_resource != None and disk_size == None:
                    reconfigure_vm_cpu_memory(self.client, vdc_name, vapp_name, vm, num_cpus, memory_resource,
                                              storage_profile_name, hardware_version, placement_policy_name)
                elif num_cpus != None and memory_resource == None and disk_size == None:
                    reconfigure_vm_cpu(self.client, vdc_name, vapp_name, vm, num_cpus, storage_profile_name, hardware_version, placement_policy_name)
                elif num_cpus == None and memory_resource != None and disk_size == None:
                    reconfigure_vm_memory(self.client, vdc_name, vapp_name, vm, memory_resource, storage_profile_name, hardware_version, placement_policy_name)
        time.sleep(15)
        return response

    def reconfigure_vm_create(self):
        params = self.params
        cluster_name = params.get('cluster_name')
        cluster_id = params.get('cluster_id')
        is_cluster = params.get('is_cluster')
        num_cpus = params.get('num_cpus')
        memory_resource = params.get('memory_resource')
        disk_size = params.get('disk_size')
        storage_profile_name = params.get('storage_profile_name')
        vdc_name = params.get('vdc_name')
        hardware_version = params.get('hardware_version')
        vapp_name = cluster_name + "-" + cluster_id
        vms_list = list_vm(cluster_name, cluster_id, is_cluster)
        response = dict()
        response['changed'] = True
        placement_policy_name = params.get('placement_policy_name')
        print("print hardware_version:", hardware_version)
        for vm in vms_list:
            # if num_cpus != None and memory_resource != None and disk_size != None and disk_size >= 40:
            #     reconfigure_vm_cpu_memory_disk(self.client, vdc_name, vapp_name, vm, num_cpus,
            #                                    memory_resource, disk_size, storage_profile_name)
            if num_cpus != None and memory_resource != None and disk_size == None:
                reconfigure_vm_cpu_memory(self.client, vdc_name, vapp_name, vm, num_cpus, memory_resource,
                                          storage_profile_name, hardware_version, placement_policy_name)
            # elif num_cpus != None and memory_resource == None and disk_size != None and disk_size > 40:
            #     reconfigure_vm_cpu_disk(self.client, vdc_name, vapp_name, vm, num_cpus, disk_size, storage_profile_name)
            elif num_cpus != None and memory_resource == None and disk_size == None:
                reconfigure_vm_cpu(self.client, vdc_name, vapp_name, vm, num_cpus, storage_profile_name, hardware_version, placement_policy_name)
            # elif num_cpus == None and memory_resource != None and disk_size != None and disk_size > 40:
            #     reconfigure_vm_memory_disk(self.client, vdc_name, vapp_name, vm, memory_resource, disk_size,
            #                                storage_profile_name)
            elif num_cpus == None and memory_resource != None and disk_size == None:
                reconfigure_vm_memory(self.client, vdc_name, vapp_name, vm, memory_resource, storage_profile_name, hardware_version, placement_policy_name)
            # elif num_cpus == None and memory_resource == None and disk_size != None and disk_size > 40:
            #     reconfigure_vm_disk(self.client, vdc_name, vapp_name, vm, disk_size, storage_profile_name)
        time.sleep(15)

        return response

def main():
    argument_spec = reconfigure_vm_argument_spec()
    response = dict(
        msg=dict(type='str'))
    module = Reconfigure_VM_Parrallel(argument_spec=argument_spec, supports_check_mode=True)

    try:
        if module.check_mode:
            response = dict()
            response['changed'] = False
            response['msg'] = "skipped, running in check mode"
            response['skipped'] = True
        elif module.params.get('state'):
            response = module.manage_states()
        elif module.params.get('operation'):
            response = module.manage_operations()
        else:
            raise Exception('Please provide state for resource')
    except Exception as error:
        response['msg'] = error
        module.fail_json(**response)
    else:
        module.exit_json(**response)


if __name__ == '__main__':
    main()
