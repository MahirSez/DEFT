reset

#set terminal pdf size 3, 1.5 font ", 10"
set terminal pdfcairo font "Gill Sans,12" linewidth 1 size 3.2in,1.6in
set output "Plot1.pdf"        #output format

set datafile separator comma
#set style line 1 lt 1 lc rgb "#483D8B"     lw 2 pt 2 ps 0.2  #lock
#set style line 2 lt 1 lc rgb "#A00000"    lw 2 pt 6 ps 0.2   #ffwd
#set style line 3 lt 1 lc rgb "#228B22"     lw 2 pt 12 ps 0.2    #lock-free
#set style line 4 lt 1 lc rgb "purple"    lw 2 pt 9 ps 0.6        #opt
#set style line 5 lt 1 lc rgb "#228B22"    lw 2 pt 5 ps 0.6    #DPS
#set style line 6 lt 1 lc rgb "purple"   lw 2 pt 4 ps 0.6

set border linewidth 1.5
set style line 1 lc rgb '#0099ff' lt 1 lw 2 pt 1 ps 1.5 #
set style line 2 lc rgb '#800000' lt 2 lw 2 pt 2 ps 1.5 dt 2 #
set style line 3 lc rgb '#8e44ad' lt 3 lw 2 pt 3 ps 1.5 #
set style line 4 lc rgb '#009900' lt 4 lw 2 pt 4 ps 1.5 dt 2 #


set logscale x 2
#set yrange [1:1024]
#set ytics 4
#set key vertical maxrows 3
#set key samplen 1.5 spacing 0.8
#set key width -6
#set key at 48,900
set key top right
set xlabel "Packet size in bytes" offset 0,0.5
set ylabel "Throughput (MPPS)" offset 1.8,0
set ytics auto nomirror
set xtics (1,64,128,256,512,1024,1500) nomirror
set xrange [32:2048]


plot 'Plot1.csv' using 1:2 ti "Baseline Mon" with linespoints ls 1, \
     '' using 1:3 ti "Reinforce Mon" with linespoints ls 2, \
     '' using 1:4 ti "Baseline DPI" with linespoints ls 3, \
     '' using 1:5 ti "Reinforce DPI" with linespoints ls 4
     

