import requests
from ansible.module_utils.requestInfo import RequestInfo

import http.client
http.client._MAXHEADERS = 1000

def handle_get(url, headers):
    print(url)
    resp = requests.get(url, headers=headers, verify=False)
    if not resp.ok:
        raise Exception(resp.content)
    return resp

def get_compute_policy_href(client, vdc_id, cpuCount, memory):
    params = RequestInfo(client)
    uri_api = client.get_api_uri()
    uri = uri_api.replace('/api', '')
    resp = handle_get(
        f"{uri}/cloudapi/2.0.0/vdcs/urn:vcloud:vdc:{vdc_id}/computePolicies?page=1&pageSize=128&filterEncoded=true&filter=policyType==VdcVmPolicy&links=true", headers=params.headers_compute_policy
    )
    compute_policy_href = ''
    for i in resp.json()['values']:
        if i["memory"] == memory and i["cpuCount"] == cpuCount:
            compute_policy_href = i["id"]
            
    print(compute_policy_href)
    return compute_policy_href

def get_system_default_compute_policy_href(client, vdc_id):
    params = RequestInfo(client)
    uri_api = client.get_api_uri()
    uri = uri_api.replace('/api', '')
    resp = handle_get(
        f"{uri}/cloudapi/2.0.0/vdcs/urn:vcloud:vdc:{vdc_id}/computePolicies?page=1&pageSize=128&filterEncoded=true&filter=policyType==VdcVmPolicy&links=true", headers=params.headers_compute_policy
    )
    compute_policy_href = ''
    for i in resp.json()['values']:
        if i["name"] == "System Default":
            compute_policy_href = i["id"]
            break
            
    print(compute_policy_href)
    return compute_policy_href
    
def get_compute_policy_name(client, vdc_id):
    params = RequestInfo(client)
    uri = client.get_api_uri()
    resp = handle_get(
        f"{uri}/vdc/{vdc_id}/computePolicies", headers=params.headers_compute_policy
    )
    compute_policy_name = ''
    for i in resp.json()['vdcComputePolicyReference']:
        if i["name"] == "vGPU-VM Policy":
            compute_policy_name = i["name"]
    print(compute_policy_name)
    return compute_policy_name

def get_placement_policy(client, vdc_id, name):
    params = RequestInfo(client)
    uri_api = client.get_api_uri()
    uri = uri_api.replace('/api', '')
    resp = handle_get(
        f"{uri}/cloudapi/2.0.0/vdcs/urn:vcloud:vdc:{vdc_id}/computePolicies?page=1&pageSize=128&filterEncoded=true&filter=isSizingOnly==false;isVgpuPolicy==false;policyType==VdcVmPolicy&links=true",
        headers=params.headers_compute_policy
    )
    # print(resp.json()['values'])
    placement_policy_href = ''
    if name == "":
        for i in resp.json()['values']:
            if "COMPUTE-01" in i["name"]:
                placement_policy_href = i["id"]
                break
            elif "Gold CPU" in i["name"]:
                placement_policy_href = i["id"]
                break
            else:
                if i["description"] == "Default":
                    placement_policy_href = i["id"]
    else:
        for i in resp.json()['values']:
            if i["name"] == name:
                placement_policy_href = i["id"]
                break
            elif "COMPUTE-01" in i["name"]:
                placement_policy_href = i["id"]
                break
            elif "Gold CPU" in i["name"]:
                placement_policy_href = i["id"]
                break
            else:
                if i["description"] == "Default":
                    placement_policy_href = i["id"]

                    # print("placement_policy_href: ", placement_policy_href)
    return placement_policy_href
#
# def get_placement_policy(client, vdc_id):
#     params = RequestInfo(client)
#     uri_api = client.get_api_uri()
#     uri = uri_api.replace('/api', '')
#     resp = handle_get(
#         f"{uri}/cloudapi/2.0.0/vdcs/urn:vcloud:vdc:{vdc_id}/computePolicies?page=1&pageSize=128&filterEncoded=true&filter=isSizingOnly==false;isVgpuPolicy==false;policyType==VdcVmPolicy&links=true", headers=params.headers_compute_policy
#     )
#     policy_list = resp.json()['values']
#     print("print policy_list:", policy_list)
#     print(type(policy_list))
#     placement_policy_href = ''
#     for placement_policy in range(len(policy_list)):
#         placement_policy_detail = policy_list[placement_policy]
#         print("In for placement_policy, print placement_policy_detail: ", placement_policy_detail)
#         print(type(placement_policy_detail))
#         placement_policy_href = placement_policy_detail["id"]
#         print("print placement_policy_href:", placement_policy_href)
#         break
#     return placement_policy_href


# def get_placement_policy(client, vdc_id, name):
#     params = RequestInfo(client)
#     uri_api = client.get_api_uri()
#     uri = uri_api.replace('/api', '')
#     resp = handle_get(
#         f"{uri}/cloudapi/2.0.0/vdcs/urn:vcloud:vdc:{vdc_id}/computePolicies?page=1&pageSize=128&filterEncoded=true&filter=isSizingOnly==false;isVgpuPolicy==false;policyType==VdcVmPolicy&links=true", headers=params.headers_compute_policy
#     )
#     placement_policy_href = ''
#     for i in resp.json()['values']:
#         iname = i["name"]
#         if iname.strip() == name:
#             placement_policy_href = i["id"]
#             break
#     return placement_policy_href