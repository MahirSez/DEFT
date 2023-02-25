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
    for ((i=0;i<$2;i++))
    do
        packetsender --udp --num "$packet_count" --rate "$1" -A 127.0.0.1 8080 --file packet_sender_data.txt &
    done
    sleep 10
    
}

# clear the previous results 
rm -rf results/*
mkdir -p results

batchs=(70)
buffers=(1000)
pkt_rates=(1500)
flow_counts=(5 10)
stamper_counts=(1)

for stamper_count in "${stamper_counts[@]}"; do
    for flow_count in "${flow_counts[@]}"; do
        for batch_size in "${batchs[@]}"; do
            for buffer_size in "${buffers[@]}"; do
                for packet_rate in "${pkt_rates[@]}"; do  
                    echo "Batch size = $batch_size, Buffer size = $buffer_size, Packet rate = $packet_rate, Flow Count = $flow_count"
                    
                    # replace env values in .env file
                    flow_cnt_per_nf=$((flow_count/stamper_count))
                    sed -i~ "/^BATCH_SIZE=/s/=.*/=$batch_size/" .env
                    sed -i~ "/^BUFFER_SIZE=/s/=.*/=$buffer_size/" .env
                    sed -i~ "/^PACKET_RATE=/s/=.*/=$packet_rate/" .env
                    sed -i~ "/^STAMPER_CNT=/s/=.*/=$stamper_count/" .env
                    sed -i~ "/^FLOW_CNT_PER_NF=/s/=.*/=$flow_cnt_per_nf/" .env
                     

                    for trial in {1..5}; do
                        echo "Trial number $trial"
                        filename=results/run_"${trial}"-batch_"${batch_size}"-buf_"${buffer_size}"-pktrate_"${packet_rate}"-flow_cnt_"${flow_cnt_per_nf}"-stamper_cnt_"${stamper_count}".csv
                        echo "Flow, Latency(ms), Throughput(byte/s), Packets Dropped" >> "$filename"
                        sed -i~ "/^TRIAL=/s/=.*/=$trial/" .env
                        run_test "$packet_rate" "$flow_count" 
                    done
                done
            done
        done
    done
done

