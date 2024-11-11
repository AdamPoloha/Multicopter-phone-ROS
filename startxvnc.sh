#!/bin/bash

RED='\033[0;31m'
NC='\033[0m'

echo -e "${RED}\nStopping Xvfb\n${NC}"
pid=`ps aux | grep 'Xvfb' | grep '0x' | awk '{print $2}'`
echo $pid
kill $pid
pid=`ps aux | grep '\-lock' | awk '{print $2}'`
kill $pid
sleep 5
rm /tmp/.X0-lock
rm /tmp/.X11-unix/*
echo -e "${RED}\nLock gone\n${NC}"
sleep 1
export DISPLAY=:0
Xvfb -ac $DISPLAY -screen 0 1920x1080x16 &
echo -e "${RED}\nVirtual X display\n${NC}"
sleep 2
startxfce4 &
echo -e "${RED}\nXFCE\n${NC}"
sleep 10
echo -e "${RED}\nXFCE Started\n${NC}"
#sleep 30
x11vnc -display $DISPLAY -nopw -forever -loop -noxdamage -repeat -rfbport 5900 -shared -noshm -ncache 10
