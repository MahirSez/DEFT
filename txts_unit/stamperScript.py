import sys

import typer as typer
from scapy.all import *
from scapy.layers.inet import IP, ICMP
from scapy.layers.l2 import Ether

cnt = 0


def forward_to_sw2(pkt):
    global cnt
    pkt[Raw].add_payload(raw("ID = " + str(cnt)))
    print(cnt)
    cnt += 1
    sendp(pkt, iface='stamper-eth1')






if __name__ == '__main__':
    print("Stamper sniffing packets on stamper-eth0....")
    sniff(filter='ip src host 10.0.0.1', iface="stamper-eth0", prn=forward_to_sw2)


