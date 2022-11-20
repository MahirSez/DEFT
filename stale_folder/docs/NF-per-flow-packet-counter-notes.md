# Per Flow Packet Counter

### About  

---
This NF sniffs for packets on an interface and maintains a map on Hazelcast cluster. The map
keeps a record of number of packets for each unique flow.


### How to use 

---
1. Open a Hazelcast cluster

2. Run the NF
```bash
$ python3 perflow-packet-counter.py -i <interface> -f <filter> --dip <destination_ip>
```

---
**Options**  
 - -i INTERFACE / --iface=INTERFACE : Interface to sniff on
 - -f FILTER / --filter=FILTER: Packet type e.g. tcp, icmp
 - --dip=DEST_IP: IP to filter on
---
 

### Test

---
1. To run the test
```bash
$ sudo python3 tests/test1.py
```
