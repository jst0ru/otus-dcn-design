#!/bin/bash
EVE_IP="127.0.0.1"
#ports=$(sudo netstat -lnpt 2>/dev/null | awk '/qemu/ && /LISTEN/ {print $4}' | awk -F: '{print $NF}' | sort -n)
ports=$(sudo netstat -lnpt 2>/dev/null|grep qemu|grep LISTEN|tr ':' ' '|awk '{print $4}'|sort -n)
echo found ports $ports
echo ""
for p in $ports; do
  echo "checking port $p"
  start=$(date +%s%3N)
  output=$(
    {
      sleep 0.2
      echo "admin"
      sleep 0.2
      echo ""
      sleep 0.2
      echo "show hostname"
      sleep 0.2
      echo "exit"
    } | timeout 7 telnet $EVE_IP $p 2>/dev/null
  )
#  output=$( (echo; sleep 1; echo "show hostname"; sleep 1; ) | timeout 5 telnet $EVE_IP $p 2>/dev/null )
  end=$(date +%s%3N)
  elapsed=$((end-start))
#  echo $output|tr '\r' '\n'
  hostname=$(echo "$output"|tr '\r' '\n'|grep 'Hostname:'|head -1|awk '{print $2}')
  if [ -z "$hostname" ]; then
    hostname="not found"
    echo $output|tr '\r' ' '
  fi
  echo "port $p hostname $hostname time ${elapsed}"
  echo
done
