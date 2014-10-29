#! /usr/bin/python
# -*- coding: utf-8 -*-
# upload performance data to central server search.sasm3.net

import sys, os, urllib, urllib2, uuid
from collections import defaultdict
dirname, filename = os.path.split(os.path.abspath(sys.argv[0]))
#TODO check data integrity before uploading
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
    mac = 'NA'
else:
    mac = '{0:012x}'.format(mac_int)
value = {'code':code, 'mac':mac, 'desc':desc}
para = urllib.urlencode(value)
url = 'http://perf.sasm3.net/raspberry/autoreg.php?'+para
req = urllib2.Request(url)
response = urllib2.urlopen(req)
output = response.read()
response.close()
print output
