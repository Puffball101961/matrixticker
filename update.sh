#!/bin/sh
echo "Automated update tool"
echo "Updating System"
sudo apt-get update && sudo apt-get upgrade -y
echo "Installing Dependencies"
sudo apt-get install python3 python3-dev python3-pillow libopenjp2-7-dev

echo "Pulling latest version"
git pull

echo "Installing Python Dependencies"
/home/pi/matrixticker/venv/bin/python3 -m pip install -r requirements.txt

echo "Configuring System Service"
sudo rm /etc/systemd/system/matrixticker.service
sudo cp matrixticker.service /etc/systemd/system/matrixticker.service
sudo systemctl daemon-reload
sudo systemctl enable matrixticker

#echo "Rebooting"
sudo reboot
