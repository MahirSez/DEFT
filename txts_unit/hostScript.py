import sys

from scapy.all import *
from scapy.layers.inet import IP, ICMP
from scapy.layers.l2 import Ether

CLIENT_IP = '10.0.0.1'


def forward_to_sw2(pkt):
    print(pkt[Raw].payload)
    # reply_pkt = Ether() / IP(dst=pkt[IP].src) / ICMP(type='echo-reply', id=pkt[ICMP].id, seq=pkt[ICMP].seq)
    # sendp(reply_pkt)


if __name__ == '__main__':
    # if len(sys.argv) != 2:
    #     print("Missing Argument: <host_name>")
    #     exit(0)

    # print("%s sniffing packets...." % sys.argv[1])
    print("host sniffing packets....")
    sniff(filter='ip src host %s' % CLIENT_IP, prn=forward_to_sw2)
