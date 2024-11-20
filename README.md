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
Set static IP address:
  Tap the Settings icon next to the current network
  Tap View more
  Choose IP settings
  Pick Static
  Type in the new IP address or keep current, and tap Save
Enable USB debugging (If you want to use adb):
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
  Install Termux:X11:
    Download Apk (https://github.com/termux/termux-x11/releases/tag/nightly)
    Open the file
    Tap Install
Inside Termux:
  pkg update
  pkg upgrade
  pkg install openssh
  Follow ssh example (https://github.com/termux/termux-boot)
  mkdir ~/.termux/boot
  nano ~/.termux/boot/start-sshd
  Paste in: (CTRL+S and CTRL+X to save and exit)
#!/data/data/com.termux/files/usr/bin/sh
termux-wake-lock
sshd
  chmod +x ~/.termux/boot/start-sshd
%Restart Phone
If you wish to use USB for ssh, you can try to use and modify networkifyUSB-root.sh if you have root, otherwise you need to either set Default USB configuration in Developer options to USB tethering or RNDIS, or enable it manually each time.
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
XFCE install (https://github.com/LinuxDroidMaster/Termux-Desktops/blob/main/Documentation/proot/debian_proot.md#installing-desktops)
Inside ssh session:
  pkg update
  pkg upgrade
  pkg install x11-repo tur-repo
  pkg update
  pkg install termux-x11-nightly pulseaudio proot proot-distro wget git curl mc
  pkg install termux-api
  proot-distro install ubuntu-oldlts
  proot-distro login ubuntu-oldlts
Inside Ubuntu session:
  apt update 
  apt upgrade
  apt install dialog nano mc git wget curl
  apt install xfce4
  exit
Inside ssh session:
  wget https://raw.githubusercontent.com/LinuxDroidMaster/Termux-Desktops/main/scripts/proot_debian/startxfce4_debian.sh
  mv ./startxfce4_debian.sh ./startxfce4_ubuntu.sh
  nano ./startxfce4_ubuntu.sh
  Modify [proot-distro login debian --shared-tmp -- /bin/bash -c  'export PULSE_SERVER=127.0.0.1 && export XDG_RUNTIME_DIR=${TMPDIR} && su - droidmaster -c "env DISPLAY=:0 startxfce"'] line to [proot-distro login ubuntu-oldlts --shared-tmp -- /bin/bash -c  'export PULSE_SERVER=127.0.0.1 && export XDG_RUNTIME_DIR=${TMPDIR} && DISPLAY=:0 startxfce4']
  chmod +x ./startxfce4_ubuntu.sh
  ./startxfce4_ubuntu.sh
Logout of ubuntu session on phone
  proot-distro login ubuntu-oldlts
Inside Ubuntu terminal session:
  apt install xvfb x11vnc
  wget https://raw.githubusercontent.com/AdamPoloha/Multicopter-phone-ROS/refs/heads/main/startxvnc.sh
  chmod +x ./startxvnc.sh
  ./startxvnc.sh

Hardware Acceleration:
Desktop (https://github.com/LinuxDroidMaster/Termux-Desktops/blob/main/Documentation/HardwareAcceleration.md)
If you have a Snapdragon CPU with a 600 or 700 series Adreno GPU, you can use the Turnip Vulkan driver.
Here I am using a Mali-G72 MP3 GPU and so will use the alternatives.
Log out of Remmina session
In the ssh ubuntu terminal window:
  CTRL+C
  exit
In the same window, now ssh to Termux:
  pkg install mesa-zink virglrenderer-mesa-zink vulkan-loader-android virglrenderer-android
  ZINK:
    MESA_NO_ERROR=1 MESA_GL_VERSION_OVERRIDE=4.3COMPAT MESA_GLES_VERSION_OVERRIDE=3.2 GALLIUM_DRIVER=zink ZINK_DESCRIPTORS=lazy virgl_test_server --use-egl-surfaceless --use-gles &
  VIRGL:
    virgl_test_server_android &
  ./startxfce4_ubuntu.sh
Inside Termux:X11 session terminal:
  apt install glmark2
  glmark2 (Runs on cpu) [50fps for me]
  GALLIUM_DRIVER=virpipe MESA_GL_VERSION_OVERRIDE=4.0 glmark2 (Runs on gpu) [40fps for me on ZINK, 52fps on VIRGL]
Logout
In ssh to Termux:
  cp ./startxfce4_ubuntu.sh ./startubuntuVNC.sh
  nano ./startubuntuVNC.sh
  Under [pulseaudio --start...] line insert:
#Start graphics server
#MESA_NO_ERROR=1 MESA_GL_VERSION_OVERRIDE=4.3COMPAT MESA_GLES_VERSION_OVERRIDE=3.2 GALLIUM_DRIVER=zink ZINK_DESCRIPTORS=lazy virgl_test_server --use-egl-surfaceless --use-gles &
virgl_test_server_android &
  Modify [proot-distro login ubuntu-oldlts --shared-tmp -- /bin/bash -c  'export PULSE_SERVER=127.0.0.1 && export XDG_RUNTIME_DIR=${TMPDIR} && DISPLAY=:0 startxfce4'] line to [proot-distro login ubuntu-oldlts --shared-tmp -- /bin/bash -c  'export PULSE_SERVER=127.0.0.1 && export XDG_RUNTIME_DIR=${TMPDIR} && cd ~ && ./startxvnc.sh']
  Save
  proot-distro login ubuntu-oldlts
Now in Ubuntu:
  nano ./startxvnc.sh
  Instead of the [export DISPLAY=:0] line paste in [export DISPLAY=:0 GALLIUM_DRIVER=virpipe MESA_GL_VERSION_OVERRIDE=4.0] (Will run desktop with gpu, may cause window manager and taskbar issues, neither would draw but a new taskbar could be created)
  exit
In ssh to Termux:
  ./startubuntuVNC.sh
Connect with Remmina

Install ROS:
Check ROS2 release for Ubuntu 22.04 (https://docs.ros.org/en/rolling/Releases.html)
ROS Humble install instructions (https://docs.ros.org/en/humble/Installation/Ubuntu-Install-Debs.html)
From Remmina or ssh ubuntu console:
  wget https://raw.githubusercontent.com/AdamPoloha/Multicopter-phone-ROS/refs/heads/main/README.md (Download this readme if you want to copy and paste commands)
  apt install software-properties-common
  add-apt-repository universe
  curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg
  echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | tee /etc/apt/sources.list.d/ros2.list > /dev/null
  apt update
  apt upgrade
  apt install ros-humble-desktop
  apt install ros-dev-tools
  nano ~/.bashrc
  At the end of the file paste in [source /opt/ros/humble/setup.bash]
  Logout

Install Firefox:
Snapless (https://askubuntu.com/questions/1399383/how-to-install-firefox-as-a-traditional-deb-package-without-snap-in-ubuntu-22)
Terminal:
  add-apt-repository ppa:mozillateam/ppa
  echo '
Package: *
Pin: release o=LP-PPA-mozillateam
Pin-Priority: 1001

Package: firefox
Pin: version 1:1snap*
Pin-Priority: -1
' | tee /etc/apt/preferences.d/mozilla-firefox
  apt install firefox

Drone package:
Make Package (https://docs.ros.org/en/eloquent/Tutorials/Creating-Your-First-ROS2-Package.html)
SJTU Drone ROS2 (https://github.com/NovoG93/sjtu_drone)
Terminal:
  mkdir ~/ros2_ws
  mkdir ~/ros2_ws/src
  cd ~/ros2_ws/src
  ros2 pkg create --build-type ament_python --node-name hello_node phone_drone
  cd ~/ros2_ws
  colcon build
  . install/setup.bash
  ros2 run phone_drone hello_node

Sensors:
You can check which sensors the Android system provides, you can try to get the raw sensor data, but it is interesting to use what the system already provides as in some cases the result is very good and optimised for a low computational impact. Not all software sensors actually provide any data.
Android Sensors (https://developer.android.com/develop/sensors-and-location/sensors/sensors_overview)
Position Sensors (https://developer.android.com/develop/sensors-and-location/sensors/sensors_position)
Make a ROS2 node (https://industrial-training-dev.readthedocs.io/en/latest/_source/session1/ros2/3-Creating-a-ROS-Package-and-Node.html)
Android Terminal:
  termux-sensor -l (lists hardware and software sensors)
  termux-sensor -s "sensor_name" (check what data you can get from the sensor)
  CTRL+C to stop the program
What I got on OPPO A91, mapped to what each sensor gave me:
  "bmi160 ACCELEROMETER", [X,Y,Z] (m/s^2)
  "akm09915 MAGNETOMETER",[X,Y,Z] (untested units)
  "ORIENTATION", -> "DEVICE_ORIENTATION"
  "bmi160 GYROSCOPE", [X,Y,Z] (Probably radians/s)
  "tcs3701 LIGHT", [16 Values, 3 Active, Mosly 1 Relevant] (Screen side)
  "tcs3701 PROXIMITY", [3 Values, 1 Active] (Screen side, either 5 at distance or 0 when close)
  "UNCALI_MAG", [6 Values, 3 Active, X,Y,Z]
  "UNCALI_GYRO", [6 Values, X,Y,Z, and 3 constants] (Constant are probably some initial offset, different every run)
  "SIGNIFICANT_MOTION", [Always empty]
  "STEP_DETECTOR", [I got either empty or One Value = 1]
  "STEP_DETECTOR_WAKEUP", Same as "STEP_DETECTOR" at first glance
  "STEP_COUNTER", [One Value] (Precision is 10 steps)
  "WAKE_GESTURE", [Empty]
  "GLANCE_GESTURE", [Empty]
  "DEVICE_ORIENTATION", [One Value] (Probably screen orientation, landscape/portrait)
  "STATIONARY_DETECT", [Empty]
  "MOTION_DETECT", [Empty]
  "IN_POCKET", [Empty]
  "UNCALI_ACC", [6 Values, 3 Active, X,Y,Z] (m/s^2)
  "FLAT", [Empty]
  "CAMERA_PROTECT", [Empty]
  "FREE_FALL", [Empty]
  "PICKUP_DETECT", [Empty -> 16 Values, 2 Active] (No clue what they mean)
  "LUX_AOD", [16 Values, similar to pickup, but 4 are Active]
  "PEDO_MINUTE", [Empty] (How many minutes has a pedo been watching you)
  "TP_GESTURE", [16 Values] (Do not want to analyse)
  "OPPO_ACTIVITY_RECOGNITION", [16 Values]
  "OPLUS Fusion Light Sensor", [16 Values, 2 Relevant] (First probably raw, second calculated same as "tcs3701 LIGHT")
  "Game Rotation Vector Sensor", [X,Y,Z,W] (Should be Gyro Integrated Quaternion)
  "GeoMag Rotation Vector Sensor", [5 Values, X,Y,Z,W,0] (Magnetometer/Compass Quaternion)
  "Gravity Sensor", [X,Y,Z] (Gravity extracted from Accelerometer)
  "Linear Acceleration Sensor", [X,Y,Z] (Gravity removed from Accelerometer)
  "Rotation Vector Sensor", -> "Game Rotation Vector Sensor"
  "Orientation Sensor", [Y,P,R] (Degrees, should have some sensor fusion)
Approaches:
  RAW (Handle everything later)
  Filtered+Integrated (Trust Android data and can use it well)
  Fused (Use fused orientation and possibly use Linear acceleration with gravity removed right away)
I will go with Filtered method as accelerometer will likely be unusable even without gravity, and I can write my own simple switching between Game and GeoMag rotation vectors.
You could send everything to ROS, but will likely not be able to run fast.
Android Terminal:
  pkg install netcat-openbsd
  cd ~
  wget https://raw.githubusercontent.com/AdamPoloha/Multicopter-phone-ROS/refs/heads/main/sensor.sh
  nano ~/sensor.sh
  Modify [termux-sensor -s] line:
termux-sensor -s "sensor1","sensor2" -d [time period in ms between updates] | nc 127.0.0.1 1234
  Mine: termux-sensor -s "Game Rotation Vector Sensor","GeoMag Rotation Vector Sensor","bmi160 GYROSCOPE","bmi160 ACCELEROMETER","akm09915 MAGNETOMETER" -d 1 | nc 127.0.0.1 1234
  chmod +x ~/sensor.sh
  termux-sensor -s "sensor1","sensor2" -d [time period in ms between updates]
  You will want to know the ordering of the data, mine: Mag, Acc, Geo, Gyro, Game 
  cp ~/sensor.sh ~/.termux/boot/sensor.sh
  Or mkdir ~/.shortcuts && cp ~/sensor.sh ~/.shortcuts/sensor.sh (For use with Termux Widget)
Once you have it running, by restarting, widget, or terminal, you can open Ubuntu
Ubuntu Terminal:
  cd ~/ros2_ws/src/phone_drone/phone_drone
  wget https://raw.githubusercontent.com/AdamPoloha/Multicopter-phone-ROS/refs/heads/main/phone_sensor_publisher_node.py
  apt install geany
  geany ../setup.py
  Add new entry point to console_scripts
'phone_sensor_publisher_node = phone_drone.phone_sensor_publisher_node.py'
  geany ./phone_sensor_publisher_node.py
  Relpace [import rospy] with [import rclpy]
  Put loose code into main(), and after if __name__ == __main__, run main() 
