#!/bin/sh -xe

cd astropy_iers_data/data

rm -f finals2000A.all
rm -f eopc04.1962-now
rm -f Leap_Second.dat

# IERS_A_URL
wget https://datacenter.iers.org/data/9/finals2000A.all

# IERS_B_URL
wget https://hpiers.obspm.fr/iers/eop/eopc04/eopc04.1962-now

# IERS_LEAP_SECOND_URL
wget https://hpiers.obspm.fr/iers/bul/bulc/Leap_Second.dat
