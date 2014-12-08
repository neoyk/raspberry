#! /usr/bin/python
# wget --delete-after --header="Host:1111.ip138.com" 112.84.191.168/ic.asp

from webcrawl import *
import subprocess, os, urllib, urllib2
mac = mac_addr()
# 20:36:59 up 13 days,  6:23,  3 users,  load average: 0.40, 0.34, 0.32
load5min = re.search("average: (.*), (.*), (.*)",subprocess.Popen(shlex.split('uptime'),stdout=subprocess.PIPE).stdout.read()).group(2)
#rootfs           14G  3.3G  9.4G  26% /
dusage = re.search("\s([\d\.]+\%)",subprocess.Popen(shlex.split('df -h /'),stdout=subprocess.PIPE).stdout.read()).group(1)
#dusage = subprocess.Popen(shlex.split('df -h /'),stdout=subprocess.PIPE).stdout.read()
if 0==connect_detection(6):
    domain = '115.25.86.4'
else:
    domain = 'perf.sasm3.net'
values= {'mac':mac, 'load5min' : load5min, 'dusage':dusage }
url = 'http://'+domain+'/raspberry/keepalive.php'
para = urllib.urlencode(values)
req = urllib2.Request(url, para)
response = urllib2.urlopen(req)
output = response.read()
print "Status uploaded:",load5min, dusage, output
response.close()
