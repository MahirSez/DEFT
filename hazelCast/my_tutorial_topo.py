#!/usr/bin/python

from mininet.cli import CLI
# from mininet.examples.linuxrouter import LinuxRouter
from mininet.log import setLogLevel, info, error
from mininet.net import Mininet
from mininet.topo import SingleSwitchTopo, Topo
from mininet.node import RemoteController, OVSSwitch, Node, CPULimitedHost
from mininet.link import TCIntf, Intf
from mininet.util import custom, irange


class StandaloneSwitch(OVSSwitch):
	def __init__(self, name, **params):
		OVSSwitch.__init__(self, name, failMode='standalone', **params)

	def start(self, controllers):
		return OVSSwitch.start(self, [])

#
# class LinuxRouter(Node):
# 	"A Node with IP forwarding enabled."
#
# 	def config(self, **params):
# 		super(LinuxRouter, self).config(**params)
# 		# Enable forwarding on the router
# 		self.cmd('sysctl net.ipv4.ip_forward=1')
#
# 	def terminate(self):
# 		self.cmd('sysctl net.ipv4.ip_forward=0')
# 		super(LinuxRouter, self).terminate()
#

class SingleRouterTopo(Topo):
	"Single switch connected to k hosts."

	def build(self, k=2, **_opts):
		"k: number of hosts"
		self.k = k
		s1 = self.addSwitch('s1')
		s2 = self.addSwitch('s2', cls=StandaloneSwitch)
		for h in irange(1, k):
			host = self.addHost('h%s' % h, defaultRoute='via 192.168.1.254')
			self.addLink(host, s1)
			self.addLink(host, s2, params1={'ip': '192.168.1.%s/24' % h})
		gate = self.addNode('gate', inNamespace=False, ip='192.168.1.254/24')
		self.addLink(gate, s2)
	# params1 = {'ip': '192.168.0.254/24'}
	# link.intf1.setIP('192.168.0.254', 24)


def setup(net):
	net['h1'].cmd("xterm -hold -e 'redis-server --protected-mode no' &")
	# net['h1'].cmd("redis-cli flushall")

	for i in range(1, 2):
		net['h%s'%i].cmd("xterm -hold -e 'bash hazelcast-4.2.2/bin/start.sh' &")

	for i in range(1, 2):
		net['h%s'%i].cmd("xterm -hold -e 'source nf_script.sh %s' &" %i)

	# for i in range(1, 2):
	# 	net['h%s'%i].cmd("xterm -hold -e 'bash host_script.sh %s' &" %i)





if __name__ == '__main__':
	setLogLevel('info')

	# Create rate limited interface
	intf = custom(TCIntf, bw=50)
	host = custom(CPULimitedHost, sched='cfs', cpu=0.1)

	# Create data network
	net = Mininet(topo=SingleRouterTopo(k=5), switch=OVSSwitch,
				  controller=RemoteController, intf=intf, host=host,
				  autoSetMacs=True, autoStaticArp=True)

	# Run network
	net.start()
	info('*** Routing Table on Router:\n')
	print(net['gate'].cmd('route -n'))
	setup(net)
	
	CLI(net)
	net.stop()

# sh ovs-ofctl add-flow s2 in_port=1,actions=output:6
# sh ovs-ofctl dump-flows s2
