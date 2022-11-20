import logging
import queue
import threading
import typer
# import redis
import socket
import time

import hazelcast
from scapy.layers.inet import IP, TCP

import sniffer

REDIS_SERVER_ADDR = '192.168.1.1'
host_var = None
redis_client = None
per_flow_packet_counter = None
flow_queue = queue.Queue(maxsize=1000000)
received_packets = 0
start_times, end_times = [], []
last_time = 0
batch_size = 10


def get_flow_from_pkt(pkt):
    tcp_sport, tcp_dport = None, None
    if IP in pkt:
        ip_src = pkt[IP].src
        ip_dst = pkt[IP].dst
        protocol = pkt[IP].proto
    if TCP in pkt:
        tcp_sport = pkt[TCP].sport
        tcp_dport = pkt[TCP].dport

    flow = (ip_src, ip_dst,
            tcp_sport, tcp_dport,
            protocol
            )
    return flow


def current_time_in_ms():
    return time.time_ns() // 1_000_000


def process_a_pkt(pkt):
    global per_flow_packet_counter
    global received_packets, last_time, times

    if received_packets % batch_size == 0:
        start_times.append(current_time_in_ms())
    received_packets += 1
    # redis_client.incr("packet_count " + host_var)
    flow = get_flow_from_pkt(pkt)
    # logging.info("Putting flow {} into queue".format(flow))
    # logging.debug("received packets {}".format(received_packets))
    flow_queue.put(flow)


def load_hazelcast():
    # Connect to Hazelcast cluster.
    client = hazelcast.HazelcastClient(
        cluster_members=[
            "10.0.0.1:5701"
            # "192.168.1.1:5701"
        ],
        # data_serializable_factories={
        #     1: factory
        # }
    )
    # Get the Distributed Map from Cluster.
    global per_flow_packet_counter
    per_flow_packet_counter = client.get_map("my-distributed-map").blocking()


def process_packet_with_hazelcast():
    global end_times
    processed_packets = 0

    print("DBG: Processing pkt")

    while True:
        flow = flow_queue.get()
        # logging.info("Extracting flow {} from queue".format(flow))
        per_flow_packet_counter.lock(flow)

        value = per_flow_packet_counter.get(flow)
        per_flow_packet_counter.set(flow, 1 if value is None else value + 1)
        # logging.info("after processing:" + str(flow) + " " + str(per_flow_packet_counter.get(flow)) + "\n")

        # logging.info("received packets {}".format(received_packets))
        processed_packets += 1
        if processed_packets % batch_size == batch_size - 1:
        # if True:
            end_times.append(current_time_in_ms())
            current_index = len(end_times)-1
            processing_time = (end_times[current_index] - start_times[current_index]) / 1000
            print(f'for batch {round(processed_packets / batch_size)} '
                  f'throughput: {batch_size / processing_time} packets/s')
        per_flow_packet_counter.unlock(flow)


# def set_host_var():
#     global host_var
#     s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     s.connect(("8.8.8.8", 80))
#     host_var = s.getsockname()[0]
#     s.close()


def main(
        interface: str = typer.Option(..., '--iface', '-i', help='Interface to run the sniffer on'),
        filter: str = typer.Option('icmp', '--filter', '-f', help='Filter on interface sniffing'),
        ip: str = typer.Option('', '--dip', help='destination Ip')

):
    global redis_client
    logging.basicConfig(level=logging.INFO)

    if ip != '':  # ip provided
        filter += ' and dst {}'.format(ip)

    # logging.info("Using Filter " + filter + " on interface " + interface)
    # logging.info("Connecting to Redis Server")
    # redis_client = redis.Redis(host=REDIS_SERVER_ADDR, port=6379, db=0)
    # set_host_var()
    # redis_client.set("packet_count " + host_var, 0)

    load_hazelcast()

    hazelcast_thread = threading. \
        Thread(target=process_packet_with_hazelcast)

    hazelcast_thread.start()

    sniffer.sniffer({
        'filter': filter,
        'iface': interface,
        'prn': process_a_pkt
    })
    hazelcast_thread.join()


if __name__ == '__main__':
    typer.run(main)
