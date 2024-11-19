#!/data/data/com.termux/files/usr/bin/sh

echo "Sending to ip: 127.0.0.1"

while true;
do
	termux-sensor -c
	termux-sensor -s "rotation Vector","geomagnetic Rotation Vector","gyroscope-lsm6ds3","accelerometer","mag-akm09911" -d 10 | nc 127.0.0.1 1234
	sleep 3s
done