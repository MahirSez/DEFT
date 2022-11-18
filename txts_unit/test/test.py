#!/usr/bin/env python3

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.node import RemoteController
from mininet.cli import CLI

from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel

from time import sleep




import sys
sys.path.append('../')

print(sys.version)

from exp_package import Flow, Hazelcast, Helpers, Sniffer
from exp_package.Two_phase_commit.primary_2pc import Primary 

import config

n_h = 1

class MultiSwitchTopo(Topo):

    def build(self, n=2):

        mac = "00:00:00:00:00:0"
        cnt = 1

        bw = 0.15

        switch1 = self.addSwitch('s1')
        switch2 = self.addSwitch('s2')
        for h in range(n):
            host = self.addHost('h%s' % (h + 1), mac = mac + str(h+2))
            self.addLink(host, switch2, cls=TCLink, bw=bw)
            # self.addLink(host, switch2)

        client = self.addHost('client', mac= mac + str(1))
        stamper = self.addHost('stamper', mac= mac + str(9))

        self.addLink(switch1, stamper)
        self.addLink(stamper, switch2, cls=TCLink, bw=bw)
        # self.addLink(stamper, switch2)
        self.addLink(switch1, client)
        self.addLink(switch1, switch2)



def get_last_background_prcoess_id(h):
    id = int(h.cmd('echo $!'))
    return id


def create_server(h, server_name):
    print("Opening Server at {}".format(server_name))

    h.cmd('bash ../../hazelcast-4.2.2/bin/start.sh &')

    # h.cmd("xterm -hold -T {} -e 'bash ../../hazelcast-4.2.2/bin/start.sh &'". \
    # format(server_name))

    return get_last_background_prcoess_id(h)


def create_primary(net, primary_name, backup_name):

    p_h = net.get(primary_name)
    p_ip = config.HOST_IP[primary_name]
    b_ip = config.HOST_IP[backup_name]


    print("Opening primary at {} with backup at {}".format(primary_name, backup_name))

    cmd = "xterm -hold -e 'source ../venv/bin/activate; python perflow-packet-counter.py " + \
        "-i {}-eth0 -f icmp --dip={} -b {}:8000' &". \
        format(primary_name, p_ip, b_ip)

    print(cmd)
    p_h.cmd(cmd)
    return get_last_background_prcoess_id(p_h)


def create_backup(net, backup_name, port=8000):
    h = net.get(backup_name)
    ip = config.HOST_IP[backup_name]

    print("Opening backup node" + backup_name + " ip :{}".format(ip))
    cmd = 'xterm -hold -T replica-{} -e "source ../venv/bin/activate; python backup.py -i {} -p {}" &'. \
        format(backup_name, ip, port)


    print(cmd)
    h.cmd(cmd)
    return get_last_background_prcoess_id(h)


def create_hazelcast_servers(net):
    background_process_list = []  # (host, pid) tuple

    ## opening hazlecast server
    ## TODO: Make sure to create a list from here

    servers = set()

    for primary in config.PRIMARIES[:n_h]:
        servers.add(primary)
        servers.add(config.PRIMARY_TO_SECONDARY[primary])
    
    print(f'Hazle Servers are {servers}')
    

    for server_name in servers:
        h = net.get(server_name)
        id = create_server(h, server_name)
        background_process_list.append((h, id))

    return background_process_list

def setUp(net):

    background_process_list = []  # (host, pid) tuple

    stamper = net.get('stamper')
    cmd = "xterm -hold -T stamper -e 'source ../venv/bin/activate; python ../stamperScript.py' &"
    stamper.cmd(cmd)
    background_process_list.append((stamper, get_last_background_prcoess_id(stamper)))
    sleep(5)

    print('Stamper is Up!')

    background_process_list.extend(create_hazelcast_servers(net))
    sleep(25)
    print('All hazlecast servers are up!')


    for primary in config.PRIMARIES[:n_h]:

        secondary = config.PRIMARY_TO_SECONDARY[primary]

        p_h = net.get(primary)
        b_h = net.get(secondary)

        process_id = create_backup(net, secondary)
        background_process_list.append((b_h, process_id))

        process_id = create_primary(net, primary, secondary)
        background_process_list.append((p_h, process_id))


    # for p_id in range(1, n_h+1):
    #     p_h = net.get("h" + str(p_id))
    #     b_id = p_id + 1 if p_id + 1 <= n_h else 1  # offset one is replica
    #     b_h = net.get("h" + str(b_id))

    #     process_id = create_backup(net, b_id)
    #     background_process_list.append((b_h, process_id))

    #     process_id = create_primary(net, p_id, b_id)
    #     background_process_list.append((p_h, process_id))

    sleep(20)
    print('Primary and backup created!')

    return background_process_list


def runTest(net):

    client = net.get('client')

    background_tasks = []

    # print("Pinging started!")    

    NUMBER_OF_PKTS = 1009

    # 1500 bytes
    # for i in range(3, 2 + 2*n_h+1, 2):
    #     source_host = h1 if (i//2) % 2 == 0 else h2
    #     s_h_id = 1 if (i//2) % 2 == 0 else 2
    #     target_ip = "10.0.0.{}".format(i)
    #     print('from {}:ping -c {} -s 4096 -i 0.02 {} &'.format(s_h_id,NUMBER_OF_PKTS, target_ip))
    #     source_host.cmd('ping -c {} -s 4096 -i 0.02 {} &'.format(NUMBER_OF_PKTS, target_ip))
    #     background_tasks.append((source_host, get_last_background_prcoess_id(source_host)))

    for target in config.PRIMARIES[:n_h]:
        target_ip = config.HOST_IP[target]

        print('from {}:ping -c {} -s 1400 -i 0.04 {} &'.\
            format(config.HOST_IP['client'],NUMBER_OF_PKTS, target_ip))

        client.cmd('ping -c {} -s 1400 -i 0.04 {} &'.format(NUMBER_OF_PKTS, target_ip))
        background_tasks.append((client, get_last_background_prcoess_id(client)))

    while background_tasks:
        h, id = background_tasks.pop()
        h.cmd('wait', id)

    print("All pings ended")


def perfTest():
    """Create network and run simple performance test"""
    topo = MultiSwitchTopo(n = 7) 

    net = Mininet(topo=topo,
                  host=CPULimitedHost, 
                  link=TCLink,
                  controller=RemoteController)

    net.start()
    print("Dumping host connections")

    dumpNodeConnections(net.hosts)


    daemons = setUp(net)

    # CLI( net )

    runTest(net)

    print("Enter 9 to kill all process")
    while True:
        inp = int(input())
        if inp == 9: break

    while daemons:
        h, id = daemons.pop()
        h.cmd('kill -9 {}'.format(id))

    print("all background process are killed!")

    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    # print(config.HOSTS)
    perfTest()
