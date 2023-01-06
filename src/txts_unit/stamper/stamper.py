from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from dataclasses import dataclass
import config


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

    def select_hz_client(self, flow):
        if flow not in self.flow_to_client:
            self.flow_to_client[flow] = config.HZ_CLIENTS[self.next_client]
            self.next_client = (self.next_client + 1) % config.HZ_CLIENT_CNT

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

        print(f'forwarding to ip {dst_hz_client} & port {config.HZ_CLIENT_LISTEN_PORT}')

        data = self.stamp_packet(data, src_addr)

        self.transport.write(data, (dst_hz_client, config.HZ_CLIENT_LISTEN_PORT))

reactor.listenUDP(config.STAMPER_LISTEN_PORT, Stamper())
print(f'Listening on port {config.STAMPER_LISTEN_PORT}...')

reactor.run()
