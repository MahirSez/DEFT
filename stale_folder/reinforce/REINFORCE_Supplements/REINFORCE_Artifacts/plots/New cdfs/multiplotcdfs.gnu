#call 'multiplotcdf1-2.gnu' 'DPI_lat_baseline_0_gnu.csv' 'DPI_lat_res_lcl_0_gnu.csv' 'DPI_lat_res_all_0_gnu.csv'  'DPI_lat_pico_0_gnu.csv'
#call 'multiplotcdf1-2.gnu' 'Load_lat_baseline_0_gnu.csv' 'Load_lat_res_lcl_0_gnu.csv' 'Load_lat_res_all_0_gnu.csv'  'Load_lat_pico_0_gnu.csv'

#gnuplot -e "file_b='simple_fwd_histogram_baseline.csv'" "b_y=1" "file_rl='simple_fwd_histogram_res_lcl.csv'" "rl_y=1" "file_ra='simple_fwd_histogram_res_all.csv'" "ra_y=1"


reset
set terminal windows size 1200, 800 enhanced font ",24"
#set terminal postscript eps enhanced color font 'Helvetica,24'
#set terminal pdfcairo font "Gill Sans,10" dashed rounded linewidth 1 size 3.2in,1.6in
#set output 'CDF.eps'
#set output 'CdfComparison.pdf'

set multiplot layout 2,2 font ",10"
set key right bottom maxrows 4 samplen 1.5 font ",9" #autotitle columnhead
set key at 11100, 0.05
#set key box lt -1 lw 3
set bmargin 4

#set autoscale
#set border 3
set style fill solid 1.0 noborder

#fill color to box

set style line 1 lt 1 lc rgb "#B00000" lw 2 pt 1 ps 0.5 dashtype 2#red
set style line 2 lt 2 lc rgb "#0000CD" lw 2 pt 2 ps 1     #blue
set style line 3 lt 3 lc rgb "#00A000" lw 2 pt 7 ps 0.5 #green
set style line 4 lt 4 lc rgb "#F25900 " lw 2 pt 2 ps 0.2 dashtype 4 #orange
set style line 5 lt 3 lc rgb "#006400" lw 2 pt 6 ps 0.5 #darkgreen


#set key right top maxrows 1 #autotitle columnhead title 'Legend'
set xlabel "Latency time (us)" font ",10" offset 0,0.5
set ylabel "CDF" font ",10" offset 1.8
set xtics font ",10" nomirror
set ytics font ",10" nomirror
set ytics 0.2
unset log y
set logscale x 10
set yrange [0:1]
#set xrange [0:3000]
bin(x,s) = s*int(x/s)
set origin -0.1,-0.08
set size 0.63,1.1

set datafile separator ","
set title "Simple Forwarding" font ",10" offset 0,-0.6
file_b=ARG1
print "Baseline name        : ", file_b

file_rl=ARG2
print "REINFORCE name        : ", file_rl

file_ra=ARG3
print "FTMB name        : ", file_ra

file_rp=ARG4
print "Pico name        : ", file_rp


plot file_b u ($1/1000):(1./$2) smooth cumulative with l ls 2 t 'Baseline', \
     file_rl u ($1/1000):(1./$2) smooth cumulative with l ls 1 t 'REINFORCE', \
     file_ra u ($1/1000):(1./$2) smooth cumulative with l ls 3 t 'FTMB', \
     file_rp u ($1/1000):(1./$2) smooth cumulative with l ls 4 t 'Pico'


#set terminal windows size 1200, 800 enhanced font ",24"
#replot

#
#
unset ylabel
set title "Monitor" font ",10"  offset 0,-0.6
set origin 0.44,-0.08
set size 0.55,1.1


file_b=ARG5
print "Baseline name        : ", file_b

file_rl=ARG6
print "REINFORCE name        : ", file_rl

file_ra=ARG7
print "FTMB name        : ", file_ra

file_rp=ARG8
print "Pico name        : ", file_rp


plot file_b u ($1/1000):(1./$2) smooth cumulative with l ls 2 t 'Baseline', \
     file_rl u ($1/1000):(1./$2) smooth cumulative with l ls 1 t 'REINFORCE', \
     file_ra u ($1/1000):(1./$2) smooth cumulative with l ls 3 t 'FTMB', \
     file_rp u ($1/1000):(1./$2) smooth cumulative with l ls 4 t 'Pico'

#set terminal windows size 1200, 800 enhanced font ",24"
#replot
#
#


#set terminal windows size 1200, 800 enhanced font ",24"
#replot

#
#
unset ylabel
set title "VLAN" font ",10"  offset 0,-0.6
set origin 0.44,-0.08
set size 0.55,1.1


file_b=ARG9
print "Baseline name        : ", file_b

file_rl='reinforce\QoS_lat_reinforce_0_gnu.csv' 
print "REINFORCE name        : ", file_rl

file_ra='ftmb\QoS_lat_ftmb_0_gnu.csv'  
print "FTMB name        : ", file_ra

file_rp='pico\QoS_lat_pico_0_gnu.csv'
print "Pico name        : ", file_rp


plot file_b u ($1/1000):(1./$2) smooth cumulative with l ls 2 t 'Baseline', \
     file_rl u ($1/1000):(1./$2) smooth cumulative with l ls 1 t 'REINFORCE', \
     file_ra u ($1/1000):(1./$2) smooth cumulative with l ls 3 t 'FTMB', \
     file_rp u ($1/1000):(1./$2) smooth cumulative with l ls 4 t 'Pico'

#set terminal windows size 1200, 800 enhanced font ",24"
#replot
#
#



unset multiplot
