reset

#set terminal pdf size 3, 1.5 font ", 10"
set terminal pdfcairo font "Gill Sans,12" linewidth 1 size 3.2in,1.6in
set output "Performance_Impact.pdf"        #output format

set datafile separator comma

set border linewidth 1.5
set style line 1 lc rgb '#0099ff' lt 1 lw 2 pt 1 ps 1.5 #
set style line 2 lc rgb '#800000' lt 2 lw 2 pt 2 ps 1.5 dt 2 #
set style line 3 lc rgb '#8e44ad' lt 3 lw 2 pt 3 ps 1.5 #
set style line 4 lc rgb '#009900' lt 4 lw 2 pt 4 ps 1.5 dt 2 #
#set bmargin 0.5 

set title "Performance Impact due to increasing shared variables"
#set xtic scale 0
set key top center maxrows 2 samplen 1.5 height -1
#set xlabel "Packet size in bytes" offset 0,0.5
#set ylabel "Throughput (MPPS)" offset 1.8,0
set ytics (0,2,4,6,8,10,12,14,16) nomirror
set xtics (0,2,4,6,8,10) nomirror
#set xrange [0:10]
set yrange [0:20]


plot 'Performance_Impact.csv' using 1 ti "FTMB" with linespoints ls 1, \
     '' using 1:3 ti "REINFORCE" with linespoints ls 2, \
     '' using 1:4 ti "BASELINE" with linespoints ls 3, \
     '' using 1:5 ti "PICO" with linespoints ls 4
     

