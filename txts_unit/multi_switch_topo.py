from mininet.topo import Topo


class MultiSwitchTopo(Topo):

    def build(self, n=2):


        switch1 = self.addSwitch('s1')
        switch2 = self.addSwitch('s2')
        for h in range(n):
            host = self.addHost('h%s' % (h + 1))
            self.addLink(host, switch2)

        client = self.addHost('client')
        stamper = self.addHost('stamper')

        self.addLink(switch1, stamper)
        self.addLink(stamper, switch2)
        self.addLink(switch1, client)
        self.addLink(switch1, switch2)


topos = { 'multiSwitch': ( lambda: MultiSwitchTopo() ) }

    
#
# if __name__ == '__main__':
#     setLogLevel('info')
#     topo = MultiSwitchTopo(n=3)
#     net = Mininet(topo=topo,
#                   host=CPULimitedHost, link=TCLink,
#                   controller=RemoteController)
#     net.start()
#     print("Dumping host connections")
