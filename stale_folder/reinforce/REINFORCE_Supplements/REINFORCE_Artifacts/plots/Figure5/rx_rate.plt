#set terminal pdf size 3, 1.5 font ", 10"
set terminal pdfcairo font "Gill Sans,12" linewidth 1 size 3.2in,1.6in
set output "rx_rate.pdf"        #output format

set style line 1 lt 1 lc rgb "#483D8B"     lw 2 pt 2 ps 0.2  #lock
set style line 2 lt 1 lc rgb "#A00000"    lw 2 pt 6 ps 0.2   #ffwd
set style line 3 lt 1 lc rgb "#228B22"     lw 2 pt 12 ps 0.2    #lock-free
set style line 4 lt 1 lc rgb "purple"    lw 2 pt 9 ps 0.6        #opt
set style line 5 lt 1 lc rgb "#228B22"    lw 2 pt 5 ps 0.6    #DPS
set style line 6 lt 1 lc rgb "purple"   lw 2 pt 4 ps 0.6

#set logscale y 2
#set yrange [1:1024]
#set ytics 4
#set key vertical maxrows 3
#set key samplen 1.5 spacing 0.8
#set key width -6
#set key at 48,900
set key  bottom left
set xlabel "Time (s)" offset 0,0.5
set ylabel "RX Rate (GB/s)" offset 1.8,0
set ytics auto nomirror
set xtics auto nomirror

#set title "Amortized Cbuf Allocation Overhead"
plot 'rxrate.dat' using 1:($2/1000000) with lp ls 1 t 'Baseline', \
		     '' using 1:($3/1000000) with lp ls 2 t 'w/o Res', \
		     '' using 1:($4/1000000) with lp ls 3 t 'w/ Res'
