import hazelcast
import threading
import queue
from queue import PriorityQueue

from twisted.internet import reactor
from twisted.internet.protocol import Factory, Protocol, DatagramProtocol

import sys
sys.path.append('../')
print(sys.version)

from exp_package import Flow, Hazelcast, Helpers, Sniffer
from exp_package.Two_phase_commit.primary_2pc import Primary

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
    BATCH_SIZE = 20
    PKTS_NEED_TO_PROCESS = 1000
    GLOBAL_UPDATE_FREQUENCY = 15
    BUFFER_LIMIT = 1 * BATCH_SIZE


class Statistics:
    processed_pkts = 0
    received_packets = 0
    total_packet_size = 0
    total_delay_time = 0
    total_three_pc_time = 0
    packet_dropped = 0


# (st_time, en_time) - processing time

class State:
    per_flow_cnt = {}


def receive_a_pkt(pkt):
    if Statistics.received_packets == 0:
        Timestamps.start_time = Helpers.get_current_time_in_ms()

    Statistics.received_packets += 1
    print(f'received pkts: {Statistics.received_packets}')
    # redis_client.incr("packet_count " + host_var)

    if Buffers.input_buffer.qsize() < Limit.BUFFER_LIMIT:
        Buffers.input_buffer.put((pkt, Statistics.received_packets))
        BufferTimeMaps.input_in[Statistics.received_packets] = Helpers.get_current_time_in_ms()
    else:
        Statistics.packet_dropped += 1


def process_a_packet(packet, packet_id):
    Statistics.processed_pkts += 1
    Statistics.total_packet_size += len(packet)
    print(f'Processed pkts: {Statistics.processed_pkts}')

    Statistics.total_delay_time += Helpers.get_current_time_in_ms() - BufferTimeMaps.input_in[packet_id]

    # flow_string = Flow.get_string_of_flow(Flow.get_flow_from_pkt(packet))
    # State.per_flow_cnt[flow_string] = State.per_flow_cnt.get(flow_string, 0) + 1

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

        if pkt_num_of_cur_batch % uniform_global_distance == 0 or pkt_num_of_cur_batch == Limit.BATCH_SIZE:
            global_state_update(10)

        if Statistics.processed_pkts + Statistics.packet_dropped == Limit.PKTS_NEED_TO_PROCESS:
            time_delta = Helpers.get_current_time_in_ms() - Timestamps.start_time
            process_time = time_delta / 1000.0 + Statistics.total_three_pc_time
            generate_statistics()
            break


def generate_statistics():
    time_delta = Helpers.get_current_time_in_ms() - Timestamps.start_time
    total_process_time = time_delta / 1000.0

    print(f'Total Time {total_process_time}')
    print(f'Throughput for batch-size {Limit.BATCH_SIZE} is {Statistics.total_packet_size / total_process_time} Byte/s')
    print(
        f'Latency for batch-size {Limit.BATCH_SIZE} is {Statistics.total_delay_time / Statistics.processed_pkts} ms/pkt')
    print(f'packets dropped {Statistics.packet_dropped}')


def empty_output_buffer():
    while not Buffers.output_buffer.empty():
        _, pkt_id = Buffers.output_buffer.get()
        # print(f'current pkt {pkt_id}')
        Statistics.total_delay_time += Helpers.get_current_time_in_ms() - BufferTimeMaps.output_in[pkt_id]


def local_state_update():
    # local state update
    # print("------------------------------------------------------------------------------------------------------")
    print(f'replicating on backup as per batch.\n cur_batch: {State.per_flow_cnt}')
    cur_time = Helpers.get_current_time_in_ms()
    global_state = per_flow_packet_counter.get("global")
    master.replicate(global_state)
    Statistics.total_three_pc_time += Helpers.get_current_time_in_ms() - cur_time


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


def main():
    global master
    addresses = ['http://localhost:9090']
    if master is None:
        master = Primary(addresses)

    global per_flow_packet_counter
    hazelcast_client = hazelcast.HazelcastClient()
    per_flow_packet_counter = Hazelcast.create_per_flow_packet_counter(hazelcast_client)

    # factory = Factory()
    # factory.protocol = Echo
    # reactor.listenTCP(8000, factory)
    # reactor.run()
    hazelcast_thread = threading. \
        Thread(target=process_packet_with_hazelcast)

    hazelcast_thread.start()

    reactor.listenUDP(8000, EchoUDP())
    print('Listening on port 8000')
    reactor.run()


if __name__ == '__main__':
    main()
