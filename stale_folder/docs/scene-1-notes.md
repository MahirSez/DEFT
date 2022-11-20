### Setup - 1: No scaling + No migration + Only state update
---------------------------------------------------------

- 1 Client -> External entity that will send a packet to process (host OS, outside mininet) --> 1 mininet host

- 4 mininet hosts -> 3 will participate in consensus

1. Controller: Floodlight
2. Mininet topology: 4 hosts, 1 switch. All the hosts are directly connected to the switch.
3. 3 Mininet hosts form a cluster: host-1, host-2, and host-3.  These hosts participate in the consensus protocol.
4. Prads runs on host-1 and listens for incoming packets.
5. We have a .pcap file consisting of 25,000 packets. host-4 starts replaying those packets to host-1.
6. Upon receiving each packet, prads logs anomaly-related data to a log file. Whenever prads logs any data, host-1 updates the "counter" variable and informs other cluster instances (The consensus part is handled entirely by HazelCast).



### HazelCast Links
-------------------

* Github -> https://github.com/hazelcast/hazelcast

* Python Client-> https://github.com/hazelcast/hazelcast-python-client

* getting started --> https://hazelcast.readthedocs.io/en/stable/getting_started.html#getting-started

* exmplaes --> https://github.com/hazelcast/hazelcast-python-client/tree/master/examples

* API documentation -->  https://hazelcast.readthedocs.io/en/stable/client.html#hazelcast.client.HazelcastClient

* Starting a cluster --> https://hazelcast.org/imdg/get-started/



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

```bash
$ bash my_listener.sh h1-eth0 . 192.168.1.1 8080
```

