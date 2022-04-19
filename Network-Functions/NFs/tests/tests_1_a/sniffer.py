from scapy.all import *


def sniffer(kwargs):
    print("SNIFFING PACKETS.........")
    pkt = sniff(**kwargs)


