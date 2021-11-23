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


def server(h):
    print("Opening Server on host 1")
    h.cmd("xterm -hold -e 'bash ../../hazelcast-4.2.2/bin/start.sh' &")
    return get_last_background_prcoess_id(h)


def host(net, id):
    h = net.get("h" + str(id))
    ip = h.IP(intf=("h" + str(id) + "-eth0"))
    print("Opening client node h" + str(id) + " ip :{}".format(ip))
    cmd = "xterm -hold -e 'source venv/bin/activate; python perflow-packet-counter.py -i h{}-eth0 -f icmp --dip={}' &". \
        format(id, ip)
    print(cmd)
    h.cmd(cmd)
    return get_last_background_prcoess_id(h)


def setUp(net):
    background_process_list = []  # (host, pid) tuple

    h1 = net.get('h1')
    id = server(h1)
    background_process_list.append((h1, id))
    sleep(10)

    for i in range(2, 5):
        h = net.get("h" + str(i))
        id = host(net, i)
        background_process_list.append((h, id))
        sleep(5)

    return background_process_list


def runTest(net):
    h2, h3, h4 = net.get('h2', 'h3', 'h4')

#   cyclic ping: h2-> h3 -> h4 -> h2; exp output: all count 200
    # h2.cmd('ping -c 100 -i 0.02 10.0.0.3 &')
    # h3.cmd('ping -c 100 -i 0.02 10.0.0.4 &')
    # h4.cmd('ping -c 100 -i 0.02 10.0.0.2 &')

#   ping test: h2-> h3 -> h4 -> h3; exp output: h2:100, h3:300, h4:200
    background_tasks = []
    h2.cmd('ping -c 100 -i 0.02 10.0.0.3 &')
    background_tasks.append((h2, get_last_background_prcoess_id(h2)))
    h3.cmd('ping -c 100 -i 0.02 10.0.0.4 &')
    background_tasks.append((h3, get_last_background_prcoess_id(h3)))
    h4.cmd('ping -c 100 -i 0.02 10.0.0.3 &')
    background_tasks.append((h4, get_last_background_prcoess_id(h4)))

    while background_tasks:
        h, id = background_tasks.pop()
        h.cmd('wait', id)

    print("All pings ended")


def perfTest():
    """Create network and run simple performance test"""
    topo = SingleSwitchTopo(n=4)
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

    print("all background process is killed!")

    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    perfTest()
