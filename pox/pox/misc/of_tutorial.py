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
from pprint import pprint
from pox.lib.packet import *
from pox.lib.addresses import *
from pox.lib.packet.icmp import *
from pox.lib.packet.ethernet import *

# import ipaddress

log = core.getLogger()



class Tutorial (object):
  """
  A Tutorial object is created for each switch that connects.
  A Connection object for that switch is passed to the __init__ function.
  """
  def __init__ (self, connection):
    # Keep track of the connection to the switch so that we can
    # send it messages!
    self.connection = connection
    self.packet_dubug_counter = 0
    self.router_mac_addr = "01:02:03:04:05:06"

    # This binds our PacketIn event listener
    connection.addListeners(self)

    # Use this table to keep track of which ethernet address is on
    # which switch port (keys are MACs, values are ports).
    self.mac_to_port = {}
    self.arp_cache = {}
    self.msg_queue = []

    self.routing_table = [
      ['10.0.1.0/24', '10.0.1.100', 's1-eth1', '10.0.1.1'],
      ['10.0.2.0/24', '10.0.2.100', 's1-eth2', '10.0.2.1'],
      ['10.0.3.0/24', '10.0.3.100', 's1-eth3', '10.0.3.1']
    ]


  def resend_packet (self, packet_in, out_port):
    """
    Instructs the switch to resend a packet that it had sent to us.
    "packet_in" is the ofp_packet_in object the switch had sent to the
    controller due to a table-miss.
    """
    msg = of.ofp_packet_out()
    msg.data = packet_in

    # Add an action to send to the specified port
    action = of.ofp_action_output(port = out_port)
    msg.actions.append(action)

    # Send message to switch
    self.connection.send(msg)


  def act_like_hub (self, packet, packet_in):
    """
    Implement hub-like behavior -- send all packets to all ports besides
    the input port.
    """

    # We want to output to all ports -- we do that using the special
    # OFPP_ALL port as the output port.  (We could have also used
    # OFPP_FLOOD.)
    self.resend_packet(packet_in, of.OFPP_ALL)

    # Note that if we didn't get a valid buffer_id, a slightly better
    # implementation would check that we got the full data before
    # sending it (len(packet_in.data) should be == packet_in.total_len)).

  def handle_ARP_request(self, srcip, dstip):

    log.info("Sending ARP_REQUEST to " + str(dstip))

    arp_req = arp()
    arp_req.hwsrc = EthAddr(self.router_mac_addr)
    arp_req.hwdst = ETHER_BROADCAST
    arp_req.opcode = arp.REQUEST
    arp_req.protosrc = srcip
    arp_req.protodst = dstip
    ether = ethernet()
    ether.type = ethernet.ARP_TYPE
    ether.dst = ETHER_BROADCAST
    ether.src = EthAddr(self.router_mac_addr)
    ether.payload = arp_req

    msg = of.ofp_packet_out()
    msg.data = ether.pack()
    msg.actions.append(of.ofp_action_output(port = of.OFPP_ALL))
    self.connection.send(msg)

  def handle_ARP(self, packet, packet_in): 
    
    if packet.payload.opcode == arp.REQUEST:
      log.info("Received ARP_REQUEST from " + str(packet.src) + ": who has " + str(packet.payload.protodst) )
      arp_reply = arp()
      arp_reply.hwsrc = EthAddr(self.router_mac_addr)
      arp_reply.hwdst = packet.src
      arp_reply.opcode = arp.REPLY
      arp_reply.protosrc = packet.payload.protodst
      arp_reply.protodst = packet.payload.protosrc
      ether = ethernet()
      ether.type = ethernet.ARP_TYPE
      ether.dst = packet.src
      ether.src = EthAddr(self.router_mac_addr)
      ether.payload = arp_reply

      msg = of.ofp_packet_out()
      msg.data = ether.pack()
      msg.actions.append(of.ofp_action_output(port = packet_in.in_port))

      log.info("Sending ARP_REPLY to " + str(packet.src) + ": " + str(self.router_mac_addr) )
      self.connection.send(msg)

    elif packet.payload.opcode == arp.REPLY:
      arp_reply = packet.payload
      log.info("Received ARP_REPLY from " + str(arp_reply.protosrc))
      self.arp_cache[arp_reply.protosrc] = packet.src
      log.debug("Installing in ARP_CACHE " + str(arp_reply.protosrc) +" <--->  " + str(packet.src))
      if len(self.msg_queue) > 0 and self.msg_queue[0][0] == arp_reply.protosrc:
        log.info("Popping msg from queue to " + str(arp_reply.protosrc))
        log.info("Left Messages: " + str(len(self.msg_queue)- 1)) 
        self.forward_from_router(self.msg_queue[0][0], self.msg_queue[0][1])
        self.msg_queue.pop(0)

  def handle_router_echo_reply(self, packet, packet_in):
    log.info("Router replying to ICMP_ECHO from " + str(packet.payload.srcip))
    msgEcho = echo()
    msgEcho.seq = packet.payload.payload.payload.seq + 1
    msgEcho.id = packet.payload.payload.payload.id
    #encapsulate the reachable ICMP packet
    icmpReachable = icmp()
    icmpReachable.type = TYPE_ECHO_REPLY
    icmpReachable.payload = msgEcho

    icmpPkt = ipv4()
    icmpPkt.srcip = packet.payload.dstip
    icmpPkt.dstip = packet.payload.srcip
    icmpPkt.protocol = ipv4.ICMP_PROTOCOL
    icmpPkt.payload = icmpReachable

    #encapsulate the packet into frame
    icmpFrame2 = ethernet()
    icmpFrame2.type = ethernet.IP_TYPE
    icmpFrame2.dst = packet.src
    icmpFrame2.src = packet.dst
    icmpFrame2.payload = icmpPkt

    msg = of.ofp_packet_out()
    msg.data = icmpFrame2.pack()
    
    action = of.ofp_action_output(port = packet_in.in_port)
    msg.actions.append(action)
    self.connection.send(msg)

  def forward_from_router(self, dstip, packet):
    msg = of.ofp_packet_out()
    packet.src = self.router_mac_addr
    dstmac = self.arp_cache[dstip]
    packet.dst = dstmac
    msg.data = packet.pack()
    action = of.ofp_action_output(port = self.mac_to_port[ dstmac] )
    # log.debug("Sending through port " + str(self.mac_to_port[ dstmac]) )
    msg.actions.append(action)
    self.connection.send(msg)


  def handle_IP(self, packet, packet_in): 
    
    log.info("Received IP packet from " + str(packet.src))
    ip_packet = packet.payload
    icmp_packet = ip_packet.payload
    
    if ip_packet.protocol == ipv4.ICMP_PROTOCOL:
      log.info("The packet is ICMP from " + str(ip_packet.srcip) + " to " + str(ip_packet.dstip))
      
      if icmp_packet.type == TYPE_ECHO_REQUEST:
        log.info("The packet is ECHO_REQUEST ")
        # echo_req_packet = icmp_packet.payload  
      elif icmp_packet.type == TYPE_ECHO_REPLY:
        log.info("The packet is ECHO_REPLY")
        # echo_reply_packet = icmp_packet.payload
      else: 
        log.info("The packet is OTHER_ICMP ")
    elif ip_packet.protocol == ipv4.TCP_PROTOCOL:
      log.info("The packet is TCP from " + str(ip_packet.srcip) + " to " + str(ip_packet.dstip))


    for entries in self.routing_table:
      if ip_packet.dstip.inNetwork(entries[0]):
        if ip_packet.dstip == entries[3]:
          if(icmp_packet.type == TYPE_ECHO_REQUEST):
            self.handle_router_echo_reply(packet, packet_in)
          else:
            log.info("Unknown ICMP packet  from " + str(ip_packet.srcip) + " to " + str(ip_packet.dstip))
        elif ip_packet.dstip not in self.arp_cache:
          log.info("Queing up message frm " + str(ip_packet.srcip) + " to " + str(ip_packet.dstip) )
          self.msg_queue.append((ip_packet.dstip, packet))
          self.handle_ARP_request(IPAddr(entries[3]), ip_packet.dstip)
        else:
          log.info("Controller forwarding packet of src " + str(ip_packet.srcip)  + " dst " + str(ip_packet.dstip))
          self.forward_from_router(ip_packet.dstip, packet)
        return


  def act_like_router(self, packet, packet_in):

    self.mac_to_port[packet.src] = packet_in.in_port
    if packet.type == packet.ARP_TYPE:
      self.handle_ARP(packet, packet_in)
    elif packet.type == packet.IP_TYPE:
      self.arp_cache[packet.payload.srcip] = packet.src
      log.info("Installing in arp_cache " + str(packet.payload.srcip) +" <--->  " + str(packet.src))
      self.handle_IP(packet, packet_in)



  def act_like_switch (self, packet, packet_in):
    """
    Implement switch-like behavior.
    """

    # Learn the port for the source MAC
    self.mac_to_port[packet.src] = packet_in.in_port

    print("whaaaa? " + str(packet.src))

    # if the port associated with the destination MAC of the packet is known:
    if packet.dst in self.mac_to_port:

      out_port = self.mac_to_port[packet.dst]
      # Send packet out the associated port
      # self.resend_packet(packet_in, self.mac_to_port[packet.dst])

      # Once you have the above working, try pushing a flow entry
      # instead of resending the packet (comment out the above and
      # uncomment and complete the below.)
      log.debug("Installing flow...")
      log.debug(str(packet.src) + " --> " + str(packet.dst))
      # Maybe the log statement should have source/destination/port?

      msg = of.ofp_flow_mod()
      
      # Set fields to match received packet
      msg.match = of.ofp_match.from_packet(packet)
      msg.match.in_port = packet_in.in_port
      
      log.debug("Forwar rule to forward via " + str(out_port))
      # Hardcoding do UNDO
      msg.actions.append(of.ofp_action_output(port = out_port))
      # msg.actions.append(of.ofp_action_output(port = 1))
      # msg.actions.append(of.ofp_action_output(port = 2))


      msg.data = packet_in

      self.connection.send(msg)

    else:
      # Flood the packet out everything but the input port
      # This part looks familiar, right?
      self.resend_packet(packet_in, of.OFPP_ALL)

     # DELETE THIS LINE TO START WORKING ON THIS #


  def _handle_PacketIn (self, event):
    """
    Handles packet in messages from the switch.
    """

    packet = event.parsed # This is the parsed packet data.
    if not packet.parsed:
      log.warning("Ignoring incomplete packet")
      return
  
    packet_in = event.ofp # The actual ofp_packet_in message.

    # Comment out the following line and uncomment the one after
    # when starting the exercise.
    # self.act_like_hub(packet, packet_in)
    self.act_like_switch(packet, packet_in)
    # self.act_like_router(packet, packet_in)



def launch ():
  """
  Starts the component
  """
  def start_switch (event):
    log.debug("Controlling %s" % (event.connection,))
    Tutorial(event.connection)
  core.openflow.addListenerByName("ConnectionUp", start_switch)
