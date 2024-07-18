from opensearchpy import OpenSearch
from datetime import datetime
import random


host = '10.20.10.4'
port = 9200
auth = ('admin', 'qfeBYTUU5tI1')  # For testing only. Don't store credentials in code.

# Create the client with SSL/TLS enabled, but hostname verification disabled.
client = OpenSearch(
    hosts=[{'host': host, 'port': port}],
    http_compress=True,  # enables gzip compression for request bodies
    http_auth=auth,
    use_ssl=True,
    verify_certs=False,
    ssl_assert_hostname=False,
    ssl_show_warn=False,
)

listCity = ["HaNoi", "SaiGon", "Can Tho", "Hai Phong", "Da Nang", "Thanh Hoa", "Binh Duong", "Quang Binh",
                    "Quang Tri"]


# Add a document to the index fde_demo_index.
for i in range(1000):
    document = {
        'title': random.choice(listCity),
        'checkYear': random.randint(1900, 2025),
        'description': "Data of fde_demo_index_no_replica",
        'timestamp': datetime.utcnow().isoformat()  # Current timestamp
    }

    response = client.index(index='fde_demo_index', body=document)
    print(response)


# Add a document to the index fde_demo_index_no_replica.
for i in range(1000):
    document = {
        'title': random.choice(listCity),
        'checkYear': random.randint(1900, 2025),
        'description': "Data of fde_demo_index_no_replica",
        'timestamp': datetime.utcnow().isoformat()  # Current timestamp
    }

    response = client.index(index='fde_demo_index_no_replica', body=document)
    print(response)
    
# Add a document to the index fde_demo_index_two_shard.
for i in range(1000):
    document = {
        'title': random.choice(listCity),
        'checkYear': random.randint(1900, 2025),
        'description': "Data of fde_demo_index_two_shard",
        'timestamp': datetime.utcnow().isoformat()  # Current timestamp
    }

    response = client.index(index='fde_demo_index_two_shard', body=document)
    print(response)
    
# Add a document to the index fde_demo_index_no_replica_two_shard.
for i in range(1000):
    document = {
        'title': random.choice(listCity),
        'checkYear': random.randint(1900, 2025),
        'description': "Data of fde_demo_index_no_replica_two_shard",
        'timestamp': datetime.utcnow().isoformat()  # Current timestamp
    }

    response = client.index(index='fde_demo_index_no_replica_two_shard', body=document)
    print(response)