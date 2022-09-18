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
		exit -1
	;;
esac

sudo systemctl stop spyserver.service

PPM=$(/usr/local/bin/kal -g $GAIN -b $BAND -c $CHAN -e $IERR |grep "average absolute error:" |awk '{print $4}')
PPB="${PPM//.}"
echo -e "${green}PPM: $PPM${clear}"
echo -e "${green}PPB: $PPB${clear}"

/usr/bin/sed -i -e "/frequency_correction_ppb =/ s/= .*/= $PPB/" /home/arthur/spyserver/spyserver.config

sudo systemctl start spyserver.service

exit 0
