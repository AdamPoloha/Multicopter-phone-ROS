# Multicopter-phone-ROS

Here I will detail the whole process to get an android phone to run ROS and control a multicopter.

What you will need:
Linux
  SSH
  Remmina
Android Phone (Accelerometer, Gyroscope, and Compass)
USB Cable

I will attempt to do it without root.

Termux and ssh:
Connect your phone to your wifi network.
Enable USB debugging:
  Settings
  About phone
  Tap build number 10 times
  Go back
  Additional settings
  Developer options
  Enable USB debugging
Install Termux:
  Download F-Droid Apk (https://github.com/f-droid/fdroidclient/releases/)
  Install F-Droid:
    Open the file
    Tap Settings
    Turn on Allow apps from this source
    Go back
    Tap Install
    Tap Open
    Wait for repositories to update
  Install Apps:
    Termux Terminal
    Termux API
    Termux Boot (If it gets blocked, you can choose to install anyway)
    Termux Widget
Inside Termux:
  pkg upgrade
  pkg install openssh
  Follow ssh example (https://github.com/termux/termux-boot)
  mkdir ~/.termux/boot
  nano ~/.termux/boot/start-sshd
  Paste in: (CTRL+S and CTRL+X to save and exit)
#!/data/data/com.termux/files/usr/bin/sh
termux-wake-lock
sshd
Restart Phone
If you wish to use USB for ssh, you can try to use and modify networkifyUSB-root.sh if you have root, otherwise you need to either set Default USB configuration in Developer options to USB tethering or RNDIS, or enable it manually each time
Inside Termux:
  passwd (set password for user) [copter]
  whoami (the ouput is the phone username) [u0_a248]
  ifconfig (find ip address of phone) [192.168.121.70]
  sshd (if Termux Boot did not autostart it)
Inside Desktop Terminal:
  ssh username@ipaddress -p 8022 [ssh u0_a248@192.168.121.70 -p 8022]
  Accept the key fingerprint and type in the password set above
  If you wish to finish the session, type 'exit'

Termux Proot:
Follow guide on Termux Desktops (https://github.com/LinuxDroidMaster/Termux-Desktops)
Ubuntu Proot (https://github.com/LinuxDroidMaster/Termux-Desktops/blob/main/Documentation/proot/ubuntu_proot.md)
Ubuntu select version (https://github.com/MFDGaming/ubuntu-in-termux)
Ubuntu Base releases (http://cdimages.ubuntu.com/ubuntu-base/releases/)
XFCE install (https://github.com/LinuxDroidMaster/Termux-Desktops/blob/main/Documentation/proot/debian_proot.md#installing-desktops)
VNC (https://gist.github.com/rikka0w0/895815ab1968a1be0f80f25e66fd61f5)
Inside ssh session:
  pkg update
  pkg upgrade
  pkg install x11-repo tur-repo
  pkg update
  pkg install pulseaudio proot proot-distro wget git curl mc
  pkg install termux-api
  git clone https://github.com/MFDGaming/ubuntu-in-termux.git
  cd ./ubuntu-in-termux
  nano ./ubuntu.sh
  Modify [UBUNTU_VERSION='24.10'] line to the ubuntu version you desire (18.04.5)
  chmod +x ubuntu.sh
  ./ubuntu.sh -y
  ./startubuntu.sh
  apt update 
  apt upgrade
  apt install nano mc git wget curl
  apt install xfce4
  apt install xvfb x11vnc
  wget https://raw.githubusercontent.com/AdamPoloha/Multicopter-phone-ROS/refs/heads/main/startxvnc.sh
  chmod +x ./startxvnc.sh
  ./startxvnc.sh
On your desktop open Remmina
Setup new connection:
  Name: PhoneDrone
  Protocol: VNC
  Server: ipaddress [192.168.121.70]
  Username: username [u0_a248]
  User password: password [copter]
  Colour Depth: High Colour
  Quality: Poor
Save and Start



  ROS Melodic install instructions (http://wiki.ros.org/melodic/Installation/Ubuntu)
