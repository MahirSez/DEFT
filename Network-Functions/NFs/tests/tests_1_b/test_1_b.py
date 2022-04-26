#!/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.node import RemoteController

from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel

from time import sleep


class SingleSwitchTopo(Topo):
    """Single switch connected to n hosts."""

    def build(self, n=2):
        switch = self.addSwitch('s1')
        for h in range(n):
            # Each host gets 50%/n of system CPU
            host = self.addHost('h%s' % (h + 1),
                                cpu=.5 / n)
            self.addLink(host, switch)


def get_last_background_prcoess_id(h):
    id = int(h.cmd('echo $!'))
    return id


def server(h, id):
    print("Opening Server")
    h.cmd("xterm -T hazle_server_{} -hold -e 'bash ../../../../hazelcast-4.2.2/bin/start.sh' &".format(id))
    return get_last_background_prcoess_id(h)


def host(net, id):
    h = net.get("h" + str(id))
    ip = h.IP(intf=("h" + str(id) + "-eth0"))

    print("Opening client node h" + str(id) + " ip :{}".format(ip))
    cmd = "xterm -hold -e 'source ../../venv/bin/activate; python perflow-packet-counter.py -i h{}-eth0 -f icmp --dip={}' &". \
        format(id, ip)

    print(cmd)
    h.cmd(cmd)
    return get_last_background_prcoess_id(h)


def backup(net, id):
    h = net.get("h" + str(id))
    ip = h.IP(intf=("h" + str(id) + "-eth0"))

    print("Opening replica node h" + str(id) + " ip :{}".format(ip))
    cmd = "xterm -hold -T replica -e 'source ../../venv/bin/activate; python slave_2pc.py' &". \
        format(id, ip)

    print(cmd)
    h.cmd(cmd)
    return get_last_background_prcoess_id(h)


def setUp(net):
    """
    h1, h2 -> hazlecast cluster
    h1 (primary), h2 (replica)
    h3 -------pings-------> h1 -------replicates----------> h2
    """
    background_process_list = []  # (host, pid) tuple


    ## opening hazlecast server
    h1 = net.get('h1')
    id = server(h1, "1")
    background_process_list.append((h1, id))

    h2 = net.get('h2')
    id = server(h2, "2")
    background_process_list.append((h2, id))

    sleep(10)

    ## 
    id = backup(net, "2")
    background_process_list.append((h2, id))


    for i in range(1,2):
        h = net.get("h" + str(i))
        id = host(net, i)
        background_process_list.append((h, id))
        sleep(5)

    return background_process_list


def runTest(net):
    h1, h3 = net.get('h1', 'h3')

    background_tasks = []

    print("Pinging started!")    

    NUMBER_OF_PKTS = 1009

    # 1500 bytes
    h3.cmd('ping -c {} -s 4096 -i 0.02 10.0.0.1 &'.format(NUMBER_OF_PKTS))
    background_tasks.append((h3, get_last_background_prcoess_id(h3)))

    while background_tasks:
        h, id = background_tasks.pop()
        h.cmd('wait', id)

    print("All pings ended")


def perfTest():
    """Create network and run simple performance test"""
    topo = SingleSwitchTopo(n=3)

    net = Mininet(topo=topo,
                  host=CPULimitedHost, link=TCLink,
                  controller=RemoteController)
    net.start()
    print("Dumping host connections")

    dumpNodeConnections(net.hosts)
    daemons = setUp(net)
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
    perfTest()
