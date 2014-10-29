sleep $(($RANDOM%300))
cd /root/mnt
num=$(($((0x`md5sum code |cut -d' ' -f1`))%24))
if [ $num -eq `date +%H` ];
then
	echo "IP detecting & syncweb"
	/usr/bin/python syncweb.py
	/usr/bin/python ipdetection.py

fi
/usr/bin/python ipv4mnt.py
/usr/bin/python ipv6mnt.py
/usr/bin/python upload.py 
