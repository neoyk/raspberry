#! /bin/bash
#exit
cd /root/mnt
unset pid
printf "Starting @ " && date
if [ ! -f pid ]
then
	echo $$ > pid
else
	read pid < pid
	ps -ef | grep $pid | grep -v grep 
	ppid=`ps -ef | grep $pid | grep -v grep | awk '{print $2}'`
	echo $ppid
	
	if [ ! -z "$ppid" ]; then
		echo "perf.sh already running, exiting"
		echo
		exit
	else
		echo $$ > pid
	fi
fi
RANDOM=$$
/usr/bin/mysqlcheck --repair raspberry
sleep 120
sleep $(($RANDOM%500))
/usr/sbin/ntpdate s1a.time.edu.cn
rm -f tmp.*
rm -f 420*
rm -f 620*
if [ ! -f hour ]
then
	echo $(($RANDOM%24)) > hour
	/usr/bin/python autoreg.py
	/usr/bin/python ipdetection.py
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
rm -f pid
printf "END @ " && date
echo
