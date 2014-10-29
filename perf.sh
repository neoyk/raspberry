sleep $(($RANDOM%300))
cd /root/mnt
num=$(($((0x`md5sum code |cut -d' ' -f1`))%24))
if [ $num -lt `date +%H` ];
then
	echo "syncweb"
	/usr/bin/python syncweb.py
fi
#v4start=`date +"%Y-%m-%d+%H:%M:%S"`
/usr/bin/python ipv4mnt.py
#v6start=`date +"%Y-%m-%d+%H:%M:%S"`
/usr/bin/python ipv6mnt.py
#/usr/bin/python upload.py $v4start $v6start
/usr/bin/python upload.py 
