from mimetypes import init
from xmlrpc.server import SimpleXMLRPCServer
from dataclasses import dataclass, field
import json


@dataclass
class Backup:
    ip: str
    port: int
    server: SimpleXMLRPCServer = field(init=False)

    def __post_init__(self):
        self.server = SimpleXMLRPCServer((self.ip, self.port), logRequests=False)

    @staticmethod
    def update_state(state):
        with open('../data/slave_state.json', 'w') as f:
            json.dump(state, f)
        
        # print('Received state from master: ')
        # print(state)
        return True


    def listen(self):
        print(f"Listening on ip={self.ip} port={self.port}")
        self.server.register_multicall_functions()
        self.server.register_function(Backup.update_state, 'update_state')
        self.server.serve_forever()
