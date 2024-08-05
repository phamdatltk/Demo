import time

import requests
from ansible.module_utils.requestInfo import RequestInfo
import xmltodict
import http.client
http.client._MAXHEADERS = 1000

def handle_get(url, headers):
    print(url)
    resp = requests.get(url, headers=headers, verify=False)
    if not resp.ok:
        raise Exception(resp.content)
    return resp

def get_vm_href(client, vapp_uuid, vm_name):
    params = RequestInfo(client)
    resp = handle_get(
            f"{params.api_url}/query?type=vm&format=records&type=vm&page=1&pageSize=100&filterEncoded=true&filter=(container=={vapp_uuid})&sortAsc=name&links=true",
            headers=params.xml_headers,
        )
    if not resp.ok:
        raise Exception(resp.content)
    dict_data = xmltodict.parse(resp.content)
    vm_href = ""
    try:
        for i in dict_data["QueryResultRecords"]["VMRecord"]:
            if i["@name"] == vm_name:
                vm_href = i["@href"]
    except TypeError:
        if dict_data["QueryResultRecords"]["VMRecord"]["@name"] == vm_name:
            vm_href = dict_data["QueryResultRecords"]["VMRecord"]["@href"]

    return vm_href

def get_vm_id(client, vapp_uuid, vm_name):
    params = RequestInfo(client)
    resp = handle_get(
            f"{params.api_url}/query?type=vm&format=records&type=vm&page=1&pageSize=100&filterEncoded=true&filter=(container=={vapp_uuid})&sortAsc=name&links=true",
            headers=params.xml_headers,
        )
    if not resp.ok:
        raise Exception(resp.content)
    dict_data = xmltodict.parse(resp.content)
    vm_href = ""
    vm_id = ""
    try:
        for i in dict_data["QueryResultRecords"]["VMRecord"]:
            if i["@name"] == vm_name and i["@isBusy"] == "false":
                vm_href = i["@href"]
                vm_id = vm_href.replace(f"{params.api_url}/vApp/", '')
    except TypeError:
        if dict_data["QueryResultRecords"]["VMRecord"]["@name"] == vm_name and dict_data["QueryResultRecords"]["VMRecord"]["@isBusy"] == "false":
            vm_href = dict_data["QueryResultRecords"]["VMRecord"]["@href"]
            vm_id = vm_href.replace(f"{params.api_url}/vApp/", '')
    except KeyError:
        return ""
    return vm_id

def get_list_vm_info(client, vm_list, vapp_uuid):
    vms_info = list()
    for vm in vm_list:
        vms_info.append({"vm_href": get_vm_href(client, vapp_uuid, vm), "vm_id": get_vm_id(client, vapp_uuid, vm), "vm_name": vm})
    # print(vms_info)
    return vms_info

def get_vm_ip(client, vapp_uuid, vm_name):
    params = RequestInfo(client)
    resp = handle_get(
            f"{params.api_url}/query?type=vm&format=records&type=vm&page=1&pageSize=100&filterEncoded=true&filter=(container=={vapp_uuid})&sortAsc=name&links=true",
            headers=params.xml_headers,
        )
    if not resp.ok:
        raise Exception(resp.content)
    dict_data = xmltodict.parse(resp.content)
    vm_ip = ""
    try:
        for i in dict_data["QueryResultRecords"]["VMRecord"]:
            # print(i["@name"])
            if i["@name"] == vm_name:
                vm_ip = i["@ipAddress"]
    except TypeError:
        if dict_data["QueryResultRecords"]["VMRecord"]["@name"] == vm_name:
            vm_ip = dict_data["QueryResultRecords"]["VMRecord"]["@ipAddress"]

    return vm_ip

def get_vm_status(client, vapp_uuid, vm_name):
    params = RequestInfo(client)
    resp = handle_get(
            f"{params.api_url}/query?type=vm&format=records&type=vm&page=1&pageSize=100&filterEncoded=true&filter=(container=={vapp_uuid})&sortAsc=name&links=true",
            headers=params.xml_headers,
        )
    if not resp.ok:
        raise Exception(resp.content)
    dict_data = xmltodict.parse(resp.content)
    vm_status = ""
    try:
        for i in dict_data["QueryResultRecords"]["VMRecord"]:
            # print(i["@name"])
            if i["@name"] == vm_name:
                vm_status = i["@status"]
    except TypeError:
        if dict_data["QueryResultRecords"]["VMRecord"]["@name"] == vm_name:
            vm_status = dict_data["QueryResultRecords"]["VMRecord"]["@status"]

    return vm_status

def check_busy_vcd(client, vapp_uuid, vm_name):
    params = RequestInfo(client)
    resp = handle_get(
            f"{params.api_url}/query?type=vm&format=records&type=vm&page=1&pageSize=100&filterEncoded=true&filter=(container=={vapp_uuid})&sortAsc=name&links=true",
            headers=params.xml_headers,
        )
    if not resp.ok:
        raise Exception(resp.content)
    dict_data = xmltodict.parse(resp.content)
    is_busy_vcd = ""
    try:
        for i in dict_data["QueryResultRecords"]["VMRecord"]:
            # print(i["@name"])
            if i["@name"] == vm_name:
                is_busy_vcd = i["@isBusy"]
    except TypeError:
        if dict_data["QueryResultRecords"]["VMRecord"]["@name"] == vm_name:
            is_busy_vcd = dict_data["QueryResultRecords"]["VMRecord"]["@isBusy"]

    return is_busy_vcd