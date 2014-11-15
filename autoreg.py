#! /usr/bin/python
# -*- coding: utf-8 -*-
# upload performance data to central server search.sasm3.net

import sys, os, urllib, urllib2, uuid, time
from collections import defaultdict
from webcrawl import connect_detection
dirname, filename = os.path.split(os.path.abspath(sys.argv[0]))
#TODO check data integrity before uploading
if len(sys.argv)>1:
    idle = int(sys.argv[1])
    time.sleep(idle)
start = {}
try:
    with open(dirname+'/code') as fh:
        code = fh.readline().rstrip()
        desc = fh.readline().rstrip()
except:
    print 'Failed to open code file'
    exit(1)
mac_int = uuid.getnode()
if (mac_int>>40)%2:
    mac = '000000000000'
else:
    mac = '{0:012x}'.format(mac_int)
if 0==connect_detection(6):
    domain = '115.25.86.4'
else:
    domain = 'perf.sasm3.net'
value = {'code':code, 'mac':mac, 'desc':desc}
para = urllib.urlencode(value)
url = 'http://'+domain+'/raspberry/autoreg.php?'+para
req = urllib2.Request(url)
response = urllib2.urlopen(req)
output = response.read()
response.close()
print 'autoreg:',output
