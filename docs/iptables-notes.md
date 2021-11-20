

# IpTables
----------

1. The packet filtering mechanism provided by iptables is organized into three different kinds of structures: 
	1. tables
	2. chains
	3. targets

2. A table is something that allows you to process packets in specific ways
3. these tables have chains attached to them. These chains allow you to inspect traffic at various points, such as when they just arrive on the network interface or just before they’re handed over to a process.

4. You can add rules to them match specific packets — such as TCP packets going to port 80 — and associate it with a target. A target decides the fate of a packet, such as allowing or rejecting it.


5. When a packet arrives (or leaves, depending on the chain), iptables matches it against rules in these chains one-by-one. When it finds a match, it jumps onto the target and performs the action associated with it.

6. If it doesn’t find a match with any of the rules, it simply does what the default policy of the chain tells it to. The default policy is also a target. By default, all chains have a default policy of allowing packets.





## Tables
-------------

1. tables allow you to do very specific things with packets. 
2. On a modern Linux distributions, there are four tables:
	1. The filter table:	It is used to make decisions about whether a packet should be allowed to reach its destination.
	2. The mangle table:	This table allows you to alter packet headers in various ways, such as changing TTL values.
	3. The nat table:		This table allows you to route packets to different hosts on NAT (Network Address Translation) networks by changing the source and destination addresses of packets.  often used to allow access to services that can’t be accessed directly, because they’re on a NAT network.
	4. The raw table: The raw table allows you to work with packets before the kernel starts tracking its state. In addition, you can also exempt certain packets from the state-tracking machinery.


## Chains
------------
1. each of these tables are composed of a few default chains.
2. chains allow you to filter packets at various points.
3. List of chains:
	1. The PREROUTING chain:	Rules in this chain apply to packets as they just arrive on the network interface. This chain is present in the nat, mangle and raw tables.
	2. The INPUT chain: Rules in this chain apply to packets just before they’re given to a local process. This chain is present in the mangle and filter tables.
	3. The OUTPUT chain: The rules here apply to packets just after they’ve been produced by a process. This chain is present in the raw, mangle, nat and filter tables.
	4. The FORWARD chain: The rules here apply to any packets that are routed through the current host. This chain is only present in the mangle and filter tables.
	5. The POSTROUTING chain: The rules in this chain apply to packets as they just leave the network interface. This chain is present in the nat and mangle tables.

## Targets
-----------

1. Some targets are terminating, which means that they decide the matched packet’s fate immediately. The packet won’t be matched against any other rules. The most commonly used terminating targets are:

	1. ACCEPT: This causes iptables to accept the packet.
	2. DROP: iptables drops the packet. To anyone trying to connect to your system, it would appear like the system didn’t even exist.
	3. REJECT: iptables “rejects” the packet. It sends a “connection reset” pac.ket in case of TCP, or a “destination host unreachable” packet in case of UDP or ICMP.

2. On the other hand, there are non-terminating targets, which keep matching other rules even if a match was found. An example of this is the built-in LOG target. When a matching packet is received, it logs about it in the kernel logs. . However, iptables keeps matching it with rest of the rules too.



## Notes
---------------

1. You also need to execute all iptables commands as root.


## Blocking IPs
-----------------
1.

```bash
iptables -t filter -A INPUT -s 59.45.175.62 -j REJECT
```
-  The `-t` switch specifies the table in which our rule would go into — in our case, it’s the filter table.
-  The `-A` switch tells iptables to “append” it to the list of existing rules in the INPUT chain.
-  the `-s` switch simply sets the source IP that should be blocked.
-	Finally, the `-j` switch tells iptables to “reject” traffic by using the REJECT target. If you want iptables to not respond at all, you can 
use the DROP target instead.

2. Default table -> filter

3. You can also block IP ranges by using the CIDR notation. If you want to block all IPs ranging from 59.145.175.0 to 59.145.175.255, you can do so with:
```bash
iptables -A INPUT -s 59.45.175.0/24 -j REJECT
```

4. If you want to block output traffic to an IP, you should use the OUTPUT chain and the -d flag to specify the destination IP:
```bash
iptables -A OUTPUT -d 31.13.78.35 -j DROP
```

## Listing rules
------------------

1. . If you want to see these rules later, you can use the -L switch. Also, as we will see in the next section, it’s very helpful to see line numbers for these rules, so we’ll also use the --line-numbers switch.

```bash
iptables -L --line-numbers
```

2. This list is also from the filter table, and you can list other tables with the -t switch.

3. -n -> shows numeric value of ips


## Deleting rules
-------------------

1. Removing it is easy: simply replace -A with -D, which deletes a rule:

```bash
iptables -D INPUT -s 221.194.47.0/24 -j REJECT
```

2. If you want to delete the second rule from the INPUT chain, the command would be:

```bash
iptables -D INPUT 2
```

3. When you delete a rule that isn’t the last rule, the line numbers change, so you might end up deleting the wrong rules! So, if you’re deleting a bunch of rules, you should first delete the ones with the highest line numbers. 

4. Sometimes, you may need to remove all rules in a particular chain. Deleting them one by one isn’t practical, so there’s the -F switch which “flushes” a chain. For example, if you want to flush the filter table’s INPUT chain, you would run:

```bash
iptables -F INPUT
```

## Inserting and replacing rules
-------------------------------

1. Since iptables evaluates rules in the chains one-by-one, you simply need to add a rule to “accept” traffic from this IP above the rule blocking 59.45.175.0/24. So, if you run the command:

```bash
iptables -I INPUT 1 -s 59.45.175.10 -j ACCEPT
```

This rule is inserted at the first line, and it makes the rule blocking 59.45.175.0/24 come to the second line. 

2. You can also replace rules with the -R switch

```bash
iptables -R INPUT 1 -s 59.45.175.10 -j ACCEPT
```

## Protocols and modules
-----------------------

1. Say, you want to block all incoming TCP traffic. You simply need to specify the protocol with -p like so:

```bash
iptables -A INPUT -p tcp -j DROP
```

2. Say, you need to block SSH access for an IP range. You have to first match all TCP traffic, like we did in the example above. Then, to check the destination port, you should first load the tcp module with -m. Next, you can check if the traffic is intended to the SSH destination port by using --dport. Thus, the entire command would be:

```bash
iptables -A INPUT -p tcp -m tcp --dport 22 -s 59.45.175.0/24 -j DROP
```

3. Now, perhaps you want to block SSH and VNC access for the IP range. While you can’t specify multiple ports with the tcp module, you can do so with the multiport module. Then, you can specify the port numbers with --dports

```bash
iptables -A INPUT -p tcp -m multiport --dports 22,5901 -s 59.45.175.0/24 -j DROP
```


4. Say, you want to block ICMP address mask requests (type 17). First, you should match ICMP traffic, and then you should match the traffic type by using icmp-type in the icmp module:

```bash
iptables -A INPUT -p icmp -m icmp --icmp-type 17 -j DROP
```


## The connection tracking module
-------------------------------------

1. If you’ve tried blocking certain IPs on the INPUT chain, you might have noticed an interesting caveat — you can’t access the services hosted on those IPs either! You might think that rules in the INPUT chain are somehow affecting traffic on the OUTPUT chain, but that isn’t the case. The packets from your system do reach the server. However, the packets that the server sends to your system get rejected. (See the next section for an additional example.)
2.  Connections tracked by this module will be in one of the following states:
	1. NEW: This state represents the very first packet of a connection.
	2. ESTABLISHED: This state is used for packets that are part of an existing connection. For a connection to be in this state, it should have received a reply from the other host.
	3. RELATED: This state is used for connections that are related to another ESTABLISHED connection. An example of this is a FTP data connection — they’re “related” to the already “established” control connection.
	4. INVALID: This state means the packet doesn’t have a proper state. This may be due to several reasons, such as the system running out of memory or due to some types of ICMP traffic.
	5. UNTRACKED: Any packets exempted from connection tracking in the raw table with the NOTRACK target end up in this state.
	6. DNAT: This is a virtual state used to represent packets whose destination address was changed by rules in the nat table.
	7. SNAT: Like DNAT, this state represents packets whose source address was changed.

3. Thus, you need to place a rule like the one below, usually at the very top. (If this isn’t the first rule, use -I to place it at the top.) The --ctstate switch sets the states. On some older kernels, this module is named state and the switch is named --state instead of --ctstate.

```bash
iptables -A INPUT -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
```

4. In addition, it’s generally a good idea to drop any packets in INVALID state. You can place it just below the position where you placed the above rule.

```bash
iptables -A INPUT -m conntrack --ctstate INVALID -j DROP
```

## Changing the default policy
------------------------------------

1.  By default, the default chains have a default policy of accepting all traffic.
2. You can change the default policy with the -P switch. Perhaps you’re configuring iptables for your home computer, and you don’t want any local programs to receive inbound connections. Once you’ve set iptables to accept packets from related and established connections, you can switch the INPUT chain’s policy to DROP with:

```bash
iptables -P INPUT DROP
```

3. Keep in mind that you should first accept packets from established and related connections before using this rule! If you don’t, you’ll find out that you can’t use any internet based applications, becuase the responses coming in through the INPUT chain will be dropped.


## Selecting interfaces
-------------------------

1. Since iptables matches packets to every rule in a chain, things can get really slow when there are a lot of rules. In such cases, it’s useful to exempt certain kinds of traffic.

2. It’s useless to filter these kinds of traffic, so you can allow it. The loopback interface is typically named lo and you can add a rule like this at the top of the INPUT chain:

```bash
iptables -A INPUT -i lo -j ACCEPT
```

- The -i flag specifies the input interface
- Here, we’ve assumed that the INPUT chain is empty and you’re adding the first rule. If that isn’t the case, you need to use the -I switch to add it at the top.

3. For the OUTPUT chain, you’ll need to use the -o flag, which stands for “output interface”. As an example, say you want to block the IP range 121.18.238.0/29, only when you’re on WiFi. If the WiFi interface is named wlan0, you can add a rule like the one below:

```bash
iptables -A OUTPUT -o wlan0 -d 121.18.238.0/29 -j DROP
```

## Negating conditions
---------------------------


1. in some cases, you may need to negate these condition checks. iptables provides the negation operator (!) for this purpose.
2. you simply need to accept TCP traffic intended for HTTP, HTTPS and SSH — and you could drop the rest:

```bash
iptables -A INPUT -p tcp -m multiport ! --dports 22,80,443 -j DROP
```

However, you should first accept packets from established and related connections before using this rule! If you don’t, you’ll find out that you can’t use any TCP based applications. This is because legitimate TCP traffic would be dropped, too.


## Blocking invalid TCP packets with the tcp module
---------------------------------------------------
1. The tcp module has a --tcp-flags switch, and you can use it to check individual TCP flags. This switch takes in two arguments: a “mask” and a set of “compared flags”. The mask selects the flags that should be checked, while the “compared flags” selects the flags that should be set in the packet.

2. Now, say for example, you want to block Christmas tree packets. So, you need to check “all” the flags, but only FIN, PSH and URG will be set. So, you can write a rule like so:

```bash
iptables -A INPUT -p tcp -m tcp --tcp-flags ALL FIN,PSH,URG -j DROP
```

3. In addition, there are many other types of invalid packets that you could reject too. For example, a packet with SYN and FIN set is invalid. In this case, you need to only check for these flags and verify if they’re set. So, the rule would be:

```bash
iptables -A INPUT -p tcp -m tcp --tcp-flags SYN,FIN SYN,FIN -j DROP
```

4. Next, we’ll consider another kind of invalid packet — a “new” connection that doesn’t begin with a SYN. Here, you simply need to check the FIN, RST, ACK and SYN flags; however only SYN should be set. Then, you can negate this condition. Finally, you can use conntrack to verify if the connection is new. Thus, the rule is:

```bash
iptables -A INPUT -p tcp -m conntrack --ctstate NEW -m tcp ! --tcp-flags FIN,SYN,RST,ACK SYN -j DROP
```


## Limiting packets: the limit module
---------------------------------------

1. Technically, the number of tokens is the “limit-burst” value, and the rate at which you can refill it is the “limit” value.


```bash
iptables -A INPUT -p icmp -m limit --limit 1/sec --limit-burst 1 -j ACCEPT
```

As long as the traffic is within the given limits, packets will be accepted. However, as soon as the flow of packets exceed this limit, the traffic passes through this rule over to the other rules. Thus, you should set a default policy of DROP on the INPUT chain for this to work.


## Per-IP packet limits: the recent module
-----------------------------------------------

1. Usually, attackers try to make many connections to speed up their attack. So, you can place a per-IP restriction like so, which will slow down the attackers:

```bash
iptables -A INPUT -p tcp -m tcp --dport 22 -m conntrack --ctstate NEW -m recent --set --name SSHLIMIT --rsource
iptables -A INPUT -p tcp -m tcp --dport 22 -m conntrack --ctstate NEW -m recent --set --name SSHLIMIT --update --seconds 180 --hitcount 5 --name SSH --rsource -j DROP
```

2. We’ve set a name for the limit module by which it can keep track of things — in our case, it’s “SSHLIMIT”. 

3.  If the IP is already on this list, then the entry for this IP is updated. In the next line, we check whether the counter has hit the value of 5 in 180 seconds. If that’s indeed the case, we drop the packet. Thus, this allows 4 new SSH connections from an IP in 3 minutes.


## Custom chains
----------------

1. 
```bash
iptables -N ssh-rules


iptables -A ssh-rules -s 18.130.0.0/16 -j ACCEPT
iptables -A ssh-rules -s 18.11.0.0/16 -j ACCEPT
iptables -A ssh-rules -j DROP

```

2. Now, you should put a rule in the INPUT chain that refers to it:

```bash
iptables -A INPUT -p tcp -m tcp --dport 22 -j ssh-rules
```

3. Using a custom chain carries many advantages. For example, you can entirely manage this chain through a script, and you don’t have to worry about interfering with the rest of the chain.

If you want to delete this chain, you should first delete any rules that reference to it. Then, you can remove the chain with:

```bash
iptables -X ssh-rules
```


## Logging packets: the LOG target
--------------------------------------

1. it logs the nature of the packet matched in the kernel logs. The location of the log depends on the distribution, but it’s usually in `/var/log/syslog` or `/var/log/messages`.

2.  As an example, say you want to log invalid TCP packets before dropping them. You should first log the packet, and then drop it:

```bash
iptables -A INPUT -p tcp -m tcp --tcp-flags FIN,SYN FIN,SYN -j LOG
iptables -A INPUT -p tcp -m tcp --tcp-flags FIN,SYN FIN,SYN -j DROP
```

3. The LOG target also takes a --log-prefix option, and you can use this so that you can search the log easily later:

```bash
iptables -A INPUT -p tcp -m tcp --tcp-flags FIN,SYN FIN,SYN -j LOG --log-prefix=iptables:
```


## iptables-save and iptables-restore
-------------------------------------

1. These commands dump rules from all chains and filters into standard output. You can redirect it to a file like so:


```bash
iptables-save > iptables.rules
```

2. Now, you can edit this file comfortably with a text editor. When you’re done, you can apply these rules with:

```bash
iptables-restore < iptables.rules
```


## Preserving iptables rules across reboots
--------------------------------------------

1. it turns out that iptables rules aren’t persistent — they’re lost when you reboot your system. Solution->


```bash
sudo apt install iptables-persistent

```

2. Internally, both of these packages run the iptables-save/restore commands to save iptables configuration to a file.

3. If your distribution doesn’t have a similar package, you can simply write a service file that loads iptables rules from a file when it starts up, and saves it when it stops.
