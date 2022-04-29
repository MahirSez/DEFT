#!/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.node import RemoteController

from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel

from time import sleep


n_h = 2


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
    print("Opening Server at {}".format(id))
    h.cmd('bash ../../../../hazelcast-4.2.2/bin/start.sh &')
    return get_last_background_prcoess_id(h)


def create_primary(net, primary_id, backup_id):

    p_h = net.get("h" + str(primary_id))
    b_h = net.get("h" + str(backup_id))
    p_ip = p_h.IP(intf=("h" + str(primary_id) + "-eth0"))
    b_ip = b_h.IP(intf=("h" + str(backup_id) + "-eth0"))


    print("Opening primary at h-{} with backup at h-{}".format(primary_id, backup_id))

    cmd = "xterm -hold -e 'source ../../venv/bin/activate; python perflow-packet-counter.py " + \
        "-i h{}-eth0 -f icmp --dip={} -b {}:8000' &". \
        format(primary_id, p_ip, b_ip)

    print(cmd)
    p_h.cmd(cmd)
    return get_last_background_prcoess_id(p_h)


def create_backup(net, id, port=8000):
    h = net.get("h" + str(id))
    ip = h.IP(intf=("h" + str(id) + "-eth0"))

    print("Opening backup node h" + str(id) + " ip :{}".format(ip))
    cmd = "xterm -hold -T replica -e 'source ../../venv/bin/activate; python backup.py -i {} -p {}' &". \
        format(ip, port)

    print(cmd)
    h.cmd(cmd)
    return get_last_background_prcoess_id(h)


def setUp(net):

    background_process_list = []  # (host, pid) tuple

    ## opening hazlecast server
    ## TODO: Make sure to create a list from here

    for id in range(1, n_h+1):
        h = net.get('h{}'.format(id))
        id = server(h, str(id))
        background_process_list.append((h, id))


    sleep(30)

    print("All hazlecast servers are up!")
    ## create backups (h3 -> h4), (h4->h5), (h5 -> h3) : make a chain


    for p_id in range(1, n_h+1):
        p_h = net.get("h" + str(p_id))
        b_id = p_id + 1 if p_id + 1 <= n_h else 1  # offset one is replica
        b_h = net.get("h" + str(b_id))

        process_id = create_backup(net, b_id)
        background_process_list.append((b_h, process_id))

        process_id = create_primary(net, p_id, b_id)
        background_process_list.append((p_h, process_id))

    sleep(20)

    return background_process_list


def runTest(net):

    pinger1, pinger2 = net.get('h'+str(n_h+1), 'h' + str(n_h+2))

    background_tasks = []

    print("Pinging started!")    

    NUMBER_OF_PKTS = 1009

    # 1500 bytes
    # for i in range(3, 2 + 2*n_h+1, 2):
    #     source_host = h1 if (i//2) % 2 == 0 else h2
    #     s_h_id = 1 if (i//2) % 2 == 0 else 2
    #     target_ip = "10.0.0.{}".format(i)
    #     print('from {}:ping -c {} -s 4096 -i 0.02 {} &'.format(s_h_id,NUMBER_OF_PKTS, target_ip))
    #     source_host.cmd('ping -c {} -s 4096 -i 0.02 {} &'.format(NUMBER_OF_PKTS, target_ip))
    #     background_tasks.append((source_host, get_last_background_prcoess_id(source_host)))

    for i in range(1, n_h+1):
        source_host = pinger1 if (i//2) % 2 == 0 else pinger2
        s_h_id = n_h+1 if (i//2) % 2 == 0 else n_h+2
        target_ip = "10.0.0.{}".format(i)
        print('from {}:ping -c {} -s 4096 -i 0.02 {} &'.format(s_h_id,NUMBER_OF_PKTS, target_ip))
        source_host.cmd('ping -c {} -s 4096 -i 0.02 {} &'.format(NUMBER_OF_PKTS, target_ip))
        background_tasks.append((source_host, get_last_background_prcoess_id(source_host)))

    while background_tasks:
        h, id = background_tasks.pop()
        h.cmd('wait', id)

    print("All pings ended")


def perfTest():
    """Create network and run simple performance test"""
    topo = SingleSwitchTopo(n = n_h + 2) 

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
