import hazelcast
import threading
import queue
from twisted.internet import reactor
from twisted.internet.protocol import DatagramProtocol
import sys
import os
from dataclasses import dataclass, field
from dotenv import load_dotenv
import subprocess
from subprocess import PIPE
import redis
import time

load_dotenv()

sys.path.append('..')
from exp_package import  Hazelcast, Helpers
from exp_package.Two_phase_commit.primary_2pc import Primary

NF_DONE_KEY = "NF_DONE"
redis_client = redis.Redis(host='redis')


per_flow_packet_counter = None
master: Primary = None

@dataclass
class PerflowState:
    flow: str 
    input_buffer_entry_time: dict[tuple, int] = field(default_factory=dict)
    output_buffer_entry_time: dict[tuple, int] = field(default_factory=dict)
    pkt_total_delay: dict[tuple, int] = field(default_factory=dict)
    
    start_time: int = 0,
    end_time: int = 0
    recieved_pkt: int = 0
    processed_pkt: int = 0
    dropped_pkt: int = 0
    total_pkt_length: int = 0
    total_delay_time: int = 0


class Buffers:
    input_buffer = queue.Queue(maxsize=100000)  # (pkts, pkts_id) tuplesp
    output_buffer = queue.Queue(maxsize=100000)  # (pkts, pkts_id) tuples

class Limit:
    GLOBAL_UPDATE_IN_A_ROW = int(os.getenv('GLOBAL_UPDATE_IN_A_ROW'))
    BATCH_SIZE = int(os.getenv('BATCH_SIZE'))
    GLOBAL_UPDATE_ON_EVERY = 200
    BUFFER_LIMIT = 4 * BATCH_SIZE

class Statistics:
    processed_pkts = 0
    received_packets = 0
    total_packet_size = 0
    total_delay_time = 0
    total_two_pc_time = 0
    packet_dropped = 0
    flow_completed = 0

    nf_pkt_cnt = 0
    nf_pkt_cnt_since_last_reading = 0

class Buffer_Statistics:
    input_buffer_length = 0
    output_buffer_length = 0

class State:
    per_flow_cnt = {}


perflow_states: dict[str, PerflowState] = {}
header_added = False
global_update_cnt = 0
two_pc_cnt = 0
TIMELAPSE_DIFF_MS = 100
pkt_delays = []
local_state = {}
global_start_time = None

def get_stamps(pkt) -> tuple[str, int]:
    pkt_data = pkt.decode('latin-1').split("\n") 
    stamp_id = int(pkt_data[-1])
    flow = pkt_data[-2]
    start_time = int(pkt_data[-3])
    return flow, stamp_id, start_time

def get_state_from_flow(flow): 
    try:
        return perflow_states[flow]
    except KeyError:
        perflow_states[flow] = PerflowState(
            flow, 
            {}, 
            {}, 
            -1,
            0
        )
        return perflow_states[flow]

def receive_single_pkt(pkt):
    flow, stamp_id, stamped_time = get_stamps(pkt)
    states = get_state_from_flow(flow)

    if states.start_time == -1:
        states.start_time = stamped_time

    states.recieved_pkt += 1

    if Buffers.input_buffer.qsize() < Limit.BUFFER_LIMIT:
        states.input_buffer_entry_time[(stamp_id, flow)] = stamped_time
        Buffers.input_buffer.put((pkt, stamp_id, flow))
    else:
        states.dropped_pkt += 1


def process_single_pkt(pkt, pkt_id):  # packet_id == stamp_id
    flow, _, _ = get_stamps(pkt)
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

def update_pkt_cnt_for_printing():
    Statistics.nf_pkt_cnt += 1
    Statistics.nf_pkt_cnt_since_last_reading += 1
    if Statistics.nf_pkt_cnt_since_last_reading == 1000:
        print("Packets processed: ", Statistics.nf_pkt_cnt)
        Statistics.nf_pkt_cnt_since_last_reading = 0

def process_packet_with_hazelcast():
    global global_update_cnt, two_pc_cnt, global_start_time
    pkt_num_of_cur_batch = 0
    uniform_global_distance = Limit.BATCH_SIZE * Limit.GLOBAL_UPDATE_ON_EVERY

    start_time = Helpers.get_current_time_in_ms()
    global_start_time = start_time

    while True:
        pkt, pkt_id, _ = Buffers.input_buffer.get()
        process_single_pkt(pkt, pkt_id)
        pkt_num_of_cur_batch += 1

        if pkt_num_of_cur_batch % uniform_global_distance == 0:
            for i in range(Limit.GLOBAL_UPDATE_IN_A_ROW):
                global_update_cnt += 1
                global_state_update(2)

        if Buffers.output_buffer.qsize() == Limit.BATCH_SIZE:
            if can_update_local_state():
                local_state_update()
                two_pc_cnt += 1
            empty_output_buffer()


def stat_collector():
    start_time = Helpers.get_current_time_in_ms()
    print("Starting to collect stat")
    while True:
        time.sleep(TIMELAPSE_DIFF_MS/1000)
        current_time = Helpers.get_current_time_in_ms()
        generate_statistics(current_time - start_time)
        start_time = current_time

        if current_time - global_start_time >= 30*1000:
            redis_client.incr(NF_DONE_KEY)
            break
    print("Stat collection complete")

def generate_statistics(time_diff):
    packets_dropped = 0
    packets_processed = 0
    active_flow_cnt = 0
    total_delay_ms = 0
    total_pkt_len = 0

    total_process_time = time_diff / 1000.0

    for _, state in perflow_states.items(): 

        if state.processed_pkt == 0:
            continue

        active_flow_cnt += 1
        total_pkt_len += state.total_pkt_length 
        total_delay_ms += state.total_delay_time
        packets_dropped += state.dropped_pkt
        packets_processed += state.processed_pkt

        state.total_pkt_length = 0
        state.total_delay_time = 0
        state.processed_pkt = 0
        state.dropped_pkt = 0

    pps = packets_processed / total_process_time
    throughput = total_pkt_len / total_process_time

    if packets_processed:
        latency = total_delay_ms / packets_processed
        latency = f'{latency:.2f}'
    else:
        latency = '-'


    write_stats_to_file(latency, int(throughput), packets_dropped, packets_processed, pps, active_flow_cnt)

def write_stats_to_file(latency: str, thoughput: int, packetdrop, packets_processed, pps, active_flow_cnt):
    global header_added, global_update_cnt, two_pc_cnt, pkt_delays

    ip_addr = get_ip_address("eth1")

    if not ip_addr:
        return
    
    filename = f'results/timelapse-{ip_addr}.csv'
    with open(filename, 'a') as f:

        if not header_added:
            f.write(f'Time(s),Latency,Throughput,Packetdrop,Global Update,2PC,Packets Processed,PPS,Active Flow Cnt,Delay List\n')
            header_added = True

        pkt_delays_str = str(pkt_delays).replace(",", " - ")
        relative_time = (Helpers.get_current_time_in_ms() - global_start_time) / 1000

        f.write(f'{relative_time:.2f},{latency},{thoughput},{packetdrop},{global_update_cnt},{two_pc_cnt},{packets_processed},{pps},{active_flow_cnt},{pkt_delays_str}\n')
        
        pkt_delays = []
        global_update_cnt = 0
        two_pc_cnt = 0

def empty_output_buffer():
    while not Buffers.output_buffer.empty():
        _, pkt_id, flow = Buffers.output_buffer.get()
        states = get_state_from_flow(flow)
        delay = Helpers.get_current_time_in_ms() - states.output_buffer_entry_time[(pkt_id, flow)]
        states.total_delay_time += delay

        states.end_time = Helpers.get_current_time_in_ms()


def local_state_update():
    global local_state
    cur_time = Helpers.get_current_time_in_ms()
    master.replicate(local_state)
    Statistics.total_two_pc_time += Helpers.get_current_time_in_ms() - cur_time


def global_state_update(batches_processed: int):

    map_key = "global"
    per_flow_packet_counter.lock(map_key)
    value = per_flow_packet_counter.get(map_key)
    per_flow_packet_counter.set(map_key, batches_processed if value is None else value + batches_processed)
    per_flow_packet_counter.unlock(map_key)


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
    print("info: value of GLOBAL_UPDATE_IN_A_ROW ", Limit.GLOBAL_UPDATE_IN_A_ROW)

    print(f"Trying to connect to cluster {CLUSTER_NAME}....")

    hazelcast_client = hazelcast.HazelcastClient(cluster_members=["hazelcast:5701"],
                                                 cluster_name=CLUSTER_NAME)
    print("Connected!")
    per_flow_packet_counter = Hazelcast.create_per_flow_packet_counter(hazelcast_client)
    hazelcast_thread = threading.Thread(target=process_packet_with_hazelcast)
    hazelcast_thread.start()

    stat_collector_thread = threading.Thread(target=stat_collector)
    stat_collector_thread.start()

    print(f"Listening for packets on port {LISTENING_PORT}")
    reactor.listenUDP(LISTENING_PORT, EchoUDP())
    reactor.run()


if __name__ == '__main__':
    main()
