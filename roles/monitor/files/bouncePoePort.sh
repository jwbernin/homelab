#!/bin/bash

switchType=$1
switchNum=$2
portNum=$3
hostState=$4
hostStateType=$5
hostAttempt=$6

function bouncePort() {
ssh admin@${switchType}${switchNum} '(echo "enable"; echo "configure"; echo "interface 0/${portNum}"; echo "poe opemode shutdown"; echo "sleep 10"; echo "poe opmode auto"; echo "exit"; echo "exit"; echo "exit") | telnet localhost 23; exit'
}


if [[ "CRITICAL" == $hostState ]];
then
  if [[ "HARD" == $hostStateType ]];
  then
    # We're down hard, definitely bounce the port
    bouncePort $switchType $switchNum $portNum
  fi
  if [[ "SOFT" == $hostStateType ]];
  then
    # Check to make sure we're on at least the third soft alert
    if [[ "3" == $hostAttempt ]];
    then
      # Third soft alert, bounce the port
      bouncePort $switchType $switchNum $portNum
    fi
  fi
else
  # Do nothing for OK, WARNING, UNKNOWN
  pass
fi

