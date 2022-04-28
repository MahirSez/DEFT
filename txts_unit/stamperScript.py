from scapy.all import *
from scapy.layers.inet import IP, ICMP
from scapy.layers.l2 import Ether


def forward_to_sw2(pkt):
    print("=========================")
    print(pkt.summary())
    pkt[IP].src = '10.0.0.4'
    pkt[Ether].src = '00:00:00:00:00:04'
    sendp(pkt, iface='stamper-eth0')


print("Stamper sniffing packets on stamper-eth0....")
sniff(filter='ip src host 10.0.0.1', iface="stamper-eth0", prn=forward_to_sw2)

