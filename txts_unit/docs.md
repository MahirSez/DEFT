
1. sudo ovs-ofctl dump-flows s1
2. sudo ovs-ofctl del-flows s1
3.  ../pox/pox.py log.level --DEBUG ft_net.multiSwitchController
4. sudo mn --custom multi_switch_topo.py --topo multiSwitch,7 --mac --controller remote --switch ovsk
5. source venv/bin/activate
6. python stamperScript.py
7. python hostScript.py


Instructions
-----------------------------

1. Open 2 terminals in folder `FT-Net/txts_unit` and activate venv with `source venv/bin/activate`

2. Run pox controller in 2nd terminal:
	`../pox/pox.py log.level --DEBUG ft_net.multiSwitchController`

3. create mininet in 1st terminal topology with the command:
	`sudo mn --custom multi_switch_topo.py --topo multiSwitch,7 --mac --controller remote --switch ovsk`

4. In mininet CLI open stamper, h1 and h2 with `xterm h1 h2 stamper` and activate venv with `source venv/bin/activate`

5. In stamper's terminal run: `python stamperScript.py`

6. In h1 and h2's terminal run: `python hostScript.py`

7. In mininet CLI run: `client ping h1 -c10`

Packets will be bypassed through stamper where the packets will be assigned an id.
Packets received by h1 will also reflect in h2

