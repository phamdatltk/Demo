class RequestInfo:
    client = None
    headers = None
    xml_headers = None
    api_url = None
    version_url = None

    def __init__(self, client):
        self.version_url = f"{client.get_cloudapi_uri()}/1.0.0"
        self.api_url = client.get_api_uri()
        self.client = client
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json;version=35.0",
            "Authorization": f"Bearer {client._vcloud_access_token}",
        }
        self.xml_headers = {
            "Content-Type": "application/*+xml",
            "Accept": "application/*+xml;version=35.0",
            "Authorization": f"Bearer {client._vcloud_access_token}",
        }
        self.xml_networkConfigSection_headers = {
            "Content-Type": "application/vnd.vmware.vcloud.networkConfigSection+xml",
            "Accept": "application/*+xml;version=35.0",
            "Authorization": f"Bearer {client._vcloud_access_token}",
        }
        self.json_special_headers = {
            "Content-Type": "application/json",
            "Accept": "application/*+json;version=35.0",
            # "X-VMWARE-VCLOUD-TENANT-CONTEXT": "a4e7638a-47bc-4474-b132-894a851d8f4e",
            "Authorization": f"Bearer {client._vcloud_access_token}",
        }
        self.headers_token = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json;version=36.2",
            "Authorization": f"Bearer {client._vcloud_access_token}",
        }
        self.headers_compute_policy = {
            "Content-Type": "application/json",
            "Accept": "application/json;version=36.2",
            "Authorization": f"Bearer {client._vcloud_access_token}",
        }
        self.headers_compute_policy = {
            "Content-Type": "application/json",
            "Accept": "application/json;version=36.2",
            "Authorization": f"Bearer {client._vcloud_access_token}",
        }
        self.json_edge_gateway_headers = {
            "Content-Type": "application/*+json",
            "Accept": "application/*+json;version=36.3",
            "Authorization": f"Bearer {client._vcloud_access_token}",
        }