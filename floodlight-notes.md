

https://courses.cs.duke.edu/fall14/compsci590.4/notes/slides_floodlight_updated.pdf
1. topology Discovery -> LLDP protocol
2. flow is definted as all packets with the same match
3. In Floodlight, each match is an object of `org.openflow.protocol.OFMatch` 
4. Flow installation example -> 
5. A set of operations associated with a match, for all packets with the same match, the operations will be applied
6. See the pdf for action installation
7. In Floodlight, each FlowMod message is a object of OFFlowMod: – `org.openflow.protocol.OFFlowMod`
8. Summary ->
	To install a flow
	1. create a FlowMod message
	2. specify the match of the flow in the message
	3. specify the actions for the flow
	• <<output>> in this case 
	4. send the message to the switch



OpenNF code notes
------------------

1. OFMessage listeners -> MiddleboxDiscovery, MiddleboxInput
2. `MiddleboxDiscovery` -> calls `middleboxDiscovered()` of `sdmbnManager`
3. New Switch connected -> `net.floodlightcontroller.core.internal.Controller.channelConnected()` called
4. Switch disconnected -> `net.floodlightcontroller.core.internal.Controller.channelDisconnected()` called
5. SDMBNManager forwards the PACKET_IN msg to the SdmbnListeners. All SdmbnListeners implement `edu.wisc.cs.wisdom.sdmbn.ISdmbnListener`
6. SdmbnListeners are basically packet listeners for openNF

7. The gate node is super important.
8. The gate node's ip has to match with the ip listed at /usr/local/etc/sdmbn.conf
9. the controller keeps listening on this 

9. Prads sends a bunch of tcp packets just after launching on a host (why?)


10. Method call chain in openNF:
	- SdmbnManager.startup() -> 		
		floodlightProvider.addOFMessageListener(OFType.PACKET_IN, discovery);
		floodlightProvider.addOFMessageListener(OFType.PACKET_IN, input);
	- MiddleBoxDiscoery.receive() ->	
		sdmbnManager.middleboxDiscovered(discovery, sw, pi.getInPort()) -> 		
		Middlebox mb = obtainMiddlebox(discovery.host, discovery.pid); ->
		testTimed.middleboxLocationUpdated() ->
		testTimed.addMiddlebox()
		-> testTimed.executeStep() -> initialRuleSetup() -> changeForwarding() -> initiateOperation()
		-> sdmbnmanager.move() -> MoveOperation.execute() -> MoveOperation.issueGet()




## Installing Flow
--------------------

1. Match: In Floodlight, each match is an object of org.openflow.protocol.OFMatch.
2. examples of Matches: 
– <src ip: 10.0.0.2, dst ip 10.0.0.3, src port: 90>
– <src mac addr: 00:0a:95:9d:68:16>
– <vlan tag: 4000, protocol: ipv4>


3. Action: A set of operations associated with a match, for all packets with the same match, the operations will be applied
4. examples of Actions: 
– <output on port 2>
– <set dst IP address to 10.0.0.3>
– <set mac address to 00:0a:95:9d:68:16>

5. In Floodlight, each actions is a object of org.openflow.protocol.OFAction – org.openflow.protocol.action.OFAction

6. FlowMod is the message regarding flow installation/deletion
7. There are a number of different types of messages a controller can send to a switch, i.e.: 
– to query port stats: OFPortStatus 
– to query vendor: OFVendor 
– to modify status of a port: OFPortMod

8. In Floodlight, each FlowMod message is a object of OFFlowMod: – org.openflow.protocol.OFFlowMod

9. To install a flow
– 1. create a FlowMod message
– 2.	 specify the match of the flow in the message
– 3. specify the actions for the flow
	• <output> in this case 
– 4. send the message to the switch