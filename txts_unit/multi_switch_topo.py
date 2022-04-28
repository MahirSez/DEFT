from mininet.topo import Topo


class MultiSwitchTopo(Topo):

    def build(self, n=2):


        switch1 = self.addSwitch('s1')
        switch2 = self.addSwitch('s2')

        for h in range(n):
            # Each host gets 50%/n of system CPU
            host = self.addHost('h%s' % (h + 1),
                                cpu=.5 / n)
            self.addLink(host, switch2)

        client = self.addHost('client')
        stampModule = self.addHost('stamper')

        self.addLink(switch1, stampModule)
        self.addLink(stampModule, switch2)
        self.addLink(switch1, client)


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
