#! /bin/bash
#exit
cd /root/mnt
unset pid
printf "Starting @ " && date
if [ ! -f run ]
then
	echo $$ > run
else
	read pid < run
	ps -ef | grep $pid | grep perf.sh | grep -v grep 
	ppid=`ps -ef | grep $pid |grep perf.sh | grep -v grep | awk '{print $2}'`
	echo $ppid
	
	if [ "$$" != "$ppid" ] && [ ! -z "$ppid" ]; then
		echo "perf.sh already running, exiting"
		echo
		exit
	else
		echo $$ > run
	fi
fi
RANDOM=$$
sleep 30
/usr/bin/mysqlcheck --repair raspberry
/usr/sbin/ntpdate -u s1a.time.edu.cn
rm -f tmp.*
rm -f 420*
rm -f 620*
if [ ! -f hour ]
then
	echo $(($RANDOM%24)) > hour
	/usr/bin/python autoreg.py
	/usr/bin/python mac.py > /etc/hostname
	/usr/bin/python syncweb.py
	hostname -F /etc/hostname
fi
if [ ! -f second ]
then
	echo $(($RANDOM%3600)) > second
fi
#num=$(($((0x`md5sum address |cut -d' ' -f1`))%24))
read num < hour
if [ $num -eq `date +%H` ];
then
	service mysql restart
	echo "syncweb"
	/usr/bin/python syncweb.py

fi
/usr/bin/python ipdetection.py
/usr/bin/python ipv4mnt.py
/usr/bin/python ipv6mnt.py
/usr/bin/python upload.py 
rm -f run
printf "END @ " && date
echo
