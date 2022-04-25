import xmlrpc.client

slaves = ['http://10.0.0.2:8000/']


def replicate(backup):
    proxy = xmlrpc.client.ServerProxy(backup)
    multicall = xmlrpc.client.MultiCall(proxy)
    multicall.update_state({
        '1': 5,
        '2': 7,
        '3': 8
    })
    results = multicall()
    for result in results:
        print(result)


def master():
    for slave in slaves:
        replicate(slave)
