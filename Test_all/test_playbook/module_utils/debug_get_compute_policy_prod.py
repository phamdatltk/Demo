import requests
from ansible.module_utils.requestInfo import RequestInfo
from pyvcloud.vcd.client import BasicLoginCredentials, Client

import urllib3
urllib3.disable_warnings()

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

def get_placement_policy(client, vdc_id):
    params = RequestInfo(client)
    uri_api = client.get_api_uri()
    uri = uri_api.replace('/api', '')
    resp = handle_get(
        f"{uri}/cloudapi/2.0.0/vdcs/urn:vcloud:vdc:{vdc_id}/computePolicies?page=1&pageSize=128&filterEncoded=true&filter=isSizingOnly==false;isVgpuPolicy==false;policyType==VdcVmPolicy&links=true", headers=params.headers_compute_policy
    )
    policy_list = resp.json()['values']
    print(type(policy_list))
    placement_policy_href = ''
    for placement_policy in range(len(policy_list)):
        placement_policy_detail = policy_list[placement_policy]
        print(type(placement_policy_detail))
        placement_policy_href = placement_policy_detail["id"]
        break



# def get_placement_policy(client, vdc_id):
#     params = RequestInfo(client)
#     uri_api = client.get_api_uri()
#     uri = uri_api.replace('/api', '')
#     resp = handle_get(
#         f"{uri}/cloudapi/2.0.0/vdcs/urn:vcloud:vdc:{vdc_id}/computePolicies?page=1&pageSize=128&filterEncoded=true&filter=isSizingOnly==false;isVgpuPolicy==false;policyType==VdcVmPolicy&links=true", headers=params.headers_compute_policy
#     )
#     policy_list = resp.json()['values']
#     print(policy_list)
#     print(type(policy_list))
#     for placement_policy in range(len(policy_list)):
#         placement_policy_detail = policy_list[placement_policy]
#         placement_policy_name = placement_policy_detail["name"]
#     # placement_policy_href = ''
#     # for i in resp.json()['values']:
#     #     iname = i["name"]
#     #     if iname.strip() == name:
#     #         placement_policy_href = i["id"]
#     #         break
#     # return placement_policy_name
#         return placement_policy_detail

def login(org, user, password,
          api_version="35.0",
          verify_ssl_certs=False,
          log_file="vcd.log",
          log_request=False,
          log_header=False,
          log_body=False):
    client = Client(
        # "{{ vcd_url }}",
        "https://han.fptcloud.com",
        api_version=api_version,
        verify_ssl_certs=verify_ssl_certs,
        log_file=log_file,
        log_requests=log_request,
        log_headers=log_header,
        log_bodies=log_body,
    )
    client.set_credentials(BasicLoginCredentials(user, org, password))
    return client

client = login("XPLAT-HAN-ORG", "truongvv10", "okd@123")
list_policy = get_placement_policy(client, "60e42ab8-6ca2-48e4-8d9e-0e1d016e3f80")
print(list_policy)
# print(client.__dict__)

