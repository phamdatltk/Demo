from pyvcloud.vcd.client import (
    BasicLoginCredentials,
    Client
)
def login(org, user, password,
        host=None,
        api_version="35.0",
        verify_ssl_certs=False,
        log_file="vcd.log",
        log_request=False,
        log_header=False,
        log_body=False):
        client = Client(
            host,
            api_version=api_version,
            verify_ssl_certs=verify_ssl_certs,
            log_file=log_file,
            log_requests=log_request,
            log_headers=log_header,
            log_bodies=log_body,
        )
        client.set_credentials(BasicLoginCredentials(user, org, password))
        return client