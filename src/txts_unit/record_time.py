import redis
import sys
import time

redis_client = redis.Redis(host="localhost", port=6378, db=5)

flag = int(sys.argv[1])
nf_cnt = int(sys.argv[2])

TIME_KEY = "TIME"
NF_COMPLETE_KEY = "NF_COMPLETE"


def get_current_time_in_ms():
    return time.time_ns() / 1_000_000

if flag == 0:
    redis_client.set(TIME_KEY, get_current_time_in_ms())
else:
    while True:
        complete_nf_cnt = redis_client.get(NF_COMPLETE_KEY)
        if complete_nf_cnt and int(complete_nf_cnt) == nf_cnt:
            break

    start_time = float(redis_client.get(TIME_KEY))
    end_time = get_current_time_in_ms()
    mid_time = (start_time + end_time) / 2

    total_delay = 0

    for key in redis_client.keys():
        if str(key) in [TIME_KEY, NF_COMPLETE_KEY]:
            continue
        timestamp = float(redis_client.get(key))
        delay = timestamp - mid_time
        total_delay += delay

    print("total delay ", total_delay)
    key_cnt = len(redis_client.keys()) - 2
    print("avg delay ", total_delay/key_cnt)



