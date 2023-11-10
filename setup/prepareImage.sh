echo "RGB Matrix Ticker Image Preparation Tool"
echo "This tool is intended to run on a brand new installation of Raspberry Pi OS (Legacy) Lite"
echo "Step 1: Update and Upgrade System"
sudo apt-get update && sudo apt-get upgrade -y
echo "Step 2: Install Packages and Cleanup"
sudo apt-get remove -y bluez bluez-firmware pi-bluetooth triggerhappy pigpio
sudo apt-get install -y python3 python3-dev python3-pip python3-pillow git
echo "Step 3: Install rpi-rgb-led-matrix"
git clone https://github.com/hzeller/rpi-rgb-led-matrix /home/pi/rpi-rgb-led-matrix
cd /home/pi/rpi-rgb-led-matrix
make build-python PYTHON=$(command -v python3)
sudo make install-python PYTHON=$(command -v python3)
cd ~
echo "Step 4: Install wifi-connect"
curl -L https://github.com/balena-io/wifi-connect/raw/master/scripts/raspbian-install.sh | bash -s -- -y
echo "Step 5: Copy setup folder to home directory"
cp -r /home/pi/matrixticker/setup /home/pi/setup
echo "Step 6: Enable setup service"
sudo cp /home/pi/setup/matrixticker-setup.service /etc/systemd/system/matrixticker-setup.service
sudo systemctl enable matrixticker-setup
echo "Step 7: Change Daemon Sudo Permissions"
echo "daemon ALL=(ALL) NOPASSWD:ALL" | sudo EDITOR='tee -a' visudo
echo "Step 8: Isolate CPU Core for Matrix Refresh"
sudo sed -i -e 's/$/ isolcpus=3/' /boot/cmdline.txt
echo "Step 9: Blacklist Audio Module"
echo "blacklist snd_bcm2835" | sudo tee /etc/modprobe.d/blacklist-rgb-matrix.conf
sudo update-initramfs -u
echo "Please delete the matrixticker folder manually from the home directory"
echo "System is now ready for replication"