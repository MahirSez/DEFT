import logging
import queue
import threading
from typing import List
import typer
# import redis

import sys
sys.path.append('../')
from exp_package import Flow, Hazelcast, Helpers, Sniffer
from exp_package.Two_phase_commit.primary_2pc import Primary 



# REDIS_SERVER_ADDR = '192.168.1.1'
# host_var = None
# redis_client = None

per_flow_packet_counter = None
master = None

class Buffers():
    input_buffer = queue.Queue(maxsize=100000)          # (pkts, pkts_id) tuples
    output_buffer = queue.Queue(maxsize=100000)         # (pkts, pkts_id) tuples

class BufferTimeMaps():
    input_in = {}
    input_out = {}
    output_in = {}
    output_out = {}


class Timestamps():
    start_times, end_times = None, None 


class Limit():
    BATCH_SIZE = 10
    PKTS_NEED_TO_PROCESS = 1000
    GLOBAL_UPDATE_FREQUENCY = 10


class Statistics():
    processed_pkts = 0
    received_packets = 0
    total_packet_size = 0
    total_delay_time = 0
    total_three_pc_time = 0
    batches_processed = 0

# (st_time, en_time) - processing time
# additional 3pc time 

# input_buffer
# output_buffer

class State():
    per_flow_cnt = {}


def receive_a_pkt(pkt):

    if Statistics.received_packets == 0:
        Timestamps.start_time = Helpers.get_current_time_in_ms()

    Statistics.received_packets += 1
    # redis_client.incr("packet_count " + host_var)
    
    Buffers.input_buffer.put((pkt, Statistics.received_packets))
    BufferTimeMaps.input_in[Statistics.received_packets] = Helpers.get_current_time_in_ms()


def process_a_packet(packet, packet_id):
    Statistics.processed_pkts += 1
    Statistics.total_delay_time += Helpers.get_current_time_in_ms() - BufferTimeMaps.input_in[packet_id]

    Statistics.total_packet_size += len(packet)

    flow_string = Flow.get_string_of_flow(Flow.get_flow_from_pkt(packet))
    State.per_flow_cnt[flow_string] = State.per_flow_cnt.get(flow_string, 0)  + 1
    
    Buffers.output_buffer.put((packet, packet_id))
    BufferTimeMaps.output_in[packet_id] = Helpers.get_current_time_in_ms()

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
            local_state_update()

        if pkt_num_of_cur_batch  % uniform_global_distance == 0 or pkt_num_of_cur_batch == Limit.BATCH_SIZE: 
            global_state_update(10)

        if Statistics.processed_pkts == Limit.PKTS_NEED_TO_PROCESS:
            # process is completed
            # generate the statistics now
            generate_statistics()
            break


def generate_statistics():
    time_delta = Helpers.get_current_time_in_ms() - Timestamps.start_time
    process_time = time_delta / 1000.0

    print(f'Throughput for batch-size {Limit.BATCH_SIZE} is {Statistics.total_packet_size/ process_time} Byte/s')


def empty_output_buffer():

    while not Buffers.output_buffer.empty():
        _, pkt_id = Buffers.output_buffer.get()
        Statistics.total_delay_time += Helpers.get_current_time_in_ms() - BufferTimeMaps.output_in[pkt_id]

def local_state_update():
    print("------------------------------------------------------------------------------------------------------")
    print(f'replicating on backup as per batch.\n cur_batch: {State.per_flow_cnt}')
    cur_time = Helpers.get_current_time_in_ms()
    master.replicate(State.per_flow_cnt)
    Statistics.total_three_pc_time += Helpers.get_current_time_in_ms() - cur_time

def global_state_update(batches_processed: int):
    map_key = "global"
    per_flow_packet_counter.lock(map_key)
    value = per_flow_packet_counter.get(map_key)
    per_flow_packet_counter.set(map_key, batches_processed if value is None else value + batches_processed)
    per_flow_packet_counter.unlock(map_key)

# def set_host_var():
#     global host_var
#     s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     s.connect(("8.8.8.8", 80))
#     host_var = s.getsockname()[0]
#     s.close()


def main(
        interface: str = typer.Option(..., '--iface', '-i', help='Interface to run the sniffer on'),
        filter: str = typer.Option('icmp', '--filter', '-f', help='Filter on interface sniffing'),
        ip: str = typer.Option('', '--dip', help='destination Ip'),
        backup_addresses: List[str] = typer.Option(..., '--backup', '-b', help='ip:port for backups of primary nf, multiple allowed') 

):
    global redis_client, per_flow_packet_counter, master
    logging.basicConfig(level=logging.INFO)

    addresses = ['http://' + address for address in backup_addresses]

    if master is None:
        master = Primary(addresses)

    if ip != '':  # ip provided
        filter += ' and dst {}'.format(ip)

    # logging.info("Using Filter " + filter + " on interface " + interface)
    # logging.info("Connecting to Redis Server")
    # redis_client = redis.Redis(host=REDIS_SERVER_ADDR, port=6379, db=0)
    # set_host_var()
    # redis_client.set("packet_count " + host_var, 0)

    hazelcast_client = Hazelcast.load_hazelcast([
            "10.0.0.1:5701",
            "10.0.0.2:5701"
            # "192.168.1.1:5701"
        ])

    per_flow_packet_counter = Hazelcast.create_per_flow_packet_counter(hazelcast_client)

    print(f'batch {Limit.BATCH_SIZE} , pkts_needed: {Limit.PKTS_NEED_TO_PROCESS}')

    hazelcast_thread = threading. \
        Thread(target=process_packet_with_hazelcast)

    hazelcast_thread.start()

    Sniffer.sniffer({
        'filter': filter,
        'iface': interface,
        'prn': receive_a_pkt
    })

    hazelcast_thread.join()


if __name__ == '__main__':
    typer.run(main)
