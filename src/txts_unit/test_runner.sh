#!/bin/bash
set -xe
packet_count=1000
run_test() {
    docker-compose down
    docker-compose up -d --build
    sleep 10
    bash net_setup.sh
    echo "rate is $1"
    SERVICE_NAME=secondary
    for id in $(docker-compose ps -q $SERVICE_NAME); do
        docker exec -d "$id" python -u secondary_test.py
    done;

    python record_time.py 0 $3
    for ((i=0;i<$2;i++))
    do
        iperf -c 127.0.0.1 -p 8080 -u -b "$1"pps -F packet_sender_data.txt -l 1400 -t 2 -x CDMSV &
    done 
    python record_time.py 1 $3
}

# clear the previous results 
rm -rf results/*
mkdir -p results

batches=(80)
buffers=(100)
pkt_rates=(2000)
flow_counts=(1)
stamper_counts=(1)
nf_count=1

for stamper_count in "${stamper_counts[@]}"; do
    for flow_count in "${flow_counts[@]}"; do
        for bs in "${batches[@]}"; do
            for (( bfs=80 ; bfs<=80 ; bfs++ )); do
                for (( pr=3000 ; pr<=3000 ; pr+=500 )); do
                    echo "Batch size = $batch_size, Buffer size = $buffer_size, Packet rate = $packet_rate, Flow Count = $flow_count"
                    
                    # replace env values in .env file
                    flow_cnt_per_nf=$((flow_count/1))
                    sed -i~ "/^BATCH_SIZE=/s/=.*/=$bs/" .env
                    sed -i~ "/^BUFFER_SIZE=/s/=.*/=$bfs/" .env
                    sed -i~ "/^PACKET_RATE=/s/=.*/=$pr/" .env
                    sed -i~ "/^STAMPER_CNT=/s/=.*/=$stamper_count/" .env
                    sed -i~ "/^FLOW_CNT_PER_NF=/s/=.*/=$flow_cnt_per_nf/" .env
                    sed -i~ "/^HZ_CLIENT_CNT=/s/=.*/=$nf_count/" .env
                     
                    filename=results/batch_"${bs}"-buf_"${bfs}"-pktrate_"${pr}"-flow_cnt_"${flow_cnt_per_nf}"-stamper_cnt_"${stamper_count}".csv
                    echo "Flow, Latency(ms), Throughput(byte/s), Throughput(pps), Packets Dropped" >> "$filename"

                    for trial in {1..1}; do
                        echo "Trial number $trial"
                        sed -i~ "/^TRIAL=/s/=.*/=$trial/" .env
                        run_test "$pr" "$flow_count" "$nf_count"
                        sleep 10
                    done
                done
            done
        done
    done
done

