from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from dataclasses import dataclass
import time

import os
from dotenv import load_dotenv
import redis

load_dotenv()

HZ_CLIENT_IP_PATTERN = os.getenv('HZ_CLIENT_IP_PATTERN')
STAMPER_LISTEN_PORT = int(os.getenv('STAMPER_LISTEN_PORT'))
STAMPER_IP_LAST_OCTET = int(os.getenv('STAMPER_IP_LAST_OCTET'))
TIME_STAMPER_LISTEN_PORT = int(os.getenv('TIME_STAMPER_LISTEN_PORT'))

STAMPER_IP = HZ_CLIENT_IP_PATTERN.replace('$', str(STAMPER_IP_LAST_OCTET))
print(f"Stamper IP: {STAMPER_IP}")


def get_current_time_in_ms():
    return time.time_ns() // 1_000_000


class TimeStamper(DatagramProtocol):
    def __init__(self):

        print('Configured hz_clint IP list:')
        print(self.hz_client_ips)

    def stamp_packet(self, data):
        # data = bytes.fromhex(data).decode('utf-8')
        print(f'data in stamp_packet method {data}')
        stamp = f'\n{get_current_time_in_ms()}'
        data += bytes(stamp, 'ascii')

        return data

    def datagramReceived(self, data, src_addr):
        src_ip, src_port = src_addr
        print(f'received {data} from ({src_ip}, {src_port})')
        data = self.stamp_packet(data)
        print(f'timestamped pkt: {data}')
        print(f'forwarding to ip {STAMPER_IP} & port {STAMPER_LISTEN_PORT}')
        self.transport.write(data, (STAMPER_IP, STAMPER_LISTEN_PORT))


reactor.listenUDP(TIME_STAMPER_LISTEN_PORT, TimeStamper())
print(f'Listening on port {TIME_STAMPER_LISTEN_PORT}...')

reactor.run()
