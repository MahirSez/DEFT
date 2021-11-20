### Setup - 2: Scaling + Migration Without Dynamic Load Balancing
-----------------------------------------------------------------

#### Participatnst

- 5 Mininet Hosts
- 1 controller


- 3 Mininet Hosts forms a cluster and each has an NF listening for incoming packets
- The controller continuously monitors them by querying the number of packets they have processed so far
- The hosts keep their processed packet count in their memory via Redis
- When host-5 is ready to send .pcap file packets, the controller installs a flow  5 -> 1
- Host-1 keeps receiving all the incoming packets. When host-1 processes a certain amount of packet, the controller changes the flow in the switch to 5 -> 2
- Then host-2 processes the rest of the traffic


Experiment Steps
------------------

- Run floodlight controller
- Change directory to `hazelCast/` and run:

```bash
sudo python my_tutorial_topo.py
```
This would launch:
	1. 3 host terminals that form a hazelCast cluster
	2. 1 Redis server
	3. 3 NFs listening or incoming packets
	4. 3 controller listeners responding to controller queries

- After the NFs have connected their hazelCast client, start replaying the traffic on host-5:

```bash
./traffic_script.sh
```

At first, host-1 processes all the incoming traffic. After processing a certain amount of packets it pauses and host-2 processes the rest of the traffic


