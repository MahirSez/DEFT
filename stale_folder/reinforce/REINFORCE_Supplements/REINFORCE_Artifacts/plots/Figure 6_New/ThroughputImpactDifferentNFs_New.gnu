reset
#set terminal windows size 1200, 800 enhanced font ",24"
#set terminal postscript eps enhanced color font 'Helvetica,24'
set terminal pdfcairo font "Gill Sans,12" linewidth 1 size 3.2in,1.6in
set output 'ThroughputImpactDifferentNFs.pdf'

#set terminal png size 1200, 800 enhanced font ",16"
#script_name=ARG0
#set output script_name."_fig.png"

set datafile separator comma
set key center top maxrows 3 font ",10" #autotitle columnhead title 'Legend'
#set key at 2,90 spacing 0.85
#set key box lt -1 lw 2
#set title 'Sched Comparison with BKPR for varying flows with 3NF Chain Homogenous Weight'
set ylabel 'Throughput (Mpps)' offset 2.2
#set xlabel offset 3
set xtics offset 0,0.5 font ",10"
set bmargin 1.5
#rotate by -15 offset 0,1
set ytics auto nomirror

set style data histogram
set style histogram cluster errorbars gap 2 lw 1.6
set style fill solid 1.0 border -1
set boxwidth 0.9
set xtic scale 0
unset log y
set yrange [0:20]
set ytics (0, 2, 4, 6, 8, 10, 12, 14, 16) nomirror
#percentage(x) = x*100


plot newhistogram lt 6, \
'ThroughputImpactforDiffNFs_New.csv' using 2:($2-$3):($2+$3):xtic(1) ti "Baseline" fs pattern 6 lc 3, '' u 4:($4-$5):($4+$5) ti "REINFORCE" fs pattern 7 lc 1, '' u 6:($6-$7):($6+$7) ti "FTMB" fs pattern 1  lc 2, '' u 8:($8-$9):($8+$9) ti "Pico*" fs pattern 2 lc 8, \
#
