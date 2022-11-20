from scapy.all import send, IP, ICMP, wrpcap, UDP, Ether, raw
from scapy.utils import randstring
from numpy.random import exponential

from time import time

pkts = []

class DistributionMeans():
    pkt_size = 20
    inter_arrival_time = 0.003  # 300 pkts / sec 

def get_next_pkt_size():
    return round(exponential(DistributionMeans.pkt_size))

def get_next_pkt_delay():
    return exponential(DistributionMeans.inter_arrival_time)


def main():
    cur_timestamp = time()
    NUM_OF_PKTS = 1000

    for _ in range(NUM_OF_PKTS):

        pkt = Ether()/IP(src="10.0.0.2",dst="10.0.0.1")/UDP()/raw(randstring(get_next_pkt_size()))
        cur_timestamp += get_next_pkt_delay()
        pkt.time = cur_timestamp

        pkts.append(pkt)

    wrpcap('icmp-pkt.pcap', pkts)

main()