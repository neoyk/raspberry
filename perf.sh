#! /bin/bash
#exit
cd /root/mnt
unset pid
ps -ef | grep perf.sh | grep -v grep 
date
pid=`ps -ef | grep perf.sh | grep -v grep | wc -l`
echo $pid

if [ "$pid" -gt "3" ]; then
	echo "perf.sh already running, exiting"
	exit
fi
RANDOM=$$
/usr/bin/mysqlcheck --repair raspberry
sleep 120
sleep $(($RANDOM%600))
/usr/sbin/ntpdate s1a.time.edu.cn
rm -f tmp.*
rm -f 420*
rm -f 620*
if [ ! -f hour ]
then
	echo $(($RANDOM%24)) > hour
fi
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
date
