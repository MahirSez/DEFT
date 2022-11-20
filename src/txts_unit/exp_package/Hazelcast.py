import hazelcast
from typing import List

def load_hazelcast(cluster_members: List[str]):
    """
        Connect to hazelcast cluster
    """

    client = hazelcast.HazelcastClient(cluster_members=cluster_members)
    return client


def create_per_flow_packet_counter(hazelcast_client):
    """
        Get the Distributed Map from Cluster
    """
    
    return hazelcast_client.get_map("my-distributed-map").blocking()