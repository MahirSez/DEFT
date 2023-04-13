from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from dataclasses import dataclass
import time
import socket

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
        self.pkt_cnt = 0
        self.pkt_cnt_since_last_reading = 0
        self.init_time = get_current_time_in_ms()

        #output rate veriables
        self.out_rate_reset = True
        self.output_rates = []
        self.out_time_start = 0
        self.out_pkt_counter = 0
        # self.packet_rate = 0

    def stamp_packet(self, data):
        # data = bytes.fromhex(data).decode('utf-8')
        # print(f'data in stamp_packet method {data}')
        stamp = f'\n{get_current_time_in_ms()}'
        data += bytes(stamp, 'ascii')

        return data
    
    def should_take_rate_reading(self):
        current_time = get_current_time_in_ms()
        return current_time - self.init_time >= 1000
    
    def should_calculate_out_rate(self):
        return self.out_pkt_counter >= 200

    def datagramReceived(self, data, src_addr):
        src_ip, src_port = src_addr
        self.pkt_cnt += 1
        self.pkt_cnt_since_last_reading += 1
        self.out_pkt_counter += 1
        if self.out_rate_reset:
            self.out_time_start = get_current_time_in_ms()
            self.out_rate_reset = False

        if self.should_take_rate_reading():
            current_time = get_current_time_in_ms()
            delay = (current_time - self.init_time) / 1000.0
            rate = self.pkt_cnt_since_last_reading / delay

            self.init_time = current_time
            self.pkt_cnt_since_last_reading = 0

            print(f"Current packet rate is: {rate} | processed packets = {self.pkt_cnt}" )

        # print(f'received {data} from ({src_ip}, {src_port}) | pkt_cnt = {self.pkt_cnt}')
        data = self.stamp_packet(data)
        # print(f'timestamped pkt: {data}')
        
        
        nginx_ip = socket.gethostbyname('nginx')
        # print(f'forwarding to {nginx_ip} & port 8080')
        self.transport.write(data, (nginx_ip, 8080))

        if self.should_calculate_out_rate():
            delay = (get_current_time_in_ms() - self.out_time_start) / 1000.0
            out_rate = self.out_pkt_counter / delay
            self.output_rates.append(out_rate)

            self.out_pkt_counter = 0
            self.out_rate_reset = True


reactor.listenUDP(TIME_STAMPER_LISTEN_PORT, TimeStamper())
print(f'Listening on port {TIME_STAMPER_LISTEN_PORT}...')

reactor.run()
