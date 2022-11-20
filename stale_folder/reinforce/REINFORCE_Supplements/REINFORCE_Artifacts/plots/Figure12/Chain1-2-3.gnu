reset
#set terminal windows size 1200, 800 enhanced font ",24"
#set terminal postscript eps enhanced color font 'Helvetica,24'
set terminal pdfcairo font "Gill Sans,12" linewidth 1 size 3.2in,1.6in
set output 'Chain1-2-3.pdf'

set datafile separator comma
set key top center maxrows 2 width -3 #autotitle columnhead title 'Legend'
#set key at 0.5,95 spacing 0.85

set ylabel 'Throughput (Mpps)' offset 2.2
#set xtics rotate by -10 offset -2,0.05  font ",21"

set style data histogram
set style histogram cluster errorbars gap 2 lw 1.6
set style fill solid 1.0 border -1
set boxwidth 1
set xtic scale 0
set yrange [0:19]
set ytics (0, 2, 4, 6, 8, 10, 12, 14) nomirror
unset log y
#set ytics auto nomirror


plot newhistogram, \
'Chain1-2-3.csv' using 2:($2-$3):($2+$3):xtic(1) ti "Baseline" fs pattern 6 lc 3, '' u 4:($4-$5):($4+$5) ti "REINFORCE" fs pattern 7 lc 1, '' u 6:($6-$7):($6+$7) ti "FTMB" fs pattern 1  lc 2, '' u 8:($8-$9):($8+$9) ti "Pico*" fs pattern 2 lc 8, \
