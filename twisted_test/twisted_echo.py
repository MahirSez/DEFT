from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
import os, sys

port = int(sys.argv[1])

class Echo(DatagramProtocol):
    
    def datagramReceived(self, data, addr):
        host, port = addr
        # print(type(host))
        # print(type(port))
        print(f'received {data} from ({host}, {port})')

        sending_host = '127.0.0.1'
        sending_port = 7000
        # if port != sending_port:
        data += b'key=100'
        self.transport.write(data, (sending_host, sending_port))
        # else:
        #     print('Fuck you Bishwa')

reactor.listenUDP(port, Echo())
reactor.run()