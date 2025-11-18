#!/usr/bin/python3

import subprocess
import pprint
import json
import sys
import sqlite3
import datetime
import pytz

grovehost = sys.argv[1]
sensorPoint = sys.argv[2]
timeframe = sys.argv[3]

today = datetime.datetime.now(pytz.timezone("America/New_York"))
if 'hour' == timeframe:
  timedelta = datetime.timedelta(hours=1)
else:
  timedelta = datetime.timedelta(days=1)
measuretime = today

year = measuretime.year
month = measuretime.month
day = measuretime.day
hour = measuretime.hour
week = measuretime.isocalendar()[1]

print (today)
print ("DEBUG - got time(s), going to get reading")

myproc = subprocess.check_output(
    "/usr/bin/ssh pi@{} /usr/local/bin/get{}.py".format(grovehost, sensorPoint),
    shell=True)

data = myproc.strip().decode("utf-8")

def getDBConn(filename):
  myconn = sqlite3.connect("/var/lib/groves/{}.sql".format(filename))
  return myconn

conn = getDBConn(grovehost)

print ("DEBUG - got connection")

if 'hour' == timeframe:
  updateQuery = "insert into {}byhour (year, month, week, day, hour, reading) values ({}, {}, {}, {}, {}, {})".format(sensorPoint, year, month, week, day, hour, data)
elif 'day' == timeframe:
  updateQuery = "insert into {}byday (year, month, week, day, reading) values ({}, {}, {}, {}, {})".format(sensorPoint, year, month, week, day, data)
elif 'week' == timeframe:
  updateQuery = "insert into {}byweek (year, week, reading) values ({}, {}, {})".format(sensorPoint, year, week, data)
elif 'month' == timeframe:
  updateQuery = "insert into {}bymonth (year, month, reading) values ({}, {}, {})".format(sensorPoint, year, month, data)

cursor = conn.cursor()
cursor.execute(updateQuery)
conn.commit()
conn.close()
#print ("Query: {}".format(updateQuery))
