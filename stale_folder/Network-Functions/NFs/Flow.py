from hazelcast.serialization.api import IdentifiedDataSerializable


class Flow(IdentifiedDataSerializable):
    def __init__(self,
                 src_ip=None,
                 dst_ip=None,
                 src_port=None,
                 dst_port=None
                 # proto=None  # scapy provides protocol as number
                 ):
        self.src_ip = src_ip
        self.dst_ip = dst_ip
        self.src_port = src_port
        self.dst_port = dst_port
        # self.proto = proto

    def __hash__(self) -> int:
        return hash((self.src_ip, self.dst_ip,
                     self.src_port, self.dst_port
                     # self.proto
                     ))

    def __eq__(self, o: object) -> bool:
        return (self.src_ip, self.dst_ip,
                self.src_port, self.dst_port,
                # self.proto
                ) == (
                   o.src_ip, o.dst_ip,
                   o.src_port, o.dst_port,
                   # o.proto
               )

    def __repr__(self) -> str:
        return "sip-{},dip-{},sprt-{},dprt-{}".format(
            self.src_ip, self.dst_ip, self.src_port, self.dst_port
            # self.proto
        )

    def get_class_id(self):
        return 1

    def get_factory_id(self):
        return 1

    def write_data(self, output):
        output.write_string(self.src_ip)
        output.write_string(self.dst_ip)
        output.write_string(self.src_port)
        output.write_string(self.dst_port)
        # output.write_int(self.proto)

    def read_data(self, input):
        self.src_ip = input.read_string()
        self.dst_ip = input.read_string()
        self.src_port = input.read_string()
        self.dst_port = input.read_string()
        # self.proto = input.read_int()
