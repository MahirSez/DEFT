from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from dataclasses import dataclass

import os
from dotenv import load_dotenv
import redis

load_dotenv()

HZ_CLIENT_CNT = int(os.getenv('HZ_CLIENT_CNT'))
HZ_CLIENT_IP_PATTERN = os.getenv('HZ_CLIENT_IP_PATTERN')

STAMPER_LISTEN_PORT = int(os.getenv('STAMPER_LISTEN_PORT'))
HZ_CLIENT_LISTEN_PORT = int(os.getenv('HZ_CLIENT_LISTEN_PORT'))
GLOBAL_KEY = 'NEXT_CLIENT'


@dataclass
class Flow:
    src_ip: str
    src_port: str


class Stamper(DatagramProtocol):

    def __init__(self):

        self.pkt_cnt = 0
        self.pkt_cnt_since_last_reading = 0

        self.redis_client = redis.Redis(host='redis')

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

            next_client = self.redis_client.incr(GLOBAL_KEY) % HZ_CLIENT_CNT
            self.flow_to_client[flow] = self.hz_client_ips[next_client]

        return self.flow_to_client[flow]

    def stamp_packet(self, data, flow):
        if flow not in self.flow_pkt_cnt:
            self.flow_pkt_cnt[flow] = 0

        # data = bytes.fromhex(data).decode('utf-8')
        # print(f'data in stamp_packet method {data}')
        stamp = f'\n{flow}\n'
        stamp += f'{self.flow_pkt_cnt[flow]}'
        data += bytes(stamp, 'ascii')

        return data

    def incr_pkt_cnt(self, flow):
        self.flow_pkt_cnt[flow] += 1

    
    def datagramReceived(self, data, src_addr):
        src_ip, src_port = src_addr

        dst_hz_client = self.select_hz_client(src_addr)

        self.pkt_cnt += 1
        self.pkt_cnt_since_last_reading += 1
        if self.pkt_cnt_since_last_reading == 1000:
            print("Packets processed: ", self.pkt_cnt)
            self.pkt_cnt_since_last_reading = 0

        data = self.stamp_packet(data, src_addr)
        self.incr_pkt_cnt(src_addr)

        self.transport.write(data, (dst_hz_client, HZ_CLIENT_LISTEN_PORT))

reactor.listenUDP(STAMPER_LISTEN_PORT, Stamper())
print(f'Listening on port {STAMPER_LISTEN_PORT}...')

reactor.run()
