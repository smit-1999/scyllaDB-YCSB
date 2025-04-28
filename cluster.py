import uuid
from cassandra.cluster import Cluster
import random
import time
import docker

def get_container_ips(container_names):
    client = docker.from_env()
    ips = []
    for name in container_names:
        try:
            container = client.containers.get(name)
            ip_address = container.attrs['NetworkSettings']['IPAddress']
            ips.append(ip_address)
        except docker.errors.NotFound:
            print(f"❌ Container {name} not found.")
    return ips