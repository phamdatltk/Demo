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

def get_anti_affinity_rule_id(client, vcd_url, vdc_id, anti_affinity_rule_name):
    params = RequestInfo(client)
    resp = handle_get(
        f"{vcd_url}/api/vdc/{vdc_id}/vmAffinityRules/", headers=params.xml_headers
    )
    dict_data = xmltodict.parse(resp.content)
    anti_affinity_rule_id = ''
    try:
        for i in dict_data['VmAffinityRules']["VmAffinityRule"]:
            print(i["Name"])
            if i["Name"] == anti_affinity_rule_name:
                anti_affinity_rule_id = i["@id"]
        return anti_affinity_rule_id
    except TypeError:
        if dict_data['VmAffinityRules']["VmAffinityRule"]["Name"] == anti_affinity_rule_name:
            anti_affinity_rule_id = dict_data['VmAffinityRules']["VmAffinityRule"]["@id"]
        return anti_affinity_rule_id
    except KeyError:
        return ''
