import hazelcast
import threading
import queue
from twisted.internet import reactor
from twisted.internet.protocol import DatagramProtocol
import sys
import os
from dataclasses import dataclass
from dotenv import load_dotenv
import subprocess
from subprocess import PIPE

load_dotenv()

sys.path.append('..')
from exp_package import  Hazelcast, Helpers
from exp_package.Two_phase_commit.primary_2pc import Primary


per_flow_packet_counter = None
master: Primary = None

@dataclass
class PerflowState:
    flow: str 
    input_buffer_entry_time: dict[tuple, int]
    output_buffer_entry_time: dict[tuple, int]
    start_time: int
    end_time: int
    recieved_pkt: int = 0
    processed_pkt: int = 0
    dropped_pkt: int = 0
    total_pkt_length: int = 0
    total_delay_time: int = 0


class Buffers:
    input_buffer = queue.Queue(maxsize=100000)  # (pkts, pkts_id) tuplesp
    output_buffer = queue.Queue(maxsize=100000)  # (pkts, pkts_id) tuples

class Limit:
    BATCH_SIZE = int(os.getenv('BATCH_SIZE'))
    PKTS_NEED_TO_PROCESS = 1000 # TODO: get it in Config
    GLOBAL_UPDATE_FREQUENCY = 1
    BUFFER_LIMIT = int(os.getenv('BUFFER_SIZE')) * BATCH_SIZE
    # BUFFER_LIMIT = 100000
    FLOW_CNT_PER_NF = int(os.getenv('FLOW_CNT_PER_NF'))

class Statistics:
    processed_pkts = 0
    received_packets = 0
    total_packet_size = 0
    total_delay_time = 0
    total_two_pc_time = 0
    packet_dropped = 0
    flow_completed = 0

class State:
    per_flow_cnt = {}


perflow_states: dict[str, PerflowState] = {}
local_state = {}

def get_stamps(pkt) -> tuple[str, int]:
    pkt_data = pkt.decode('latin-1').split("\n") 
    stamp_id = int(pkt_data[-1])
    flow = pkt_data[-2]
    return flow, stamp_id

def get_state_from_flow(flow): 
    try:
        return perflow_states[flow]
    except KeyError:
        perflow_states[flow] = PerflowState(
            flow, 
            {}, 
            {}, 
            Helpers.get_current_time_in_ms(), 
            0
        )
        return perflow_states[flow]

def receive_single_pkt(pkt):
    flow, stamp_id = get_stamps(pkt)
    states = get_state_from_flow(flow)
    states.recieved_pkt += 1

    if Buffers.input_buffer.qsize() < Limit.BUFFER_LIMIT:
        Buffers.input_buffer.put((pkt, stamp_id, flow))
        states.input_buffer_entry_time[(stamp_id, flow)] = Helpers.get_current_time_in_ms()
    else:
        states.dropped_pkt += 1


def process_single_pkt(pkt, pkt_id):  # packet_id == stamp_id
    flow, _ = get_stamps(pkt)
    states = get_state_from_flow(flow)

    states.processed_pkt += 1
    states.total_pkt_length += len(pkt)

    delay = Helpers.get_current_time_in_ms() - states.input_buffer_entry_time[(pkt_id, flow)]
    states.total_delay_time += delay
    Buffers.output_buffer.put((pkt, pkt_id, flow))
    states.output_buffer_entry_time[(pkt_id, flow)] = Helpers.get_current_time_in_ms()


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
        pkt, pkt_id, flow = Buffers.input_buffer.get()
        process_single_pkt(pkt, pkt_id)
        flow, _ = get_stamps(pkt)
        states = get_state_from_flow(flow)
        pkt_num_of_cur_batch += 1

        if Buffers.output_buffer.qsize() == Limit.BATCH_SIZE:
            pkt_num_of_cur_batch = 0
            empty_output_buffer()
            if can_update_local_state():
                local_state_update()

        if pkt_num_of_cur_batch % uniform_global_distance == 0 or pkt_num_of_cur_batch == Limit.BATCH_SIZE:
            # for i in range(10):
            global_state_update(10)

        if is_flow_completed(states):
            Statistics.flow_completed += 1
            states.end_time = Helpers.get_current_time_in_ms()
            print(Statistics.flow_completed)
            print(Limit.FLOW_CNT_PER_NF)
        

        if Statistics.flow_completed == Limit.FLOW_CNT_PER_NF:
            generate_statistics()

def is_flow_completed(states: PerflowState):
    # print(f'Processed pkt = {states.processed_pkt}')
    # print(f'Dropped pkt = {states.dropped_pkt}')
    return states.processed_pkt + states.dropped_pkt >= Limit.PKTS_NEED_TO_PROCESS

def generate_statistics():
    batch_size = int(os.getenv('BATCH_SIZE'))
    buffer_size = int(os.getenv('BUFFER_SIZE'))
    packet_rate = int(os.getenv('PACKET_RATE'))
    stamper_count = int(os.getenv('STAMPER_CNT'))
    flow_count = int(os.getenv('FLOW_CNT_PER_NF'))
    trial=int(os.getenv('TRIAL'))
    
    filename = f'results/batch_{batch_size}-buf_{buffer_size}-pktrate_{packet_rate}-flow_cnt_{flow_count}-stamper_cnt_{stamper_count}.csv'
    print(f"Writing stats to {filename}")

    for flow, state in perflow_states.items(): 
        # latency()
        time_delta = state.end_time - state.start_time
        total_process_time = time_delta / 1000.0
        throughput_bps = state.total_pkt_length / total_process_time
        latency = state.total_delay_time / state.processed_pkt
        throughput_pps = state.processed_pkt / total_process_time

        flow_string = flow.replace('(', "") \
                          .replace(")", "") \
                          .replace(",", ":")
                          
        with open(filename, 'a') as f:
            f.write(f'{flow_string},{latency},{throughput_bps}, {throughput_pps}, {state.dropped_pkt}\n')


def empty_output_buffer():
    while not Buffers.output_buffer.empty():
        _, pkt_id, flow = Buffers.output_buffer.get()
        states = get_state_from_flow(flow)
        delay = Helpers.get_current_time_in_ms() - states.output_buffer_entry_time[(pkt_id, flow)]
        states.total_delay_time += delay


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
        receive_single_pkt(datagram)


CLUSTER_NAME = "deft-cluster"
LISTENING_PORT = 8000


def get_ip_address(iface):
    process = subprocess.Popen(f'ifconfig {iface} | grep "inet"', shell=True, stderr=PIPE, stdout=PIPE)
    stdout, stderr = process.communicate()
    line = stdout.decode()
    if not line:
        return None
    your_ip = line.strip().split()[1]
    return your_ip


def create_secondary():
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
    if master is None:
        master = Primary()

    global per_flow_packet_counter

    batch_size = int(os.getenv('BATCH_SIZE'))
    buffer_size = int(os.getenv('BUFFER_SIZE'))
    packet_rate = int(os.getenv('PACKET_RATE'))
    stamper_count = int(os.getenv('STAMPER_CNT'))
    flow_count = int(os.getenv('FLOW_CNT_PER_NF'))
    trial=int(os.getenv('TRIAL'))
    
    filename = f'results/batch_{batch_size}-buf_{buffer_size}-pktrate_{packet_rate}-flow_cnt_{flow_count}-stamper_cnt_{stamper_count}.csv'
    print(f'will open file {filename}')
    print(f"Trying to connect to cluster {CLUSTER_NAME}....")

    hazelcast_client = hazelcast.HazelcastClient(cluster_members=["hazelcast:5701"],
                                                 cluster_name=CLUSTER_NAME)
    print("Connected!")
    per_flow_packet_counter = Hazelcast.create_per_flow_packet_counter(hazelcast_client)
    hazelcast_thread = threading.Thread(target=process_packet_with_hazelcast)
    hazelcast_thread.start()

    print(f"Listening for packets on port {LISTENING_PORT}")
    reactor.listenUDP(LISTENING_PORT, EchoUDP())
    reactor.run()


if __name__ == '__main__':
    main()
