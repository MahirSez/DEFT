

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


