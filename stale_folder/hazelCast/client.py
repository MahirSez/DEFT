import logging
import time
import os

import hazelcast

logging.basicConfig(level=logging.INFO)

# Connect to Hazelcast cluster.
client = hazelcast.HazelcastClient(
	cluster_members=[
		"10.0.0.1:5701"
	],
)

print("PYTHON: HazelCast client connected")
pn_counter = client.get_pn_counter("pn-counter").blocking()
print("Counter is initialized with", pn_counter.get())

logfile = open("prads.log", "r")
logfile.seek(0, os.SEEK_END)

while True:
	line = logfile.readline()
	if line:
		print("PYTHON: " + line)
		print("PYTHON: Current value after inc. " + str(pn_counter.add_and_get(1)))
	else:
		time.sleep(0.1)
# Shutdown the client.
client.shutdown()
