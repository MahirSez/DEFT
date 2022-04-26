import xmlrpc.client

slaves = ['http://10.0.0.2:8000/']


def replicate_on_a_slave(slave, states):

    proxy = xmlrpc.client.ServerProxy(slave)
    multicall = xmlrpc.client.MultiCall(proxy)

    print(f"replicating states on slave {slave}")

    multicall.update_state(states)

    results = multicall()
    for result in results:
        print(result)


def replicate(states):
    for slave in slaves:
        replicate_on_a_slave(slave, states)
