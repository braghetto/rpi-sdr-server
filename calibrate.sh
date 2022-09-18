#!/usr/bin/bash

GAIN=29

SERIAL=$(lsusb -d 0bda: -v |grep iSerial |awk '{print $3}')

green='\033[0;32m'
clear='\033[0m'

case $SERIAL in
	00000001)
		IERR=74
		BAND='GSM-R'
		CHAN=967
	;;
	00000002)
		IERR=55
		BAND='GSM850'
		CHAN=137
	;;
	*)
		exit 1
	;;
esac

sudo systemctl stop spyserver.service
sudo systemctl stop rtltcp.service
sudo systemctl stop sdrpp.service

PPM=$(/usr/local/bin/kal -g $GAIN -b $BAND -c $CHAN -e $IERR |grep "average absolute error:" |awk '{print $4}')
PPMI=$(echo $PPM |awk '{print int($1+0.5)}')
PPB="${PPM//.}"
echo -e "${green}PPMi: $PPM${clear}"
echo -e "${green}PPM: $PPM${clear}"
echo -e "${green}PPB: $PPB${clear}"

/usr/bin/sed -i -e "/frequency_correction_ppb =/ s/= .*/= $PPB/" /etc/spyserver.config
/usr/bin/sed -i -e "s/-P [0-9]\+/-P $PPMI/" /etc/systemd/system/rtltcp.service

sudo systemctl daemon-reload

if [ "$(sudo systemctl is-enabled spyserver.service)" = "enabled" ]
then
sudo systemctl start spyserver.service
fi

if [ "$(sudo systemctl is-enabled rtltcp.service)" = "enabled" ]
then
sudo systemctl start rtltcp.service
fi

if [ "$(sudo systemctl is-enabled sdrpp.service)" = "enabled" ]
then
sudo systemctl start sdrpp.service
fi

exit 0

