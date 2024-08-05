import re
import requests
import json
import argparse

from ansible.module_utils.requestInfo import RequestInfo
from netaddr import IPNetwork
import http.client
http.client._MAXHEADERS = 1000

def handle_get(url, headers):
    print(url)
    print(headers)
    resp = requests.get(url, headers=headers, verify=False)
    if not resp.ok:
        raise Exception(resp.content)
    return resp

def get_orgVdcNetwork(client, name):
    #name is name of interal network
    params = RequestInfo(client)

    #resp = handle_get(f"{params.version_url}/orgVdcNetworks?page=1&pageSize=1000", headers=params.headers)
    resp = handle_get(f"{params.version_url}/orgVdcNetworks?filter=name%3D%3D{name}&page=1&pageSize=1000", headers=params.headers)
    print(resp.json()) 
    #print(resp.json()) 
    orgVdcNetwork = dict()
    for i in resp.json()["values"]:
        if i["name"] == name:
            orgVdcNetwork = i
    orgVdcNetwork['uuid'] = orgVdcNetwork['id'].replace("urn:vcloud:network:", '')
    print(orgVdcNetwork['uuid'])
    print(orgVdcNetwork['id'])
    print(orgVdcNetwork["subnets"]["values"][0]["gateway"])
    print(orgVdcNetwork["subnets"]["values"][0]["prefixLength"])
    gateway = orgVdcNetwork["subnets"]["values"][0]["gateway"]
    prefixLength = orgVdcNetwork["subnets"]["values"][0]["prefixLength"]
    gw_cidr = f"{gateway}/{prefixLength}"
    network_addr = IPNetwork(gw_cidr).network
    orgVdcNetwork['subnet_cidr'] = f"{network_addr}/{prefixLength}"
    # print(orgVdcNetwork)
    return orgVdcNetwork
