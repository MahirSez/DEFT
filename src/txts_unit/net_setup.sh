#!/bin/bash
sudo ovs-vsctl del-br ovs-br1
sudo ovs-vsctl add-br ovs-br1

HZ_CLIENT_CNT=$(grep HZ_CLIENT_CNT .env | cut -d '=' -f2)
HZ_CLIENT_IP_PATTERN=$(grep HZ_CLIENT_IP_PATTERN .env | cut -d '=' -f2)


# sudo ifconfig ovs-br1 173.16.1.1 netmask 255.255.255.0 up
sudo ifconfig ovs-br1 "${HZ_CLIENT_IP_PATTERN/$/1}" netmask 255.255.255.0 up

for ((i=1;i<=HZ_CLIENT_CNT;i++)); 
do
    client_ip=${HZ_CLIENT_IP_PATTERN/$/$((i + 1))}/24
    client_name=txts_unit_hz_client_$i
    command="sudo ovs-docker add-port ovs-br1 eth1 $client_name --ipaddress=$client_ip"
    
    echo "$command"
    $command
done

# sudo ovs-docker add-port ovs-br1 eth1 txts_unit_hz_client_1 --ipaddress=173.16.1.2/24
# sudo ovs-docker add-port ovs-br1 eth1 txts_unit_hz_client_2 --ipaddress=173.16.1.3/24
