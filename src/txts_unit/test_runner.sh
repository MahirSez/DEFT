#!/bin/bash
# set -xe

run_test() {
    docker-compose down
    docker-compose up -d --build
    sleep 30
    bash net_setup.sh
    packetsender --num 1000 --rate "$1" -A 127.0.0.1 8080 "hello"
}

# clear the previous results 
rm results/*

batchs=(10)
buffers=(30)
pkt_rates=(50 100)

for batch_size in ${batchs[*]}; do
    for buffer_size in ${buffers[*]}; do
        for packet_rate in ${pkt_rates[*]}; do    
            echo $batch_size $buffer_size $packet_rate
            
            # replace env values in .env file
            sed -i~ "/^BATCH_SIZE=/s/=.*/=$batch_size/" .env
            sed -i~ "/^BUFFER_SIZE=/s/=.*/=$buffer_size/" .env
            sed -i~ "/^PACKET_RATE=/s/=.*/=$packet_rate/" .env
            
            touch results/batch_${batch_size}-buf_${buffer_size}-pktrate_${packet_rate}.csv
            echo "Latency(ms), Throughput(byte/s), Packets Dropped" >> results/batch_${batch_size}-buf_${buffer_size}-pktrate_${packet_rate}.csv

            run_test $packet_rate
        done
    done
done


