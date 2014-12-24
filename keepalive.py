#! /usr/bin/python
# wget --delete-after --header="Host:1111.ip138.com" 112.84.191.168/ic.asp

from webcrawl import *
from random import randint
import subprocess, shlex, os, urllib, urllib2, time
time.sleep(randint(20,200)/10.0)
mac = mac_addr()
dirname, _ = os.path.split(os.path.abspath(sys.argv[0]))
if os.path.isfile(dirname+os.sep+'version'):
    with open(dirname+os.sep+'version') as f:
        version = f.readline().rstrip()
else:
    version = '1.0'
# 20:36:59 up 13 days,  6:23,  3 users,  load average: 0.40, 0.34, 0.32
load5min = re.search("average: (.*), (.*), (.*)",subprocess.Popen(shlex.split('uptime'),stdout=subprocess.PIPE).stdout.read()).group(2)
#rootfs           14G  3.3G  9.4G  26% /
dusage = re.search("\s([\d\.]+\%)",subprocess.Popen(shlex.split('df -h /'),stdout=subprocess.PIPE).stdout.read()).group(1)
#dusage = subprocess.Popen(shlex.split('df -h /'),stdout=subprocess.PIPE).stdout.read()
domain = domain_detection()
machine_time = time.strftime("%Y%m%d-%H%M%S")
values= {'mac':mac, 'load5min' : load5min, 'dusage':dusage, 'version':version,'time':machine_time }
url = 'http://'+domain+'/raspberry/keepalive.php'
para = urllib.urlencode(values)
req = urllib2.Request(url, para)
response = urllib2.urlopen(req)
output = response.read()
response.close()
print time.strftime("%Y-%m-%d %H:%M"),"Status uploaded:",load5min, dusage, version, machine_time, output
if(int(output)&2):
    print "starting openvpn"
    os.system("/usr/sbin/service openvpn start")
    time.sleep(2)
if(int(output)&4):
    print "stoping openvpn"
    os.system("/usr/sbin/service openvpn stop")
if(int(output)&8):
    subprocess.Popen(shlex.split("nohup bash /root/mnt/perf.sh >> /root/mnt/log.perf 2>&1"))
