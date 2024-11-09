# Multicopter-phone-ROS

Here I will detail the whole process to get an android phone to run ROS and control a multicopter.

What you will need:
Linux
Android Phone (Accelerometer, Gyroscope, and Compass)
USB Cable

I will attempt to do it without root.

Phone installs:
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
  Inside Termux:
    whoami (the ouput is the phone username)
    
