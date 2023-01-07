#!/bin/bash
sudo ovs-vsctl del-br ovs-br1
sudo ovs-vsctl add-br ovs-br1
sudo ifconfig ovs-br1 173.16.1.1 netmask 255.255.255.0 up
