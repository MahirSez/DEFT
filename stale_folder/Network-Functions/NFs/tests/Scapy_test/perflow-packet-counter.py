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

    Statistics.received_packets += 1
    flow = get_flow_from_pkt(pkt)
    
    print(f'pkt-id [{Statistics.received_packets}]: {flow}, len - {len(pkt)} ')


def main(
        interface: str = typer.Option(..., '--iface', '-i', help='Interface to run the sniffer on'),
        filter: str = typer.Option('icmp', '--filter', '-f', help='Filter on interface sniffing'),
        ip: str = typer.Option('', '--dip', help='destination Ip')

):
    if ip != '':  # ip provided
        filter += ' and dst {}'.format(ip)

    sniffer.sniffer({
        'filter': filter,
        'iface': interface,
        'prn': process_a_pkt
    })

if __name__ == '__main__':
    typer.run(main)
