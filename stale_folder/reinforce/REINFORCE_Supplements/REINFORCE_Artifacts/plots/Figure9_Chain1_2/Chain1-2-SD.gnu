set terminal windows size 1200, 800 enhanced font ",22"
#set terminal postscript eps enhanced color font 'Helvetica,22'
#set output 'Chain1-2.eps'

set datafile separator comma
set key left top maxrows 2 #autotitle columnhead title 'Legend'
set ylabel 'Throughput in Mpps'

set style data histogram
set style histogram cluster errorbars gap 2 lw 1.6
set style fill solid 1.0 border -1
set boxwidth 1
set xtic scale 0
set yrange [0:10]
set ytics (0, 1, 2, 3, 4, 5, 6, 7, 8, 9) nomirror


plot newhistogram, \
'Chain1-2.csv' using 2:($2-$3):($2+$3):xtic(1) ti "Baseline" fs pattern 6, '' u 4:($4-$5):($4+$5) ti "Local Replication" fs pattern 7, '' u 6:($6-$7):($6+$7) ti "Remote Replication" fs pattern 9

     
     