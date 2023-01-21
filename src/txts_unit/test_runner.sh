#!/bin/bash
set -xe
packet_count=1000

run_test() {
    docker-compose down
    docker-compose up -d --build
    sleep 10
    bash net_setup.sh
    echo "rate is $1"
    # sudo packetsender --udp --num "$packet_count" --rate "$1" -A 127.0.0.1 8080 "Hello World!"
    packetsender --udp --num "$packet_count" --rate "$1" -A 127.0.0.1 8080 --file packet_sender_data.txt
}

# clear the previous results 
# rm -rf results/*

batchs=(10)
buffers=(30)
pkt_rates=(100 200 500 1000)

for batch_size in "${batchs[@]}"; do
    for buffer_size in "${buffers[@]}"; do
        for packet_rate in "${pkt_rates[@]}"; do  
            echo "Batch size = $batch_size, Buffer size = $buffer_size, Packet rate = $packet_rate"
            
            # replace env values in .env file
            sed -i~ "/^BATCH_SIZE=/s/=.*/=$batch_size/" .env
            sed -i~ "/^BUFFER_SIZE=/s/=.*/=$buffer_size/" .env
            sed -i~ "/^PACKET_RATE=/s/=.*/=$packet_rate/" .env
            
            touch results/batch_"${batch_size}"-buf_"${buffer_size}"-pktrate_"${packet_rate}".csv
            echo "Latency(ms), Throughput(byte/s), Packets Dropped" >> "results/batch_${batch_size}-buf_${buffer_size}-pktrate_${packet_rate}.csv"

            for trial in {1..5}; do
                echo "Trial number $trial"
                run_test "$packet_rate"
            done
        done
    done
done


