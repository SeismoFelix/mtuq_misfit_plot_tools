#!/bin/sh
################################################################
#Script for plotting the focal mechanisms Uncertainties. The X and Y axis could be strike, dip or rake.
#Felix Rodriguez Cardozo
#May 12th 2022
##psmeca_file_dip_strike_surface_slip.txt
#gmt makecpt -T3.8471359451573206e-09/1.0003204348985174e-08/0.1e-09 -Crainbow  > misfit1.cpt
#gmt makecpt -T3.8471359451573206e-09/9.994456999898963e-09/0.1e-09 -Crainbow  > misfit2.cpt
#gmt makecpt -T3.8471359451573206e-09/7.975461338251326e-09/0.1e-09 -Crainbow  > misfit3.cpt
##Making surface plot for x_axis:dip, y_axis:strike and  slip free
#4.8471359451573206e-09
#1.0003204348985174e-08
##Making surface plot for x_axis:slip, y_axis:strike and  dip free
#4.8471359451573206e-09
#9.194456999898963e-09
##Making surface plot for x_axis:slip, y_axis:dip and  strike free
#4.8471359451573206e-09
#7.775461338251326e-09

PSFILE=uncertainties3.ps
COLOR1=color_misfit_dip_strike_surface_slip.txt
COLOR2=color_misfit_slip_strike_surface_dip.txt
COLOR3=color_misfit_slip_dip_surface_strike.txt
FOCMEC1=psmeca_file_dip_strike_surface_slip.txt
FOCMEC2=psmeca_file_slip_strike_surface_dip.txt
FOCMEC3=psmeca_file_slip_dip_surface_strike.txt
REGION1=0/90/0/360 #-JX10i/7i
REGION2=-90/90/0/360
REGION3=-90/90/0/90

gmt psbasemap -R$REGION3 -JX10i/7i -Bx10.0 -Bya10.0 -BWeSn -K -V >> $PSFILE
gmt psxy $COLOR3 -R -J -O -Wthin -Sc0.4 -V -Cmisfit3.cpt -K >> $PSFILE
gmt psmeca $FOCMEC3 -G255/0/0 -R -T100 -J -Sa0.4 -C -h1 -O -V >> $PSFILE
gmt psconvert $PSFILE -Tf -P
