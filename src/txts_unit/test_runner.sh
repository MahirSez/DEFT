#!/bin/bash
set -x
packet_count=1000
run_test() {
    python kill_iperf.py --force

    docker-compose down
    docker-compose up -d
    sleep 10
    bash net_setup.sh
    echo "rate is $1"
    SERVICE_NAME=secondary
    for id in $(docker-compose ps -q $SERVICE_NAME); do
        docker exec -d "$id" python -u secondary_test.py
    done;

    iperf -c 127.0.0.1 -p 8080 -u -b "$1"pps -F packet_sender_data.txt -l 100 -t 1200 -x CDMSV -P "$2" &

    python kill_iperf.py
    
}

# clear the previous results 
rm -rf results/*
mkdir -p results

batches=(80)
buffers=(100)
# pkt_rates=(200)
flow_counts=(4)
# stamper_counts=(1 2 3 4 5)
stamper_counts=(1)

docker-compose build


for stamper_count in "${stamper_counts[@]}"; do
    for flow_count in "${flow_counts[@]}"; do
        for bs in "${batches[@]}"; do
            for (( bfs=10 ; bfs<=10 ; bfs++ )); do
                for (( pr=2500 ; pr<=2500 ; pr+=500 )); do
                    echo "Batch size = $batch_size, Buffer size = $buffer_size, Packet rate = $packet_rate, Flow Count = $flow_count"
                    
                    # replace env values in .env file
                    nf_cnt=$stamper_count
                    flow_cnt_per_nf=$((flow_count/nf_cnt))
                    sed -i~ "/^BATCH_SIZE=/s/=.*/=$bs/" .env
                    sed -i~ "/^BUFFER_SIZE=/s/=.*/=$bfs/" .env
                    sed -i~ "/^PACKET_RATE=/s/=.*/=$pr/" .env
                    sed -i~ "/^STAMPER_CNT=/s/=.*/=$stamper_count/" .env
                    sed -i~ "/^FLOW_CNT_PER_NF=/s/=.*/=$flow_cnt_per_nf/" .env
                    sed -i~ "/^HZ_CLIENT_CNT=/s/=.*/=$nf_cnt/" .env
                     
                    filename=results/batch_"${bs}"-buf_"${bfs}"-pktrate_"${pr}"-flow_cnt_"${flow_cnt_per_nf}"-stamper_cnt_"${stamper_count}".csv
                    echo "Flow, Latency(ms), Throughput(byte/s), Throughput(pps), Packets Dropped, Input Buffer Max Length, Output Buffer Max Length" >> "$filename"

                    for trial in {1..1}; do
                        echo "Trial number $trial"
                        sed -i~ "/^TRIAL=/s/=.*/=$trial/" .env
                        echo "NF count: " $nf_cnt >> time_output.txt
                        time run_test "$pr" "$flow_count" >> time_output.txt
                    done
                done
            done
        done
    done
done

