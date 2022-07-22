from scapy.all import *
from scapy.layers.inet import IP, TCP

per_flow_stamp = {}


CLIENT_IP = '10.0.0.1'


def get_flow_from_pkt(pkt) -> tuple:
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


def get_string_of_flow(flow: tuple) -> str:
    return f"{flow[0]},{flow[1]},{flow[2]},{flow[3]},{flow[4]}"


def forward_to_sw2(pkt):

    flow_id = get_flow_from_pkt(pkt)

    if flow_id not in per_flow_stamp:
        per_flow_stamp[flow_id] = 0

    cnt = per_flow_stamp[flow_id]

    if Raw in pkt:
        pkt[Raw].add_payload(raw("ID = " + str(cnt)))
        print('................')

        pl = pkt[Raw].payload
        print(type(pl))

        print("%s: %s" % (bytes(pkt[Raw].payload).decode(), cnt))


    per_flow_stamp[flow_id] += 1
    sendp(pkt, iface='stamper-eth1')



if __name__ == '__main__':
    print("Stamper sniffing packets on stamper-eth0....")
    sniff(filter='ip src host {}'.format(CLIENT_IP), iface="stamper-eth0", prn=forward_to_sw2)
    # sniff(filter='ip', iface="stamper-eth0", prn=forward_to_sw2)



