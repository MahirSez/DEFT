from scapy.all import *
import time

print("SNIFFING PACKETS.........")

i = 0
end_time = 0
start_time = 0


def print_pkt(pkt):
    global i, start_time, end_time
    i += 1
    if i == 1:
        start_time = time.time()
    if i == 10:
        end_time = time.time()


pkt = sniff(iface='h1-eth0', filter='icmp and dst 10.0.0.1', prn=print_pkt, count=10)

print(end_time - start_time)