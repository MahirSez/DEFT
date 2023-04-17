#!/bin/bash

# source test_data_params/batch_sz_vs_pkt_rate.env

# for item in "${effective_packet_rate[@]}"
# do
#   echo $item
# done

#!/bin/bash

# Loop over all files in the results directory
for filename in results/batch_*-buf_*-pktrate_*-flow_cnt_*-stamper_cnt_*.csv; do
    # Extract the pktrate value and multiply it by 100
    # pktrate=$(echo "$filename" | sed -n 's/^results\/batch_[[:digit:]]\+-buf_[[:digit:]]\+-pktrate_\([[:digit:]]\+\)-flow_cnt_[[:digit:]]\+-stamper_cnt_[[:digit:]]\+\.csv/\1/p')
    # new_pktrate=$(printf "%d" $((pktrate)))

    # # Create the new filename with the updated pktrate
    # new_filename=$(echo "$filename" | sed "s/pktrate_${pktrate}/pktrate_${new_pktrate}/")

    # # Rename the file
    # mv "$filename" "$new_filename"

    value=$(echo $filename | sed -n 's/.*pktrate_0*\([0-9]\{1,\}\).*/\1/p')

    if [ -n "$value" ]; then
        new_value="${value}00"
        new_filename=$(echo $filename | sed "s/pktrate_0*${value}/pktrate_${new_value}/")
        mv "$filename" "$new_filename"
    fi
done

