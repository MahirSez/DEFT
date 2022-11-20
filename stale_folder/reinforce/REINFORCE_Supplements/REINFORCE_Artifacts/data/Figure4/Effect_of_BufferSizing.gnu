reset

set terminal windows size 1200,800 font ",24"
#set terminal postscript eps enhanced color font 'Helvetica,24'
#set terminal png enhanced color font 'Helvetica,24'
set output 'Effect_of_BufferSizing.png'


set xlabel 'Buffer Size'
set ylabel 'Throughput in Mpps'
set y2label '99th %ile Latency (in milli seconds)'
set datafile separator comma
set key left top maxrows 1 width 1 font ",24"

unset logscale y
#set yrange [0:9]
set auto y
set auto y2
set style data histogram
set style histogram rowstacked
set style fill solid 1 border -1
set boxwidth 0.75
set ytics auto nomirror
set y2tics auto nomirror

#set xtic scale 0
#set ytic 0.5
#set ytics (0,0.5,1,1.5,2,2.5,3,3.5,4,4.5,5,5.5,6,6.5,7)

# 2, 3 are the indexes of the columns; 'fc' stands for 'fillcolor'
#color definitions
#set border linewidth 1.5
set style line 1 lc rgb '#99FF33' lt 1 lw 2 pt 7 ps 1.5 # --- green
set style line 2 lc rgb '#dd181f' lt 1 lw 2 pt 2 ps 1.5 # --- red
set style line 3 lc rgb '#0099ff' lt 1 lw 2 pt 7 ps 1.5 # --- blue

plot newhistogram,\
'Effect_of_BufferSizing.csv' using 2:xtic(1) title "Throughput" fs pattern 4 lc rgb '#0099ff', '' u 3 title "99th %ile Latency" with linespoints axes x1y2 ls 2