#!/bin/bash

#Looks for adb device, uses adb shell to switch USB mode, waits for adb to disconnect, then checks for new network with ip 192.168.42.XXX
#Static ip not used as tested Honor 8 changes mac address each restart, so Linux detects a new network

while true;
do
	devs="$(adb devices)"
	#echo $devs
	tmp=${devs#*CSTDU}   # remove prefix ending in "CSTDU"
	#echo $tmp
	echo "Waiting for phone ADB"
	if [ "$tmp" == "$devs" ]
	then
		echo "Connect phone, or reconnect"
		sleep 0.5s
	else
		break
	fi
done

echo "ADB device connected"
#echo "Wait 15 seconds"
#sleep 15s

while true;
do
	adb shell su -c service call connectivity 33 i32 1 s16 text
	adb="$(adb devices)"
	#echo $adb
	tmp=${adb#*wrong}   # remove prefix ending in "wrong"
	#echo "$tmp
	if [ "$tmp" == "$adb" ]
	then
		sleep 0.5s
	else
		break
	fi
done

echo "ADB disconnected, good"

while true;
do
	ips="$(hostname -I)"
	#echo $ips
	tmp=${ips#*192.168.42}   # remove prefix ending in "192.168.42."
	#echo $tmp
	echo "Checking ip addresses"
	if [ "$tmp" == "$ips" ]
	then
		echo "Phone network not found"
		sleep 0.5s
	else
		break
	fi
done

ip=192.168.42$tmp
echo "My ip on phone network is: "$ip
