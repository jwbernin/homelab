#!/bin/bash

filterid=$1

/usr/bin/sudo /bin/systemctl restart rtlsdr

sleep 15

/home/pi/go/bin/rtlamr -format=json -msgtype=r900 -filterid=${filterid} -single=true
