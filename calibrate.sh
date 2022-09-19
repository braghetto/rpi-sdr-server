#!/usr/bin/bash

GAIN=29

SERIAL=$(lsusb -d 0bda: -v |grep iSerial |awk '{print $3}')

green='\033[0;32m'
clear='\033[0m'

# initial error and best channel to run kal
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

# stop sdr services
sudo systemctl stop spyserver.service
sudo systemctl stop rtltcp.service
sudo systemctl stop sdrpp.service

# float ppm value
PPM=$(/usr/local/bin/kal -g $GAIN -b $BAND -c $CHAN -e $IERR |grep "average absolute error:" |awk '{print $4}')
# round ppm to integer
PPMI=$(echo $PPM |awk '{print int($1+0.5)}')
# multiply to ppb
PPB="${PPM//.}"
# print
echo -e "${green}PPMi: $PPMI${clear}"
echo -e "${green}PPM: $PPM${clear}"
echo -e "${green}PPB: $PPB${clear}"

# set ppm/ppb in configs
/usr/bin/sed -i -e "/frequency_correction_ppb =/ s/= .*/= $PPB/" /etc/spyserver.config
/usr/bin/sed -i -e "s/-P [0-9]\+/-P $PPMI/" /etc/systemd/system/rtltcp.service
/usr/bin/sed -i -e "s/\"ppm\": [0-9]\+,/\"ppm\": $PPMI,/" ~/.config/sdrpp/rtl_tcp_config.json

# start sdr services again
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

# done
exit 0

