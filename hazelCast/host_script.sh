#!/bin/bash

echo "Running script for host-${1}"


self_ip="192.168.1.${1}"
self_port=8080
ctrl_ip=192.168.1.254
ctrl_port=6666

echo "my ip: ${self_ip}"
echo "Listening on port: ${self_port}"





nc -k -l $self_ip $self_port | while read COMMAND; do
	echo $COMMAND
done
