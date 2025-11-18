#!/usr/bin/python3

import subprocess
import pprint
import json
import sys
import sqlite3
import datetime
import pytz
import statistics

grovehost = sys.argv[1]
sensorPoint = sys.argv[2]
timeframe = sys.argv[3]

today = datetime.datetime.now(pytz.timezone("America/New_York"))
if 'hour' == timeframe:
  sys.exit(1)
elif 'day' == timeframe:
  timedelta = datetime.timedelta(days=1)
elif 'week' == timeframe:
  timedelta = datetime.timedelta(days=7)
elif 'month' == timeframe:
  timedelta = datetime.timedelta(months=1)
else:
  sys.exit(2)

measuretime = today - timedelta

year = measuretime.year
month = measuretime.month
day = measuretime.day
hour = measuretime.hour
week = measuretime.isocalendar()[1]

print (today)
print ("DEBUG - got time(s), going to get reading")

def getDBConn(filename):
  myconn = sqlite3.connect("/var/lib/groves/{}.sql".format(filename))
  return myconn

def getData(dbconn, timeframe):
  toRet = []
  if 'day' == timeframe:
    query = "select reading from {}byhour where year = {} and month = {} and day = {}".format(sensorPoint, year, month, day)
  elif 'week' == timeframe:
    query = "select reading from {}byhour where year = {} and week = {}".format(sensorPoint, year, week)
  elif 'month' == timeframe:
    query = "select reading from {}byhour where year = {} and month= {}".format(sensorPoint, year, month)

  curs = dbconn.cursor()
  for row in curs.execute(query):
    toRet.append(row[0])
  conn.commit()
  return toRet

conn = getDBConn(grovehost)

values = getData(conn, timeframe)

maxVal = max(values)
minVal = min(values)
meanVal = sum(values)/len(values)
stdevVal = statistics.stdev(values)

if 'day' == timeframe:
  updateQuery = "insert into {}byday (year, month, week, day, high, low, mean, stddev) values ({}, {}, {}, {}, {}, {}, {}, {})".format(sensorPoint, year, month, week, day, maxVal, minVal, meanVal, stdevVal)
elif 'week' == timeframe:
  updateQuery = "insert into {}byweek (year, month, week, high, low, mean, stddev) values ({}, {}, {}, {}, {}, {}, {})".format(sensorPoint, year, month, week, maxVal, minVal, meanVal, stdevVal)
elif 'month' == timeframe: 
  updateQuery = "insert into {}bymonth (year, month, high, low, mean, stddev) values ({}, {}, {}, {}, {}, {})".format(sensorPoint, year, month, maxVal, minVal, meanVal, stdevVal)
else:
  sys.exit(3)

cursor = conn.cursor()
cursor.execute(updateQuery)
conn.commit()
conn.close()
#print ("Query: {}".format(updateQuery))
