#!/bin/bash

use=`/usr/bin/sqlite3 /var/lib/groves/watermeter-1547149398.sql 'select last_difference from byhour order by id desc limit 1;'`

let "usage = $use / 10"

if (( $usage <= 50 )); then
	echo "OK - Water usage $usage gallons"
elif (( $usage <= 80 )); then
	echo "WARNING - Water usage $usage gallons"
else
	echo "CRITICAL - Water usage $usage gallons"
fi

