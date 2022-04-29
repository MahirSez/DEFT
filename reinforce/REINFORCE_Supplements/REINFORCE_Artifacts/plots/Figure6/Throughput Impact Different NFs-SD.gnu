reset
set terminal windows size 1200, 800 enhanced font ",24"
#set terminal postscript eps enhanced color font 'Helvetica,24'
#set output 'Throughput Impact Different NFs.eps'

#set terminal png size 1200, 800 enhanced font ",16"
#script_name=ARG0
#set output script_name."_fig.png"

set datafile separator comma
set key right top maxrows 3 #autotitle columnhead title 'Legend'
#set key box lt -1 lw 2
#set title 'Sched Comparison with BKPR for varying flows with 3NF Chain Homogenous Weight'
set ylabel 'Throughput in Mpps'
#set xlabel 'Number of Flows'
set xtics rotate by -45 offset 0,0.25  font ",21"

set style data histogram
set style histogram cluster errorbars gap 2 lw 1.6
set style fill solid 1.0 border -1
set boxwidth 0.85
set xtic scale 0
unset log y
set yrange [0:17]
set ytics (0, 2, 4, 6, 8, 10, 12, 14, 16) nomirror
#percentage(x) = x*100


plot newhistogram lt 6, \
'ThroughputImpactforDiffNFs.csv' using 2:($2-$3):($2+$3):xtic(1) ti "Baseline" fs pattern 4, '' u 4:($4-$5):($4+$5) ti "Local Replication" fs pattern 5 lc 1, '' u 6:($6-$7):($6+$7) ti "Remote  Replication" fs pattern 2, \
#