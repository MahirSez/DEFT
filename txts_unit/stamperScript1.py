from scapy.all import *


def forward_to_sw1(pkt):
    print("=========================")
    pkt.summary()
    sendp(pkt, iface='stamper-eth0')


print("Stamper sniffing packets on eth1....")
sniff(iface="stamper-eth1", prn=forward_to_sw1)
