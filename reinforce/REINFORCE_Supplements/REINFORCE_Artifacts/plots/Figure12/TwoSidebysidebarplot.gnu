reset
#set terminal windows size 1200, 800 enhanced font ",24"
#set terminal postscript eps enhanced color font 'Helvetica,24'
set terminal pdfcairo font "Gill Sans,12" dashed rounded linewidth 1 size 4.6in,2in
set output 'TwoSidebysidebarplot.pdf'

set datafile separator comma

set multiplot layout 1,2 font ",10"
set key top center samplen 1.5 maxrows 2 height -1 font ",9" #autotitle columnhead
#set key at 11100, 0.05
#set key box lt -1 lw 3
set bmargin 4

set xtics rotate by -45 offset 0,0.25
set ytics nomirror
set yrange [0:3]
set ytics 0.5

set ylabel 'Throughput in Mpps'

set title "Throughput"
set style data histogram
set style histogram cluster errorbars gap 2 lw 1.6
set style fill solid 1.0 border -1
set boxwidth 1
set xtic scale 0

plot newhistogram lt 6, \
'TwoSidebysidebarplot.csv' using 2:3:4:xtic(1) ti "Bar1 first Col" fs pattern 6 lc 3, '' u 5:6:7 ti "Bar1 Sec Col" fs pattern 7 lc 1, '' u 8:9:10 ti "Bar1 Third Col" fs pattern 1 lc 2, \

#
#
set title "Latency" 
set style data histogram
set style histogram cluster errorbars gap 2 lw 1.6
#set style fill solid 1.0 border -1
set boxwidth 1
set ylabel 'Latency in ms' 

plot newhistogram lt 6, \
'TwoSidebysidebarplot.csv' using 11:12:13:xtic(1) ti "Bar2 first Col" fs pattern 6 lc 3, '' u 14:15:16 ti "Bar2 Sec Col" fs pattern 7 lc 1, '' u 17:18:19 ti "Bar2 Third Col" fs pattern 1 lc 2, \
#

unset multiplot