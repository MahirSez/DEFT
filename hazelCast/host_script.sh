
ctrl_ip=192.168.1.254
ctrl_port=6666

cmd="$(echo 'ready' | netcat -q 1 $ctrl_ip $ctrl_port )"

if [ $cmd == 'start' ]
then 
	cmd="$(echo 'overload' | netcat -q 1 $ctrl_ip $ctrl_port)"
	echo $cmd
fi

cmd="$(echo 'terminate' | netcat -q 1 $ctrl_ip $ctrl_port)"
