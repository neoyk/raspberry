#! /bin/bash
#exit
RANDOM=$$
/usr/bin/mysqlcheck --repair raspberry
sleep $(($RANDOM%600))
/usr/sbin/ntpdate s1a.time.edu.cn
cd /root/mnt
rm -f tmp.*
rm -f 420*
rm -f 620*
if [ ! -f hour ]
then
	echo $(($RANDOM%24)) > hour
fi
date
#num=$(($((0x`md5sum address |cut -d' ' -f1`))%24))
read num < hour
if [ $num -eq `date +%H` ];
then
	service mysql restart
	echo "IP detecting & syncweb"
	/usr/bin/python syncweb.py
	/usr/bin/python ipdetection.py

fi
/usr/bin/python ipv4mnt.py
/usr/bin/python ipv6mnt.py
/usr/bin/python upload.py 
