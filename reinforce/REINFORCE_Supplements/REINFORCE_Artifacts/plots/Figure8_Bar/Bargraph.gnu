reset
#set terminal windows size 1200, 800 enhanced font ",24"
#set terminal postscript eps enhanced color font 'Helvetica,24'
set terminal pdfcairo font "Gill Sans,12" linewidth 1 size 3.2in,1.6in
set output 'Bargraph.pdf'

set datafile separator comma
#set key top center maxrows 2 width -3 #autotitle columnhead title 'Legend'


set style line 1 lc rgb 'grey30' ps 0 lt 1 lw 2
set style line 2 lc rgb 'grey70' lt 1 lw 2
set style fill solid 1.0 border rgb 'grey30'

set border 3
set xtics nomirror scale 0
set ytics auto nomirror

set boxwidth 1
set style fill solid 1.0 border -1
set border 3



plot 'Bargraph.csv' u 1:xtic(0) w boxes ls 1, \