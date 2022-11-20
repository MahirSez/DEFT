# Packet Sniffer for NFs

### How to Use

---------------

1. Run mininet with a basic topology
```bash
$ sudo mn --topo=single,2 --mac
```  

2. Open h1 in xterm
```bash
mininet> xterm h1
```  

3. Run the sniffer from a host, say h1
```bash
$ python3 sniffer.py
```  
 
4. From mininet terminal, use basic ping:
```bash
mininet> h2 ping -c <count> h1
```

5. For ping with smaller delay
```bash
mininet> h2 ping -c <count> -i <interval> h2
```

## Important Links

------------------------
1. Scapy Documentation - [Docs](https://scapy.readthedocs.io/en/latest/)
2. Packet sniffer with Scapy - [Here](https://www.geeksforgeeks.org/packet-sniffing-using-scapy/)



## Useful Commands 
-------------------

- find out process ids running on a specific port:
```bash
sudo lsof -t -i:<port>
```
- now killing the process:
```
sudo kill -9 <pid>
```

