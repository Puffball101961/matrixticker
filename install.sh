#!/bin/sh
echo "Automated setup tool"
echo "Updating System"
sudo apt-get update && sudo apt-get upgrade -y
echo "Installing Dependencies"
python3 -m pip install -r requirements.txt

echo "Disabling setup service"
sudo systemctl disable matrixticker-setup

echo "Configuring System Service"
sudo cp matrixticker.service /etc/systemd/system/matrixticker.service
sudo systemctl enable matrixticker
