import requests
from ansible.module_utils.requestInfo import RequestInfo
import http.client
http.client._MAXHEADERS = 1000

def handle_get(url, headers):
    print("debug handle_get url:", url)
    print(url)
    resp = requests.get(url, headers=headers, verify=False)
    if not resp.ok:
        raise Exception(resp.content)
    return resp

def get_vapp_template_href(client, catalogName, vapp_template_name):
    params = RequestInfo(client)
    uri = client.get_api_uri()
    resp = handle_get(
        f"{uri}/query?type=vAppTemplate&format=records&page=1&pageSize=1000&filterEncoded=true&filter=((isExpired==false))&sortAsc=name&links=true", headers=params.json_special_headers
    )
    vapp_template_href = ''
    for i in resp.json()['record']:
        if i['catalogName'] == catalogName and i['name'] == vapp_template_name:
            vapp_template_href = i['href']
    print(vapp_template_href)
    return vapp_template_href

def get_vapp_template_uuid(client, catalogName, vapp_template_name):
    params = RequestInfo(client)
    uri = client.get_api_uri()
    resp = handle_get(
        f"{uri}/query?type=vAppTemplate&format=records&page=1&pageSize=1000&filterEncoded=true&filter=((isExpired==false);(name==*{vapp_template_name}*))&sortAsc=name&links=true", headers=params.json_special_headers
    )
    vapp_template_href = ''
    vapp_template_uuid = ''
    for i in resp.json()['record']:
        if i['catalogName'] == catalogName and i['name'] == vapp_template_name:
            vapp_template_href = i['href']
            vapp_template_uuid = vapp_template_href.replace(f'{uri}/vAppTemplate/vappTemplate-', '')
    return vapp_template_uuid