from typing import List
import xmlrpc.client


class Primary:

    def __init__(self):
        self.slaves = []
        self.proxies = []

    # slaves : List[str] = field(init=False)
    # proxies: List[xmlrpc.client.ServerProxy] = field(init=False)


    def add_secondary(self, secondary_ip):
        self.slaves.append(secondary_ip)
        self.proxies.append(xmlrpc.client.ServerProxy(secondary_ip))


    @staticmethod
    def replicate_on_a_slave(slave, proxy, states):

        multicall = xmlrpc.client.MultiCall(proxy)

        # print(f"replicating states on slave {slave}")
        multicall.update_state(states)

        results = multicall()
        # for result in results:
        #     print(result)


    def replicate(self, states):
        for slave, proxy in zip(self.slaves, self.proxies):
            Primary.replicate_on_a_slave(slave=slave, proxy=proxy, states=states)
