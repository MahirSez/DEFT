from scapy.layers.inet import IP, TCP

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
            # tcp_sport, tcp_dport,
            protocol
            )
            
    return flow

def get_string_of_flow(flow: tuple) -> str:
    """
        returns a string format of flow
    """

    return f"{flow[0]},{flow[1]},{flow[2]}"