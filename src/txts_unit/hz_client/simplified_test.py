import hazelcast
import threading
import queue
from queue import PriorityQueue
from twisted.internet import reactor
from twisted.internet.protocol import Factory, Protocol, DatagramProtocol
import sys
import os
from dotenv import load_dotenv
import subprocess
from subprocess import DEVNULL, STDOUT, check_call, PIPE


load_dotenv()


sys.path.append('..')
from exp_package import  Hazelcast, Helpers
from exp_package.Two_phase_commit.primary_2pc import Primary

import socket

per_flow_packet_counter = None
master: Primary = None


class Buffers:
    input_buffer = queue.Queue(maxsize=100000)  # (pkts, pkts_id) tuples
    output_buffer = queue.Queue(maxsize=100000)  # (pkts, pkts_id) tuples


class BufferTimeMaps:
    input_in = {}
    input_out = {}
    output_in = {}
    output_out = {}


class Timestamps:
    start_times, end_times = None, None


class Limit:
    BATCH_SIZE = int(os.getenv('BATCH_SIZE'))
    PKTS_NEED_TO_PROCESS = 1000
    GLOBAL_UPDATE_FREQUENCY = 1
    BUFFER_LIMIT = 1 * BATCH_SIZE


class Statistics:
    processed_pkts = 0
    received_packets = 0
    total_packet_size = 0
    total_delay_time = 0
    total_two_pc_time = 0
    packet_dropped = 0


# (st_time, en_time) - processing time

local_state = {
    "received_packet" : 0,
    "processed_packet" : 0
}

class State:
    per_flow_cnt = {}


def receive_a_pkt(pkt):
    if Statistics.received_packets == 0:
        Timestamps.start_time = Helpers.get_current_time_in_ms()

    Statistics.received_packets += 1
    local_state['received_packet'] += 1
    # print(f'received pkts: {Statistics.received_packets}')
    # redis_client.incr("packet_count " + host_var)

    if Buffers.input_buffer.qsize() < Limit.BUFFER_LIMIT:
        Buffers.input_buffer.put((pkt, Statistics.received_packets))
        BufferTimeMaps.input_in[Statistics.received_packets] = Helpers.get_current_time_in_ms()
    else:
        Statistics.packet_dropped += 1


def process_a_packet(packet, packet_id):
    Statistics.processed_pkts += 1
    Statistics.total_packet_size += len(packet)
    print(f'Length of packet is {len(packet)}')
    print(f'Processed pkts: {Statistics.processed_pkts}')
    local_state['processed_packet'] += 1

    Statistics.total_delay_time += Helpers.get_current_time_in_ms() - BufferTimeMaps.input_in[packet_id]

    Buffers.output_buffer.put((packet, packet_id))
    BufferTimeMaps.output_in[packet_id] = Helpers.get_current_time_in_ms()


def can_update_local_state():

    if len(master.slaves) > 0:
        return True
    
    secondary_ip = create_secondary()
    if not secondary_ip:
        return False

    print(f"New Slave added {secondary_ip}")
    master.add_secondary(secondary_ip)
    return True

def process_packet_with_hazelcast():
    pkt_num_of_cur_batch = 0
    uniform_global_distance = Limit.BATCH_SIZE // Limit.GLOBAL_UPDATE_FREQUENCY

    while True:
        pkt, pkt_id = Buffers.input_buffer.get()

        process_a_packet(pkt, pkt_id)

        pkt_num_of_cur_batch += 1

        if Buffers.output_buffer.qsize() == Limit.BATCH_SIZE:
            pkt_num_of_cur_batch = 0
            empty_output_buffer()

            if can_update_local_state():
                local_state_update()

        if pkt_num_of_cur_batch % uniform_global_distance == 0 or pkt_num_of_cur_batch == Limit.BATCH_SIZE:
            global_state_update(10)

        if Statistics.processed_pkts + Statistics.packet_dropped == Limit.PKTS_NEED_TO_PROCESS:
            time_delta = Helpers.get_current_time_in_ms() - Timestamps.start_time
            process_time = time_delta / 1000.0 + Statistics.total_two_pc_time

            generate_statistics()
            break


def generate_statistics():
    time_delta = Helpers.get_current_time_in_ms() - Timestamps.start_time
    total_process_time = time_delta / 1000.0
    throughput = Statistics.total_packet_size / total_process_time
    latency = Statistics.total_delay_time / Statistics.processed_pkts


    batch_size = int(os.getenv('BATCH_SIZE'))
    buffer_size = int(os.getenv('BUFFER_SIZE'))
    packet_rate = int(os.getenv('PACKET_RATE'))
    
    filename = f'results/batch_{batch_size}-buf_{buffer_size}-pktrate_{packet_rate}.csv'

    with open(filename, 'a') as f:
        # f.write('Latency(ms), Throughput(byte/s), Packets Dropped\n')
        f.write(f'{latency},{throughput},{Statistics.packet_dropped}\n')


def empty_output_buffer():
    while not Buffers.output_buffer.empty():
        _, pkt_id = Buffers.output_buffer.get()
        # print(f'current pkt {pkt_id}')
        Statistics.total_delay_time += Helpers.get_current_time_in_ms() - BufferTimeMaps.output_in[pkt_id]


def local_state_update():
    global local_state
    print(f'replicating on backup as per batch.\n cur_batch: {State.per_flow_cnt}')
    cur_time = Helpers.get_current_time_in_ms()
    master.replicate(local_state)
    Statistics.total_two_pc_time += Helpers.get_current_time_in_ms() - cur_time


def global_state_update(batches_processed: int):
    # global state update
    print(f'Global state update')
    map_key = "global"
    per_flow_packet_counter.lock(map_key)
    value = per_flow_packet_counter.get(map_key)
    per_flow_packet_counter.set(map_key, batches_processed if value is None else value + batches_processed)
    per_flow_packet_counter.unlock(map_key)
    print(per_flow_packet_counter.get(map_key))


class EchoUDP(DatagramProtocol):
    def datagramReceived(self, datagram, address):
        # print(str(datagram))  
        # print(str(address))   
        # self.transport.write(datagram, address)   
        receive_a_pkt(datagram)
        # global_state_update(address)


CLUSTER_NAME = "deft-cluster"
LISTENING_PORT = 8000




def get_ip_address(iface):

    # f = os.popen(f'ifconfig {iface} | grep "inet\ addr" | cut -d: -f2 | cut -d" " -f1')
    # f = os.popen(f'ifconfig {iface} | grep "inet"')
    process = subprocess.Popen(f'ifconfig {iface} | grep "inet"', shell=True, stderr=PIPE, stdout=PIPE)
    stdout, stderr = process.communicate()
    line = stdout.decode()
    if not line:
        return None
    your_ip = line.strip().split()[1]
    return your_ip


# def get_ip_address(iface):
#     # f = os.popen(f'ifconfig {iface} | grep "inet\ addr" | cut -d: -f2 | cut -d" " -f1')
#     f = os.popen(f'ifconfig {iface} | grep "inet"')
#     line = f.read()
#     your_ip = line.strip().split()[1]
#     return your_ip

def create_secondary():
    # hostname=socket.gethostname()   
    # ip = n1.ifaddresses('eth1')[n1.AF_INET][0]['addr']

    interface = "eth1"
    ip = get_ip_address(interface)
    if not ip:
        return None

    print(f"IP-address of interface {interface} is {ip}")
    
    ip_segments = ip.split('.')
    ip_segments[-1] = str(int(ip_segments[-1]) + 100)

    secondary_address = 'http://' + '.'.join(ip_segments) + ":7000"

    return secondary_address

def main():
    global master
    # addresses = []

    # addresses.append(create_secondary())
    # print(addresses)

    if master is None:
        master = Primary()

    global per_flow_packet_counter

    batch_size = int(os.getenv('BATCH_SIZE'))
    buffer_size = int(os.getenv('BUFFER_SIZE'))
    packet_rate = int(os.getenv('PACKET_RATE'))
    
    filename = f'results/batch_{batch_size}-buf_{buffer_size}-pktrate_{packet_rate}.csv'

    print(f'will open file {filename}')

    print(f"Trying to connect to cluster {CLUSTER_NAME}....")

    hazelcast_client = hazelcast.HazelcastClient(cluster_members=["hazelcast:5701"],
                                                 cluster_name=CLUSTER_NAME)
    # hazelcast_client = hazelcast.HazelcastClient(cluster_members=["172.17.0.2:5701"],
    #                                             cluster_name=CLUSTER_NAME)
    print("Connected!")

    per_flow_packet_counter = Hazelcast.create_per_flow_packet_counter(hazelcast_client)

    hazelcast_thread = threading.Thread(target=process_packet_with_hazelcast)
    hazelcast_thread.start()

    print(f"Listening for packets on port {LISTENING_PORT}")
    reactor.listenUDP(LISTENING_PORT, EchoUDP())
    reactor.run()


if __name__ == '__main__':
    main()
