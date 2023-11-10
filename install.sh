#!/bin/sh
echo "Automated setup tool"
echo "Updating System"
sudo apt-get update && sudo apt-get upgrade -y
echo "Installing Dependencies"
python3 -m pip install -r requirements.txt

echo "Expanding Root Filesystem"
sudo raspi-config nonint do_expand_rootfs

echo "Disabling setup service"
sudo systemctl disable matrixticker-setup

echo "Configuring System Service"
sudo cp matrixticker.service /etc/systemd/system/matrixticker.service
sudo systemctl enable matrixticker

echo "Automatically Setting Timezone"
zone=$(wget -O - -q http://geoip.ubuntu.com/lookup | sed -n -e 's/.*<TimeZone>\(.*\)<\/TimeZone>.*/\1/ p')

if [ "$zone" != "" ]; then
    echo $zone | sudo tee /etc/timezone > /dev/null
    dpkg-reconfigure -f noninteractive tzdata >/dev/null 2>&1
    timedatectl set-timezone $zone
    echo "[INFO] Timezone was set to $zone" >> "$logFile"   
else
    echo "[ERROR] Timezone is empty" >> "$logFile"
fi

echo "Fix Permissions of Home Folder"
sudo chown -R pi:pi /home/pi