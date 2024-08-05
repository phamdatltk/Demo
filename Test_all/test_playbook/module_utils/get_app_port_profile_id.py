import requests
import json
import argparse

from ansible.module_utils.requestInfo import RequestInfo
import http.client
http.client._MAXHEADERS = 1000

def handle_get(url, headers):
    print(url)
    resp = requests.get(url, headers=headers, verify=False)
    if not resp.ok:
        raise Exception(resp.content)
    return resp

def get_app_port_profile_urn(client, app_port_profile_name, port, protocol, context, scope):
    params = RequestInfo(client)

    resp = handle_get(
        f"{params.version_url}/applicationPortProfiles?page=1&pageSize=2000&filterEncoded=true&filter=(_context=={context};scope=={scope};usableForNAT==true;applicationPorts.protocol=={protocol};applicationPorts.destinationPorts=={port})&sortAsc=name&links=true", headers=params.headers
    )
    # return resp.json()
    # print(resp.json()["values"])
    app_port_profile_id = ""
    for i in resp.json()["values"]:
        # for j in i["applicationPorts"]:
        #     if j["protocol"] == protocol and j["destinationPorts"] == [port]:
        #         app_port_profile_id = i["id"]
        #         # print(app_port_profile_id)
        if i["name"] == app_port_profile_name:
            app_port_profile_id = i["id"]
    return app_port_profile_id
