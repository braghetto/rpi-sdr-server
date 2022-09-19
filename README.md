# Rpi SDR Server

Its my quick setup to use a rpi as a sdr server.


## About

This script configure a fresh raspian instalation to serve as a sdr server.
These settings are very specific to my usage and configuration.
Do not use until you understand the installation script and make the necessary changes for your use.


## Installation

### Compatibility
* Raspberry Pi OS Lite 64bit - debian 11 bullseye
* Raspberry Pi 3 B+ hardware
* RTL2832 usb hardware

### Install
* Build a raspberry pi os sdcard
* connect wifi/ethernet to internet
* have ssh access with sudo powers
* install git client
`sudo apt install git`
* clone this repository
`git clone https://github.com/braghetto/rpi-sdr-server.git`
* run
`cd rpi-sdr-server/`
`./install.sh`
* Grab a beer and wait, we'll be compiling a lot of stuff using rpi hardware...
* Reboot

## Use

## Software included
* spyserver
* sdrpp server
* rtl_tcp
* calibration tool
* rtl_433 tool

## Services avaliable
* spyserver.service
* rtltcp.service
* sdrpp.service

## Configuration files
* spyserver
`/etc/spyserver.config`
* rtl_433
`/etc/rtl_433.conf`
* sdrpp server
`~/.config/sdrpp/`

## Instructions
* By default the spyserver is the service enabled by installation script.
* Do not run or enable multiple sdr services at same time.
* Use systemctl to start/stop or enable/disable sdr services.
* Use calibrate command to ajust ppm error.
* Use only one usb RTL2832 dongle at time.

