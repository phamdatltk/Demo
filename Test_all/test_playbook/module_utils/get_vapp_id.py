import requests
from requests.packages import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from ansible.module_utils.requestInfo import RequestInfo
import xmltodict
from ansible.module_utils.get_vdc_id import get_vdc_id
import http.client
http.client._MAXHEADERS = 1000

def handle_get(url, headers):
    print(url)
    resp = requests.get(url, headers=headers, verify=False)
    if not resp.ok:
        raise Exception(resp.content)
    return resp

def get_vapp_id(client, name, vdc_name):
    # name is name of vApp
    vdc_id = get_vdc_id(client, vdc_name)
    params = RequestInfo(client)
    resp = handle_get(
            f"{params.api_url}/query?type=vApp&page=1&pageSize=2000&filterEncoded=true&filter=(vdc=={vdc_id})",
            headers=params.xml_headers,
        )
    if not resp.ok:
        raise Exception(resp.content)
    dict_data = xmltodict.parse(resp.content)
    vapp_id = ""
    vapp_href = ""
    # print(dict_data["QueryResultRecords"])
    try:
        for i in dict_data["QueryResultRecords"]["VAppRecord"]:
            if i["@name"] == name:
                vapp_href = i["@href"]
                vapp_id = vapp_href.replace(f"{params.api_url}/vApp/", '')
                # print(vapp_href)
    except TypeError:
        if dict_data["QueryResultRecords"]["VAppRecord"]["@name"] == name:
            vapp_href = dict_data["QueryResultRecords"]["VAppRecord"]["@href"]
            vapp_id = vapp_href.replace(f"{params.api_url}/vApp/", '')
    print(vapp_id)
    return vapp_id

def get_vapp_uuid(client, name, vdc_name):
    # name is name of vApp
    vdc_id = get_vdc_id(client, vdc_name)
    params = RequestInfo(client)
    resp = handle_get(
            f"{params.api_url}/query?type=vApp&page=1&pageSize=2000&filterEncoded=true&filter=(vdc=={vdc_id})",
            headers=params.xml_headers,
        )
    if not resp.ok:
        raise Exception(resp.content)
    dict_data = xmltodict.parse(resp.content)
    vapp_id = ""
    vapp_href = ""
    vapp_uuid = ""
    # print(dict_data["QueryResultRecords"])
    try:
        for i in dict_data["QueryResultRecords"]["VAppRecord"]:
            if i["@name"] == name:
                vapp_href = i["@href"]
                vapp_id = vapp_href.replace(f"{params.api_url}/vApp/", '')
                vapp_uuid = vapp_id.replace("vapp-", '')
                # print(vapp_href)
    except TypeError:
        if dict_data["QueryResultRecords"]["VAppRecord"]["@name"] == name:
            vapp_href = dict_data["QueryResultRecords"]["VAppRecord"]["@href"]
            vapp_id = vapp_href.replace(f"{params.api_url}/vApp/", '')
            vapp_uuid = vapp_id.replace("vapp-", '')
    print(vapp_uuid)
    return vapp_uuid