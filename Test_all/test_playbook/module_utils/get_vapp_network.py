import requests
import json
from requests.packages import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
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

def check_vapp_network(client, name, vapp_uuid):
    # name is name of vApp Network
    params = RequestInfo(client)
    resp = handle_get(
            f"{params.api_url}/query?type=vAppNetwork&format=records&type=vAppNetwork&page=1&pageSize=100&filterEncoded=true&filter=((vApp=={vapp_uuid}))&sortAsc=name&links=true",
            headers=params.xml_headers,
        )
    if not resp.ok:
        raise Exception(resp.content)
    dict_data = xmltodict.parse(resp.content)
    try:
        for i in dict_data['QueryResultRecords']['VAppNetworkRecord']:
            print(i['@name'])
            if i['@name'] == name:
                return True
    except TypeError:
        if dict_data['QueryResultRecords']['VAppNetworkRecord']['@name'] == name:
            return True
    except KeyError:
        return False
        
    return False