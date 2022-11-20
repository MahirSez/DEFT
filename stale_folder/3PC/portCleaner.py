import os

portsToCheck = [55550,55551,55552,55553,55554]

for port in portsToCheck:
    query = "fuser " + str(port) + "/tcp"
    result = os.popen(query).read()
    if len(result) > 0:
        query = "kill -9 " + str(int(result.strip()))
        print os.popen(query).read()
