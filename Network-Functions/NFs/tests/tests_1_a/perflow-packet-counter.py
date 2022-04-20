import logging
import queue
import threading
import typer
# import redis
import socket
import time

from numpy.random import exponential

import hazelcast
from scapy.layers.inet import IP, TCP

import sniffer

REDIS_SERVER_ADDR = '192.168.1.1'
host_var = None
redis_client = None


per_flow_packet_counter = None
pkt_queue = queue.Queue(maxsize=1000000)
last_time = 0

class Timestamps():
    start_times, end_times = None, None 

# @dataclass(frozen=True)
class Limit():
    BATCH_SIZE = 20
    PKTS_NEED_TO_PROCESS = 1000


class Statistics():
    processed_pkts = 0
    received_packets = 0
    total_packet_sizes = 0
    total_three_pc_time = 0

# (st_time, en_time) - processing time
# additional 3pc time 

# input_buffer
# output_buffer


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


def get_3pc_time():
    return exponential(scale=0.3)


def current_time_in_ms():
    return time.time_ns() // 1_000_000


def process_a_pkt(pkt):
    global start_time, received_packets

    if Statistics.received_packets % Limit.BATCH_SIZE == 0 \
        and Statistics.received_packets == 0:
        Timestamps.start_time = current_time_in_ms()

    Statistics.received_packets += 1
    # redis_client.incr("packet_count " + host_var)
    flow = get_flow_from_pkt(pkt)
    
    # logging.info("Putting flow {} into queue".format(flow))
    # print("received packets {}".format(Statistics.received_packets))
    pkt_queue.put(pkt)


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

    map_key = "global"

    while True:
        pkt = pkt_queue.get()

        Statistics.processed_pkts += 1
        Statistics.total_packet_sizes += len(pkt)

        if Statistics.processed_pkts % Limit.BATCH_SIZE == Limit.BATCH_SIZE - 1:
            Statistics.total_three_pc_time += get_3pc_time()
            Timestamps.end_time = (current_time_in_ms())

            per_flow_packet_counter.lock(map_key)

            value = per_flow_packet_counter.get(map_key)
            per_flow_packet_counter.set(map_key, 1 if value is None else value + 1)
            # logging.info("after processing:" + str(flow) + " " + str(per_flow_packet_counter.get(flow)) + "\n")

            # logging.info("received packets {}".format(received_packets))
            per_flow_packet_counter.unlock(map_key)

        if Statistics.processed_pkts == Limit.PKTS_NEED_TO_PROCESS:
            time_delta = Timestamps.end_time - Timestamps.start_time
            process_time = time_delta / 1000.0 + Statistics.total_three_pc_time

            print(f'Throughput for batch-size {Limit.BATCH_SIZE} is {Statistics.total_packet_sizes/process_time} byte/s')
            break


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


    print(f'batch {Limit.BATCH_SIZE} , pkts_needed: {Limit.PKTS_NEED_TO_PROCESS}')

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
