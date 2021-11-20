#!/bin/bash

echo "Running script for host-${1}"


self_ip="192.168.1.${1}"
self_port=8080
ctrl_ip=192.168.1.254
ctrl_port=6666

echo "my ip: ${self_ip}"
echo "Listening on port: ${self_port}"

# COMMAND=192.168.1.1_packet_count
# count=1
# echo -n "${COMMAND}: ${count}"

# echo $COMMAND
# count=$(redis-cli get $COMMAND)
# echo "${COMMAND} ${count}"


# for i in {1..100}
# do
# 	echo 'doing'

# 	echo -n 'lol ok' | nc $ctrl_ip $ctrl_port
# 	echo 'done'
# done




nc -lk $self_ip $self_port | while read COMMAND; do
	echo $COMMAND
	count=$(redis-cli -h 192.168.1.1 -p 6379 get "${COMMAND}")
	echo -n "${COMMAND} ${count}" | nc $ctrl_ip $ctrl_port 
done


# nc 192.168.1.254 6666 <server_listener.sh