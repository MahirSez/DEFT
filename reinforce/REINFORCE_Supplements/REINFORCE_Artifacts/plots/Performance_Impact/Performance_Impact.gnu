reset
#set terminal windows size 1200, 800 enhanced font ",16"
set terminal pdfcairo font "Gill Sans,12" linewidth 1 size 3.2in,1.8in
set output "Performance_Impact.pdf"        #output format


set datafile separator comma
set key center top maxrows 2 spacing 1 samplen 1.5 height -1 #autotitle columnhead 

#set title "Performance Impact due to increasing shared variables"
set ylabel 'Throughput in MPPS' offset 2
set xlabel 'Num. of shared variables' offset 0,1
set xtics scale 0
#set tmargin 2
#set bmargin 2.5 

#set xrange [0:15]
set xtics (0,2,4,6,8,10) offset 0,0.5 nomirror
unset logscale y
set yrange [0:20]
#set y2range [0:*]
#set y2tics font ",22" nomirror
set ytics (0,2,4,6,8,10,12,14,16) nomirror


#color definitions
set border linewidth 1.5
set style line 1 lc rgb '#009900' lt 1 lw 2 pt 1 ps 1.5 dt 5 #
set style line 2 lc rgb '#B00000' lt 2 lw 2 pt 2 ps 1.5 dt 2 #
set style line 3 lc rgb '#0000CD' lt 3 lw 2 pt 3 ps 1.5 #
set style line 4 lc rgb '#F25900' lt 4 lw 2 pt 4 ps 1.5 dt 4 #

plot 'Performance_Impact.csv' using 1:4 ti "BASELINE" with linespoints ls 3, \
     '' using 1:3 ti "REINFORCE" with linespoints ls 2, \
     '' using 1:2 ti "FTMB" with linespoints ls 1, \
     '' using 1:5 ti "PICO" with linespoints ls 4
 
#plot 'Performance_Impact.csv' using 1:2 ti "FTMB" with linespoints ls 1, \
#     '' using 1:3 ti "REINFORCE" with linespoints ls 2, \
#     '' using 1:4 ti "BASELINE" with linespoints ls 3, \
#     '' using 1:5 ti "PICO" with linespoints ls 4 

