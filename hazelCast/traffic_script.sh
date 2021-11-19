
ctrl_ip=192.168.1.254
ctrl_port=6666

cmd="$(echo 'ready' | netcat -q 1 $ctrl_ip $ctrl_port )"

if [ $cmd == 'start' ]
then 
	# cmd="$(echo 'overload' | netcat -q 1 $ctrl_ip $ctrl_port)"
	# echo $cmd
	tcpreplay -i h5-eth0 -p 500 capture.pcap
	# ping -c 10 10.0.0.2
fi

cmd="$(echo 'terminate' | netcat -q 1 $ctrl_ip $ctrl_port)"
