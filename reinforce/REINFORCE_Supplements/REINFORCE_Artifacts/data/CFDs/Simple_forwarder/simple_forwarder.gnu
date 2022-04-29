#call 'simple_forwarder.gnu' 'Simple_Forwarder_lat_baseline_0_gnu.csv' 'Simple_Forwarder_lat_res_lcl_0_gnu.csv' 'Simple_Forwarder_lat_res_all_0_gnu.csv'  'Simple_Forwarder_lat_pico_0_gnu.csv'

#gnuplot -e "file_b='simple_fwd_histogram_baseline.csv'" "b_y=1" "file_rl='simple_fwd_histogram_res_lcl.csv'" "rl_y=1" "file_ra='simple_fwd_histogram_res_all.csv'" "ra_y=1"


reset
set terminal windows size 1200, 800 enhanced font ",24"
#set terminal postscript eps enhanced color font 'Helvetica,24'
#set output 'CDF.eps' 	

#set multiplot layout 2,3 font ",16"
set key left top maxrows 2 width -1.5 font ",14" #autotitle columnhead
#set key box lt -1 lw 3 
set bmargin 4

#set autoscale
#set border 3
set style fill solid 1.0 noborder                         

#fill color to box

set style line 1 lt 1 lc rgb "#B00000" lw 4 pt 1 ps 0.5 #red
set style line 2 lt 2 lc rgb "#0000CD" lw 4 pt 2 ps 0.4 #blue
set style line 3 lt 3 lc rgb "#00A000" lw 5 pt 6 ps 0.5 #green
set style line 4 lt 4 lc rgb "#f4d03f " lw 5 pt 2 ps 0.5 #orange
set style line 5 lt 3 lc rgb "#006400" lw 5 pt 6 ps 0.5 #darkgreen


#set key right top maxrows 1 #autotitle columnhead title 'Legend'
set xlabel "Latency time (us)" offset 0,0.5 font ",12"
set ylabel "CDF" offset 1.7,0 font ",14"
set xtics font ",12" nomirror
set ytics font ",12" nomirror
unset log y
set logscale x 10
#set yrange [0:1]
#set xrange [0:3000]
#set key right left                              
#set location of legend
#set key above width -7 height 0.6 vertical maxrows 2 samplen 2 
#set key font ",10"
bin(x,s) = s*int(x/s)

set datafile separator ","
set title "Simple Forwarder" font ",16"
file_b=ARG1
print "Baseline name        : ", file_b

file_rl=ARG2
print "Local name        : ", file_rl

file_ra=ARG3
print "Remote name        : ", file_ra

file_rp=ARG4
print "Pico name        : ", file_rp

plot file_b u ($1/1000):(1./$2) smooth cumulative with l ls 2 t 'Baseline', \
     file_rl u ($1/1000):(1./$2) smooth cumulative with l ls 1 t 'Local Replica', \
     file_ra u ($1/1000):(1./$2) smooth cumulative with l ls 3 t 'Remote Replica', \
     file_rp u ($1/1000):(1./$2) smooth cumulative with l ls 4 t 'Pico Replica'
     
#set terminal windows size 1200, 800 enhanced font ",24"
#replot

