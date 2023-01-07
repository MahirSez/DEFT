from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from dataclasses import dataclass

import os
from dotenv import load_dotenv

load_dotenv()

HZ_CLIENT_CNT = int(os.getenv('HZ_CLIENT_CNT'))
HZ_CLIENT_IP_PATTERN = os.getenv('HZ_CLIENT_IP_PATTERN')

STAMPER_LISTEN_PORT = int(os.getenv('STAMPER_LISTEN_PORT'))
HZ_CLIENT_LISTEN_PORT = int(os.getenv('HZ_CLIENT_LISTEN_PORT'))


@dataclass
class Flow:
    src_ip: str
    src_port: str


class Stamper(DatagramProtocol):

    def __init__(self):
        self.next_client = 0

        # should use redis
        self.flow_to_client = {} 
        self.flow_pkt_cnt = {}

        self.hz_client_ips = []

        for i in range(HZ_CLIENT_CNT):
            # adding with `i+2` because the ip of the ovs-br1 interface will be 173.16.1.1
            client_ip = HZ_CLIENT_IP_PATTERN.replace('$', str(i + 2))
            self.hz_client_ips.append(client_ip)
        
        print('Configured hz_clint IP list:')
        print(self.hz_client_ips)

    def select_hz_client(self, flow):
        if flow not in self.flow_to_client:
            self.flow_to_client[flow] = self.hz_client_ips[self.next_client]
            self.next_client = (self.next_client + 1) % HZ_CLIENT_CNT

        return self.flow_to_client[flow]

    def stamp_packet(self, data, flow):
        if flow not in self.flow_pkt_cnt:
            self.flow_pkt_cnt[flow] = 0

        stamp = f'\n{self.flow_pkt_cnt[flow]}\n'
        data += bytes(stamp, 'ascii')

        return data


    
    def datagramReceived(self, data, src_addr):
        src_ip, src_port = src_addr

        print(f'received {data} from ({src_ip}, {src_port})')
        

        dst_hz_client = self.select_hz_client(src_addr)

        print(f'forwarding to ip {dst_hz_client} & port {HZ_CLIENT_LISTEN_PORT}')

        data = self.stamp_packet(data, src_addr)

        self.transport.write(data, (dst_hz_client, HZ_CLIENT_LISTEN_PORT))

reactor.listenUDP(STAMPER_LISTEN_PORT, Stamper())
print(f'Listening on port {STAMPER_LISTEN_PORT}...')

reactor.run()
