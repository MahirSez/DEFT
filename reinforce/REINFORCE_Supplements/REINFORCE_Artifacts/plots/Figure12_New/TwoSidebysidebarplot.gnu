reset
#set terminal windows size 1200,800 font ",24"
#set terminal postscript eps enhanced color font 'Helvetica,24'
#set terminal png enhanced color font 'Helvetica,24'
set terminal pdfcairo font "Gill Sans,11" linewidth 1.2 size 3.2in,1.6in
set output 'TwoSidebysidebarplot.pdf'

set datafile separator comma
#set xlabel 'Buffer Size' offset 0,0.3
set ylabel 'Throughput in Mpps' offset 1.2
set y2label 'Latency in ms' offset -1.2

#set key left top maxrows 2 width 1 font ",10"
set key top center samplen 1.5 maxrows 2 height -1 font ",10" #autotitle columnhead
#set key center out vert maxrows 1 width 1 font ",11"
#set key at -1.45,6.9 samplen 2

unset logscale y
set yrange [0:3.5]
set ytics 0.5
set style data histogram
set style histogram cluster errorbars gap 2 lw 1.6
set style fill solid 1.0 border -1
set boxwidth 1
set xtic scale 0

set xtics rotate by -45 offset 0,0.25
set ytics nomirror
set y2tics nomirror
set y2range [0:3.5]
set y2tics 0.5

# 2, 3 are the indexes of the columns; 'fc' stands for 'fillcolor'
#color definitions
#set border linewidth 1.5
set style line 1 lc 3 lt 1 lw 2 pt 9 ps 0.5 # --- green
set style line 2 lc 1 lt 1 lw 2 pt 5 ps 0.5 # --- red
set style line 3 lc 2 lt 1 lw 2 pt 3 ps 0.5 # --- blue

plot newhistogram  lt 6,\
'TwoSidebysidebarplot.csv' using 2:3:4:xtic(1) ti "TPUT 1" fs pattern 6 lc 3, '' u 5:6:7 ti "TPUT 2" fs pattern 7 lc 1, '' u 8:9:10 ti "TPUT 3" fs pattern 1 lc 2, \
'' u 11:xtic(1) ti "Latency 1" with linespoints axes x1y2 ls 1 lc 3, '' u 14 ti "Latency 2" with linespoints axes x1y2 ls 2 lc 1, '' u 17 ti "Latency 3" with linespoints axes x1y2 ls 3 lc 2, \
