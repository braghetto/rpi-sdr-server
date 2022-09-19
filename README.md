# Rpi SDR Server

Its my quick setup to use a rpi as a sdr server.


## About

This script configure a fresh raspian instal to serve as a sdr server.


## How To

### Compatibility
* Raspberry Pi OS Lite 64bit - debian 11 bullseye
* Raspberry Pi 3 B+ hardware
* RTL2832 usb hardware

### Install
* Build a a raspberry pi os sdcard
* have ssh access with sudo powers
* connect wifi/ethernet to internet
* install git client
`sudo apt install git`
* clone this repository
`git clone https://github.com/braghetto/rpi-sdr-server.git`
* run
`cd rpi-sdr-server/`
`./install.sh`
