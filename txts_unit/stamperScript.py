from scapy.all import *
from scapy.layers.inet import IP

per_host_stamp = {}


CLIENT_IP = '10.0.0.1'

def forward_to_sw2(pkt):
    if pkt[IP].dst not in per_host_stamp:
        per_host_stamp[pkt[IP].dst] = 0

    cnt = per_host_stamp[pkt[IP].dst]

    pkt[Raw].add_payload(raw("ID = " + str(cnt)))
    print("%s: %s" % (pkt[IP].dst, cnt))

    per_host_stamp[pkt[IP].dst] += 1
    sendp(pkt, iface='stamper-eth1')



if __name__ == '__main__':
    print("Stamper sniffing packets on stamper-eth0....")
    sniff(filter='ip src host %s' % CLIENT_IP, iface="stamper-eth0", prn=forward_to_sw2)


