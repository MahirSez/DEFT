# Copyright 2012 James McCauley
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
This component is for use with the OpenFlow tutorial.

It acts as a simple hub, but can be modified to act like an L2
learning switch.

It's roughly similar to the one Brandon Heller did for NOX.

./pox.py log.level --DEBUG misc.of_tutorial misc.full_payload

Iperf: flow_out -> *** Results: ['582 Kbits/sec', '1.54 Mbits/sec']



"""

from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.packet.ethernet import *

log = core.getLogger()

switchID = 1

macToName = {
	'00:00:00:00:00:01': 'client',
	'00:00:00:00:00:02': 'h1',
	'00:00:00:00:00:03': 'h2',
	'00:00:00:00:00:04': 'stamper',
	'ff:ff:ff:ff:ff:ff': 'flood'
}

CLIENT_MAC = EthAddr('00:00:00:00:00:01')
STAMPER_MAC = EthAddr('00:00:00:00:00:04')


class Tutorial(object):
	"""
	A Tutorial object is created for each switch that connects.
	A Connection object for that switch is passed to the __init__ function.
	"""

	# init is called for each switch
	def __init__(self, connection):
		global switchID
		# Keep track of the connection to the switch so that we can
		# send it messages!
		self.connection = connection
		# This binds our PacketIn event listener
		connection.addListeners(self)

		self.switchID = switchID
		switchID += 1

		# Use this table to keep track of which ethernet address is on
		# which switch port (keys are MACs, values are ports).
		self.mac_to_port = {}
		if self.switchID == 1:
			self.mac_to_port[STAMPER_MAC] = 1
		elif self.switchID == 2:
			self.mac_to_port[STAMPER_MAC] = 3

		log.debug("Switch ID = " + str(self.switchID))


	def resend_packet(self, packet_in, out_port):
		"""
		Instructs the switch to resend a packet that it had sent to us.
		"packet_in" is the ofp_packet_in object the switch had sent to the
		controller due to a table-miss.
		"""
		msg = of.ofp_packet_out()
		msg.data = packet_in

		# Add an action to send to the specified port
		action = of.ofp_action_output(port=out_port)
		msg.actions.append(action)

		# Send message to switch
		self.connection.send(msg)

	def act_like_hub(self, packet, packet_in):
		"""
		Implement hub-like behavior -- send all packets to all ports besides
		the input port.
		"""

		# We want to output to all ports -- we do that using the special
		# OFPP_ALL port as the output port.  (We could have also used
		# OFPP_FLOOD.)
		self.resend_packet(packet_in, of.OFPP_ALL)

	def act_like_switch(self, packet, packet_in):
		"""
		Implement switch-like behavior.
		"""

		print(type(packet))

		# Learn the port for the source MAC
		self.mac_to_port[packet.src] = packet_in.in_port


		srcName = "unknown" if str(packet.src) not in macToName else macToName[str(packet.src)]
		dstName = "unknown" if str(packet.dst) not in macToName else macToName[str(packet.dst)]
		switchName = 'switch-1' if self.switchID == 1 else 'switch-2'
		packetType = ethtype_to_str(packet.type)
		print(switchName + " : " + srcName + " --> " + dstName)
		print(switchName + " : " + str(packet.src) + " --> " + str(packet.dst) + " :: " + packetType)

		print(self.mac_to_port)


		# if the port associated with the destination MAC of the packet is known:
		if packet.dst in self.mac_to_port:

			if self.switchID == 1 and packet.src == CLIENT_MAC and packet.type != packet.ARP_TYPE:
				out_port = self.mac_to_port[STAMPER_MAC]
			else:
				out_port = self.mac_to_port[packet.dst]

			# log.debug("Installing flow...")
			# log.debug(str(packet.src) + " --> " + str(packet.dst))

			msg = of.ofp_flow_mod()

			# Set fields to match received packet
			msg.match = of.ofp_match.from_packet(packet)
			msg.match.in_port = packet_in.in_port

			print("Packets from " + str(packet.src) + " to " + str(packet.dst) + " will go through port " + str(out_port))
			msg.actions.append(of.ofp_action_output(port=out_port))

			if self.switchID == 2 and packet.src == CLIENT_MAC and packet.type != packet.ARP_TYPE and macToName[str(packet.dst)] == 'h1':
				msg.actions.append(of.ofp_action_output(port=2))

			msg.data = packet_in
			self.connection.send(msg)
		else:
			# Flood the packet out everything but the input port
			self.resend_packet(packet_in, of.OFPP_ALL)

	def _handle_PacketIn(self, event):
		"""
		Handles packet in messages from the switch.
		"""

		packet = event.parsed  # This is the parsed packet data.
		if not packet.parsed:
			log.warning("Ignoring incomplete packet")
			return

		packet_in = event.ofp  # The actual ofp_packet_in message.

		# Comment out the following line and uncomment the one after
		# when starting the exercise.
		# self.act_like_hub(packet, packet_in)
		self.act_like_switch(packet, packet_in)


def launch():
	"""
	Starts the component
	"""
	def start_switch(event):
		log.debug("Controlling %s" % (event.connection,))
		Tutorial(event.connection)

	core.openflow.addListenerByName("ConnectionUp", start_switch)
