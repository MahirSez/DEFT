import logging
import queue
import threading
import typer

import hazelcast
from scapy.layers.inet import IP, TCP

import sniffer

per_flow_packet_counter = None
flow_queue = queue.Queue(maxsize=1000000)
received_packets = 0


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


def process_a_pkt(pkt):
    global per_flow_packet_counter
    global received_packets

    received_packets += 1
    flow = get_flow_from_pkt(pkt)
    logging.info("Putting flow {} into queue".format(flow))
    # logging.debug("received packets {}".format(received_packets))
    flow_queue.put(flow)


def load_hazelcast():
    # factory = {
    #     1: Flow
    # }
    # Connect to Hazelcast cluster.
    client = hazelcast.HazelcastClient(
        cluster_members=[
            "10.0.0.1:5701"
        ],
        # data_serializable_factories={
        #     1: factory
        # }
    )
    # Get the Distributed Map from Cluster.
    global per_flow_packet_counter
    per_flow_packet_counter = client.get_map("my-distributed-map").blocking()


def process_packet_with_hazelcast():
    while True:
        flow = flow_queue.get()
        logging.info("Extracting flow {} from queue".format(flow))
        per_flow_packet_counter.lock(flow)

        value = per_flow_packet_counter.get(flow)
        per_flow_packet_counter.set(flow, 1 if value is None else value + 1)
        logging.info("after processing:" + str(flow) + " " + str(per_flow_packet_counter.get(flow)) + "\n")

        logging.info("received packets {}".format(received_packets))
        per_flow_packet_counter.unlock(flow)


def main(
        interface:  str = typer.Option(..., '--iface', '-i', help='Interface to run the sniffer on'),
        filter:     str = typer.Option('icmp', '--filter', '-f', help='Filter on interface sniffing'),
        ip:         str = typer.Option('', '--dip', help='destination Ip')

):
    logging.basicConfig(level=logging.INFO)

    if len(ip) != 0:    #  ip provided 
        filter += ' and dst {}'.format(ip)

    logging.info("Using Filter " + filter)

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
