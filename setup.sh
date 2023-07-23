#!/bin/sh
echo "Automated setup tool"
echo "Updating System"
sudo apt-get update && sudo apt-get upgrade -y
echo "Installing Dependencies"
sudo apt-get install python3 python3-dev python3-pillow libopenjp2-7-dev
/home/pi/matrixticker/venv/bin/python3 -m pip install -r requirements.txt

echo "Removing Audio Module"
echo "blacklist snd_bcm2835" | sudo tee /etc/modprobe.d/blacklist-rgb-matrix.conf

sudo update-initramfs -u

echo "Reserving CPU core for Displays"
sudo sed -i -e 's/$/ isolcpus=3/' /boot/cmdline.txt

echo "Configuring System Service"
sudo cp matrixticker.service /etc/systemd/system/matrixticker.service
sudo systemctl enable matrixticker

#echo "Rebooting"
sudo reboot
