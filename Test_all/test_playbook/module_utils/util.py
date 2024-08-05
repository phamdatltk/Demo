def list_vm(cluster_name, cluster_id, is_cluster):
    master_vm = cluster_name + "-" + cluster_id + "-master1"
    list_vm = [master_vm]
    if is_cluster == "yes":
        slave01_vm = cluster_name + "-" + cluster_id + "-slave1"
        slave02_vm = cluster_name + "-" + cluster_id + "-slave2"
        list_vm.append(slave01_vm)
        list_vm.append(slave02_vm)
    return list_vm

def list_vm_opensearch(cluster_name, cluster_id, data_node):
    data_node = data_node + 1
    list_vm = []
    for i in range(1, data_node):
        node = cluster_name + "-" + cluster_id + "-node" + str(i)
        list_vm.append(node)
    return list_vm


## Add VM for clickhouse
def list_vm_clickhouse(cluster_name, cluster_id, is_cluster, number_of_shard):

    list_vm = []

    if is_cluster == "no":
        for i in range(1, number_of_shard + 1):
            master_node = cluster_name + "-" + cluster_id + "-master" + str(i)
            list_vm.append(master_node)
    
    if is_cluster == "yes":
        # Add all master node to list
        for i in range(1, number_of_shard + 1):
            master_node = cluster_name + "-" + cluster_id + "-master" + str(i)
            list_vm.append(master_node)
        # Add master 2 and 3 to list if 1 shard cluster
        if number_of_shard == 1:  
            slave01_vm = cluster_name + "-" + cluster_id + "-master2"
            slave02_vm = cluster_name + "-" + cluster_id + "-master3"
            list_vm.append(slave01_vm)
            list_vm.append(slave02_vm)
        # Add all slave node to list 
        if number_of_shard > 1:
            for i in range(1, number_of_shard + 1):
                slave_node = cluster_name + "-" + cluster_id + "-slave" + str(i)
                list_vm.append(slave_node)            
    return list_vm
