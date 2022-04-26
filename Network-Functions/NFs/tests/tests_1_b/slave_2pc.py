from xmlrpc.server import SimpleXMLRPCServer
import json


def update_state(state):
    with open('data/slave_state.json', 'w') as f:
        json.dump(state, f)
    
    print('Received state from master: ')
    print(state)
    return True


def backup():
    server = SimpleXMLRPCServer(("10.0.0.2", 8000))
    print("Listening on port 8000...")
    server.register_multicall_functions()
    server.register_function(update_state, 'update_state')
    server.serve_forever()


if __name__ == '__main__':
    backup()