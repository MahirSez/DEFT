reset
#set terminal windows size 1200, 800 enhanced font ",24"
#set term pdf enhanced color font "Times-Roman, 11" size 4in,1.5in
set terminal pdfcairo font "Gill Sans,12" linewidth 1.5 size 3.2in,1.6in

set output "ResIsolation.pdf"        #output format

#set output 'candlesticks.png'
set boxwidth 0.2 absolute
set key center top maxrows 1 #autotitle columnhead title 'Legend'
#set title "Monitor NF"

set ytics auto nomirror
set xrange[0:3]
set yrange[0:1800]
set ytics 300 offset 0.2
#set log y 10
set ylabel "Latency ({/Symbol m}s)" offset 1.8
set xtics scale 0
#set xtics rotate by -45
set xtics offset 0, screen 0.13



# Data columns: X Min 1stQuartile Median 3rdQuartile Max BoxWidth Titles

# set bars 4.0
set style fill empty
plot 'candle.dat' using 1:3:2:6:5:7:xticlabels(8) with candlesticks lt 2 lw 3 notitle whiskerbars, \
  ''         using 1:4:4:4:4:7 with candlesticks lt -1 lw 1 notitle
