#set terminal pdf size 3, 1.5 font ", 10"
set terminal pdfcairo font "Gill Sans,12" linewidth 1 size 3.2in,1.6in
set output "MultiTenant.pdf"        #output format

set datafile separator comma
set style line 1 lt 1 lc rgb "#483D8B"     lw 2 pt 2 ps 0.2  #lock #purple
set style line 2 lt 1 lc rgb "#A00000"    lw 2 pt 6 ps 0.2   #Maroon
set style line 3 lt 1 lc rgb "#228B22"     lw 2 pt 12 ps 0.2    #lock-free #green
set style line 4 lt 1 lc rgb "#1F4AF6"    lw 2 pt 9 ps 0.6        #opt #blue
set style line 5 lt 1 lc rgb "#228B22"    lw 2 pt 5 ps 0.6    #DPS
set style line 6 lt 1 lc rgb "#F6591F"   lw 2 pt 4 ps 0.6   #Orange

set border 11
#set logscale y 2
#set yrange [1:1024]
#set ytics 4
#set key vertical maxrows 3
#set key samplen 1.5 spacing 0.8
#set key width -6
#set key at 48,900
#set key out vert
#set key top left maxrows 2
set key samplen 1 spacing 0.75 height -1.25
set key outside horizontal center top maxrows 2

set xlabel "Time (s)" offset 0,1
set ylabel "Throughput in Mpps" offset 1.8,0
set y2label "CPU Utilization %" offset -2.5
set ytics auto nomirror
set xtics auto offset 0,0.5 nomirror
set y2tics 20 offset -1,0.3 nomirror
set y2range [0:100]

#set title "Amortized Cbuf Allocation Overhead"
plot 'All.csv' using 1:($3/1000000) with l ls 6 t 'NF1 Thrpt.', \
		     '' using 1:($4/1000000) with l ls 4 t 'NF2 Thrpt.', \
		     '' using 1:($2/1000000) with l ls 3 t 'Aggr. Thrpt.', \
             '' using 1:($5) with l axes x1y2 ls 6 lw 1.5 dt 3 t 'NF1 CPU Util %', \
             '' using 1:($6) with l axes x1y2 ls 4 lw 1.5 dt 3 t 'NF2 CPU Util %' 
