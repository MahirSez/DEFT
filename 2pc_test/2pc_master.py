import xmlrpc.client

slaves = ['http://10.0.0.2:8000/']


def replicate(backup, states):
    proxy = xmlrpc.client.ServerProxy(backup)
    multicall = xmlrpc.client.MultiCall(proxy)

    multicall.update_state(states)

    results = multicall()
    for result in results:
        print(result)


def master():
    for slave in slaves:
        replicate(slave)
