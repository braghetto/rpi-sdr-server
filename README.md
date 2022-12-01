# Rpi SDR Server

Its my quick setup to use a rpi as a sdr server.


## About

The deploy playbook will configure a fresh raspios instalation to serve as a sdr server.


## Installation

### Compatibility
* Raspberry Pi OS Lite 64bit - debian 11 bullseye
* Raspberry Pi 3 B+ hardware
* RTL2832 usb hardware

### Install
* Build a raspberry pi os sdcard
* You can easily build a sdcard using rpi-imager tool
* Connect rpi wifi/ethernet to internet
* Have ssh access to rpi with sudo powers
* You will need to have ansible installed (in your pc, not in rpi host):
* [Ansible Instalation Docs](https://docs.ansible.com/ansible/latest/installation_guide/index.html)
* Clone this repository:
* `git clone https://github.com/braghetto/rpi-sdr-server.git`
* Change to repo directory:
* `cd rpi-sdr-server`
* Run ansible deploy playbook inside repo directory:
* `ansible-playbook deploy.yml`
* You be prompted for rpi ip address, ssh port, ssh username, ssh password, telegram bot token, bot owner id and bot group id.
* Grab a beer and wait, we'll be compiling a lot of stuff using rpi hardware...
* Reboot rpi

## Use

### Software included
* spyserver
* soapyremote server
* telegram bot
* rtl_airband
* rtl_tcp
* calibration tool
* rtl_433 tool

### Services avaliable
* spyserver.service
* soapyserver.service
* telegrambot.service
* rtlairband.service
* rtltcp.service

### Configuration files
* spyserver
`/etc/spyserver.config`
* rtl_433
`/etc/rtl_433.conf`
* rtl_airband
`/etc/rtl_airband.conf`
* telegram bot
`/usr/local/src/telegrambot/bot.py`

### Instructions
* Its possible to change telegram bot TOKEN, GROUP_ID and OWNER_ID inside file: /usr/local/src/telegrambot/tokens.py
* If you want to change the airband channels you can change their names in: /usr/local/src/telegrambot/airband.py
* The telegrambot service is enabled by default.
* Do not run or enable multiple sdr services at same time.
* Use systemctl to start/stop or enable/disable sdr services.
* Use calibrate command to ajust ppm error.
* Calibrate script is very tailored for my use case and my dongles, you probaly want to change it.
* Channels configured by default in the airband are specific to my region, you probably want to change them too.
* Use only one usb RTL2832 dongle at time.
