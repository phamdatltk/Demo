import requests

from ansible.module_utils.requestInfo import RequestInfo
import xmltodict
from ansible.module_utils.get_vapp_template import get_vapp_template_uuid
import http.client
http.client._MAXHEADERS = 1000

def handle_get(url, headers):
    print(url)
    resp = requests.get(url, headers=headers, verify=False)
    if not resp.ok:
        raise Exception(resp.content)
    return resp

def get_vapp_vm_template_href(client, vapp_template_uuid):
    params = RequestInfo(client)
    uri = client.get_api_uri()
    resp = handle_get(
        f"{uri}/query?type=vm&format=records&type=vm&page=1&pageSize=15&filterEncoded=true&filter=(container=={vapp_template_uuid})&sortAsc=name&links=true", headers=params.xml_headers
    )
    dict_data = xmltodict.parse(resp.content)
    vapp_vm_template_href = ''
    for i in dict_data['QueryResultRecords']['VMRecord']['Link']:
        if i['@rel'] == 'self':
            vapp_vm_template_href = i['@href']
    print(vapp_vm_template_href)
    return vapp_vm_template_href

def get_vapp_vm_template_uuid(client, vapp_template_uuid):
    params = RequestInfo(client)
    uri = client.get_api_uri()
    resp = handle_get(
        f"{uri}/query?type=vm&format=records&type=vm&page=1&pageSize=15&filterEncoded=true&filter=(container=={vapp_template_uuid})&sortAsc=name&links=true", headers=params.xml_headers
    )
    dict_data = xmltodict.parse(resp.content)
    vapp_vm_template_href = ''
    vapp_vm_template_uuid = ''
    for i in dict_data['QueryResultRecords']['VMRecord']['Link']:
        if i['@rel'] == 'self':
            vapp_vm_template_href = i['@href']
            vapp_vm_template_uuid = vapp_vm_template_href.replace(f'{uri}/vApp/', '')
    print(vapp_vm_template_uuid)
    return vapp_vm_template_uuid
