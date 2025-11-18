#!/usr/bin/python3

import subprocess
import pprint
import json
import sys
import sqlite3
import datetime
import pytz

meterid = sys.argv[1]
timeframe = sys.argv[2]

today = datetime.datetime.now(pytz.timezone("America/New_York"))
if 'hour' == timeframe:
  timedelta = datetime.timedelta(hours=1)
else:
  timedelta = datetime.timedelta(days=1)
measuretime = today - timedelta

year = measuretime.year
month = measuretime.month
day = measuretime.day
hour = measuretime.hour
week = measuretime.isocalendar()[1]

print (today)
print ("DEBUG - got time(s), going to get reading")

myproc = subprocess.check_output(
    "/usr/bin/ssh pi@meterreader.jbho.me /home/pi/read-sdr.sh {}".format(meterid),
    shell=True)

data = json.loads(myproc)['Message']

def getDBConn(meterid):
  myconn = sqlite3.connect("/var/lib/groves/watermeter-{}.sql".format(meterid))
  return myconn

def getLastReading(dbconn, period):
  cursor = dbconn.cursor()
  row = cursor.execute("select consumption from by{} order by id desc limit 1".format(period))
  results = row.fetchall()
  if len(results) > 0:
    print ("DEBUG - returning "+str(results[0][0]))
    return results[0][0]
  return 0

conn = getDBConn(meterid)

print ("DEBUG - got connection")

lastReading = getLastReading(conn, timeframe)

print ("DEBUG - got last reading")
print (lastReading)
print (type(lastReading))

if 0 == lastReading:
  lastDifference = 0
  lastReading = data['Consumption']
else:
  lastDifference = data['Consumption'] - lastReading

print ("DEBUG - got last differential")

if 'hour' == timeframe:
  updateQuery = "insert into byhour (year, month, week, day, hour, backflow, consumption, leak, leaknow, lastconsumption, last_difference) values ({}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {})".format(year, month, week, day, hour, data['BackFlow'], data['Consumption'], data['Leak'], data['LeakNow'], lastReading, lastDifference)
elif 'day' == timeframe:
  updateQuery = "insert into byday (year, month, week, day, backflow, consumption, leak, leaknow, lastconsumption, last_difference) values ({}, {}, {}, {}, {}, {}, {}, {}, {}, {})".format(year, month, week, day, data['BackFlow'], data['Consumption'], data['Leak'], data['LeakNow'], lastReading, lastDifference)
elif 'week' == timeframe:
  updateQuery = "insert into byweek (year, week, backflow, consumption, leak, leaknow, lastconsumption, last_difference) values ({}, {}, {}, {}, {}, {}, {}, {})".format(year, week, data['BackFlow'], data['Consumption'], data['Leak'], data['LeakNow'], lastReading, lastDifference)
elif 'month' == timeframe:
  updateQuery = "insert into bymonth (year, month, backflow, consumption, leak, leaknow, lastconsumption, last_difference) values ({}, {}, {}, {}, {}, {}, {}, {})".format(year, month, data['BackFlow'], data['Consumption'], data['Leak'], data['LeakNow'], lastReading, lastDifference)

cursor = conn.cursor()
cursor.execute(updateQuery)
conn.commit()
conn.close()
#print ("Query: {}".format(updateQuery))
