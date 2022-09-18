#!/usr/bin/bash



# initial system update
sudo apt -y update
sudo apt -y full-upgrade

# install libs and deps
sudo apt -y install git cmake build-essential libtool automake autoconf \
libvolk2-dev libzstd-dev libglfw3-dev libusb-dev libusb-1.0-0-dev libsoapysdr-dev \
libairspy-dev libairspyhf-dev libiio-dev libad9361-dev librtaudio-dev libhackrf-dev \
libfftw3-dev soapysdr-module-all soapysdr-tools

# go home
cd ~

# build rtl-sdr
git clone https://gitea.osmocom.org/sdr/rtl-sdr.git
cd rtl-sdr/
mkdir build
cd build/
cmake ../ -DINSTALL_UDEV_RULES=ON -DDETACH_KERNEL_DRIVER=ON -DENABLE_ZEROCOPY=ON
make
sudo make install
sudo ldconfig
cd ~

# build kalibrate tool
git clone https://github.com/steve-m/kalibrate-rtl
cd kalibrate-rtl/
./bootstrap && CXXFLAGS='-W -Wall -O3'
./configure
make
sudo make install
cd ~

# install spyserver
mkdir spyserver
cd spyserver/
wget http://airspy.com/downloads/spyserver-arm64.tgz
tar xvzf spyserver-arm64.tgz
rm spyserver-arm64.tgz
cd ~

# build sdrpp
git clone https://github.com/AlexandreRouma/SDRPlusPlus.git
cd SDRPlusPlus/
mkdir build
cd build/
cmake ..
make
sudo make install
cd ~

# build rtl_433
git clone https://github.com/merbanan/rtl_433.git
cd rtl_433
mkdir build
cd build
cmake ..
make
sudo make install
cd ~

# move src dirs
sudo mv kalibrate-rtl/ /usr/local/src
sudo mv rtl-sdr/ /usr/local/src
sudo mv rtl_433/ /usr/local/src
sudo mv SDRPlusPlus/ /usr/local/src
sudo mv spyserver/ /usr/local/src
sudo cp /usr/local/src/spyserver/spyserver /usr/local/bin/spyserver
sudo chown -R root:root /usr/local/src/*

# clone git repo
git clone https://github.com/braghetto/rpi-sdr-server.git
cd rpi-sdr-server/

# modproble blacklist
sudo rm /etc/modprobe.d/blacklist-rtl8xxxu.conf
sudo cp blacklist-rtlsdr.conf /etc/modprobe.d/

# install scripts
sudo mkdir /usr/local/src/scripts
sudo cp calibrate.sh /usr/local/src/scripts
sudo ln -s /usr/local/src/scripts/calibrate.sh /usr/local/bin/calibrate

# etc config files
sudo cp spyserver.config /etc
sudo cp rtl_433.conf /etc
mkdir ~/.config/rtl_433/
ln -s /etc/rtl_433.conf ~/.config/rtl_433/rtl_433.conf

# systemd services
sudo cp spyserver.service /etc/systemd/system
sudo cp rtltcp.service /etc/systemd/system
sudo systemctl daemon-reload
sudo systemctl enable spyserver.service

# remove repo
cd ~
rm -rf rpi-sdr-server/

# disable services
sudo systemctl stop triggerhappy.service 
sudo systemctl stop triggerhappy.socket 
sudo systemctl disable triggerhappy.service 
sudo systemctl disable triggerhappy.socket 
sudo systemctl stop polkit.service 
sudo systemctl disable polkit.service
sudo systemctl stop bluetooth.service 
sudo systemctl disable bluetooth.service
sudo systemctl stop hciuart.service 
sudo systemctl disable hciuart.service

# fix cmdline
sudo sed -i 's/console=serial0,115200 //g' /boot/cmdline.txt
sudo sed -i 's/$/ dwc_otg.fiq_fix_enable=0/' /boot/cmdline.txt

# boot config
echo "gpu_mem=16" |sudo tee -a /boot/config.txt
echo "force_turbo=1" |sudo tee -a /boot/config.txt
echo "arm_freq=900" |sudo tee -a /boot/config.txt
echo "core_freq=500" |sudo tee -a /boot/config.txt
echo "disable_splash=1" |sudo tee -a /boot/config.txt
echo "boot_delay=1" |sudo tee -a /boot/config.txt

# cpu governor
sudo sed -i '/^exit 0/d' /etc/rc.local
echo "# cpu governor" |sudo tee -a /etc/rc.local
echo "echo performance > /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor" |sudo tee -a /etc/rc.local
echo "echo performance > /sys/devices/system/cpu/cpu1/cpufreq/scaling_governor" |sudo tee -a /etc/rc.local
echo "echo performance > /sys/devices/system/cpu/cpu2/cpufreq/scaling_governor" |sudo tee -a /etc/rc.local
echo "echo performance > /sys/devices/system/cpu/cpu3/cpufreq/scaling_governor" |sudo tee -a /etc/rc.local
echo |sudo tee -a /etc/rc.local
echo "exit 0" |sudo tee -a /etc/rc.local

# avoid writing to sdcard
sudo sed -i 's/vfat    defaults/vfat    defaults,noatime/g' /etc/fstab
sudo sed -i 's/defaults,noatime/defaults,noatime,commit=1800/g' /etc/fstab
echo "tmpfs /tmp tmpfs defaults,noatime,nosuid,nodev,noexec,mode=0755,size=20M 0 0" |sudo tee -a /etc/fstab
echo "tmpfs /var/tmp tmpfs defaults,noatime,nosuid,nodev,noexec,mode=0755,size=20M 0 0" |sudo tee -a /etc/fstab
echo "tmpfs /var/log tmpfs defaults,noatime,nosuid,nodev,noexec,mode=0755,size=20M 0 0" |sudo tee -a /etc/fstab
echo "tmpfs /var/lib/upsd tmpfs defaults,noatime,nosuid,nodev,noexec,mode=0755,size=4K 0 0" |sudo tee -a /etc/fstab
sudo sed -i 's/CONF_SWAPSIZE=100/CONF_SWAPSIZE=0/g' /etc/dphys-swapfile
sudo swapoff -a

# done
green='\033[0;32m'
clear='\033[0m'
echo -e "${green}INSTALLATION COMPLETE${clear}"
echo -e "${green}Restart the system!${clear}"

