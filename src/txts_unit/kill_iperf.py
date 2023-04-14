import redis

import os
from dotenv import load_dotenv
import redis
import subprocess
import argparse

def kill_iperf():
    print("Killing iperf")
    command = "ps aux | grep -i iperf | awk '/iperf/{print $2}' | xargs kill -9"
    subprocess.run(command, shell=True)


def wait_for_redis_cnt():
    print("Waiting for NFs to finish...")
    while True:
        complete_nf_cnt = redis_client.get(NF_DONE_KEY)
        if complete_nf_cnt and int(complete_nf_cnt) == HZ_CLIENT_CNT:
            break
    print("Waiting is over")


load_dotenv()
parser = argparse.ArgumentParser()
redis_client = redis.Redis(port=6378)

HZ_CLIENT_CNT = int(os.getenv('HZ_CLIENT_CNT'))

NF_DONE_KEY = "NF_DONE"

parser.add_argument('--force', action='store_true')
args = parser.parse_args()

if not args.force:
    wait_for_redis_cnt()
kill_iperf()






