
# State Sharing with HazelCast


### Setup - 1: No scaling + No migration + Only state update
---------------------------------------------------------

- 1 Client -> External entity that will send a packet to process (host OS, outside mininet) --> 1 mininet host

- 4 mininet hosts -> 3 will participate in consensus


1. Each host in mininet will be have a single NF running inside it. 
2. Each host in mininet will have a listener that comes with the NF. This listener will listen for incoming packets
3. Each host will be a part of hazelCast cluster and act as an instance participating in the consensus.

4. A client will send a packet to a host in the mininet.
5. Upon receiving, the host will process the packet via its NF and calculate the states to be stored in the cluster
6. Upon calculating a state / a batch of state / after every x time unit -> 
	a host will run the hazelCast client script to update the distributed data inside the cluster

7. If the host updates a batch of state / after every x time unit ->
	Have to store the intermediate states "somewhere" (??)



Q1. What NF to chooose -> Will start with a packet counter. Then firewall/prads etc.
Q2. What state to store -> `packet_count` for packet count counter. Other states depend on the NF
* But an already built NF would be better ig. because otherwise would have to implement packet listener :(


* Will continue to parse Prads.log and calculate state ->
	i. A script will continue to poll on prads.log
	ii. whenever a new update appears insert it in the cluster



### HazelCast Links
-------------------

* Github -> https://github.com/hazelcast/hazelcast

* Python Client-> https://github.com/hazelcast/hazelcast-python-client

* getting started --> https://hazelcast.readthedocs.io/en/stable/getting_started.html#getting-started

* exmplaes --> https://github.com/hazelcast/hazelcast-python-client/tree/master/examples

* API documentation -->  https://hazelcast.readthedocs.io/en/stable/client.html#hazelcast.client.HazelcastClient

* Starting a cluster --> https://hazelcast.org/imdg/get-started/



### Todos
----------


1. Run floodlight -> OK
2. Run mininet -> make 4 hosts, single topology -> OK
3. Make 1 hosts form a cluster -> OK

4. Test with tcpdump
	4.1. Pipe tcpdump output to a file -> OK
	4.2. Poll on the output file, when a new line appears, run the client code > OK

5. Prads -> check how to use -> OK
6. Replace tcpdump with prads -> OK

7. pcap -> check how to use -> OK
8. Use pcap to broadcast / replay packets -> Ok

9. Merge pcap + prads + hazelCast -> OK



### Experiment Steps
--------------------

* Install & run floodlight-v0.90 from https://floodlight.atlassian.net/wiki/spaces/floodlightcontroller/pages/1343544/Installation+Guide

* Install mininet:
```bash
$ sudo apt install mininet
```

* Create topology:
```bash
$ sudo mn --mac --controller remote --topo single,4
```

* Check switch's flow table:
```bash
mininet> sh ovs-ofctl dump-flows s1
```

* Insert flow entry manually. This will forward all of h4's flows to h1.
```bash
$ mininet> sh ovs-ofctl add-flow s1 in_port=4,actions=output:1
```

* Download & extract HazelCast IMDG from https://hazelcast.com/open-source-projects/downloads/#hazelcast-imdg

* On mininet, open xterm terminal for h1 h2 h3:
```bash
$ mininet> xterm h1 h2 h3
```

* On each xterm host, change directory to the hazelcast folder. Create and join the hosts to the cluster. Each host would acknowledge each other
```
bin/start.sh
```

* Create a pcap file:
```bash
$ sudo tcpdump -w capture.pcap -i wlp2s0 tcp -c 25000
```

* Install prads:
```bash
$ sudo apt install prads
```

* Run prads on h1's terminal. A log file would be generated with the name `prads.log`. Prads would keep listern for incoming packets:
```bash
$ prads -i h1-eth0 -l prads.log
```

* Open pipenv shell on h1's terminal:
```bash
$ pipenv shell
```

* Run the client code.This will continuously listen on `prads.log` file and trigger on any new appended line in te log:
```bash
(pipenv)$ python3 client.py
```

* Open h4's terminal and replay pcap file's packets at 500pkt/s:
```bash
$ sudo tcpreplay -p 500 -i h4-eth0 capture.pcap  
```
* After all packets are replayed, the pn-counter's final output would match the number of lines in `prads.log`



### Additional useful Commands
---------------------------

* To ping a host:
```bash
$ ping -c 10 10.0.0.2
```

* To tcpdump ip packets:
```bash
$ tcpdump -i h1-eth0 ip
```

* Change a pcap file's destination IP:
```bash
$ tcprewrite --infile=capture.pcap --outfile=temp.pcap --dstipmap=0.0.0.0/0:10.0.0.1 --enet-dmac=00:00:00:00:00:01
```

* Change pcap file's src IP:
```bash
$ tcprewrite --infile=temp.pcap --outfile=temp1.pcap --srcipmap=0.0.0.0/0:10.0.0.4 --enet-smac=00:00:00:00:00:04
```

* Fix checksum:
```bash
$ tcprewrite --infile=temp1.pcap --outfile=final.pcap --fixcsum
```

* Altogether: 
```bash
$  tcprewrite --infile=capture.pcap --outfile=final.pcap --dstipmap=0.0.0.0/0:10.0.0.1 --enet-dmac=00:00:00:00:00:01 --srcipmap=0.0.0.0/0:10.0.0.4 --enet-smac=00:00:00:00:00:04 --fixcsum
```

* tcpdump to a file real time & run client code:
```bash
$ tcpdump -l -i h1-eth0 ip | tee >> dump.log >(python3 client.py)
```
