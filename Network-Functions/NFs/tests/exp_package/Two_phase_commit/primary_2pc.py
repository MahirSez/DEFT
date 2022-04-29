from typing import List
import xmlrpc.client
from dataclasses import dataclass, field

@dataclass
class Primary:
    slaves : List[str]
    proxies: List[xmlrpc.client.ServerProxy] = field(init=False)


    def __post_init__(self):
        self.proxies = [xmlrpc.client.ServerProxy(slave) for slave in self.slaves]


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
