from scapy.all import *


def forward_to_sw2(pkt):
    print("=========================")
    pkt.summary()
    sendp(pkt, iface='stamper-eth1')


print("Stamper sniffing packets on eth0....")
sniff(iface="stamper-eth0", prn=forward_to_sw2)
