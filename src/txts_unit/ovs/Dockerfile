# Not currently used in this project

FROM python:3.10.8

RUN apt update
RUN apt install -y openvswitch-switch
RUN apt install -y iputils-ping net-tools

RUN ovs-vsctl add-br ovs-br1
RUN ifconfig ovs-br1 173.16.1.1 netmask 255.255.255.0 up

RUN ovs-docker del-ports ovs-br1 txts_unit_hz_client1
RUN ovs-docker del-ports ovs-br1 txts_unit_hz_client2

RUN ovs-docker add-port ovs-br1 eth1 txts_unit_hz_client1 --ipaddress=173.16.1.2/24
RUN ovs-docker add-port ovs-br1 eth1 txts_unit_hz_client2 --ipaddress=173.16.1.3/24

