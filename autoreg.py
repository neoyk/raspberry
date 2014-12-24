#! /usr/bin/python
# -*- coding: utf-8 -*-
# upload performance data to central server search.sasm3.net

import sys, os, urllib, urllib2, uuid, time, MySQLdb, shlex, subprocess
from collections import defaultdict
from webcrawl import *
dirname, filename = os.path.split(os.path.abspath(sys.argv[0]))
#TODO check data integrity before uploading
if len(sys.argv)>1:
    idle = int(sys.argv[1])
    time.sleep(idle)
start = {}
mac = mac_addr()
domain = domain_detection()
value = {'mac':mac }
para = urllib.urlencode(value)
url = 'http://'+domain+'/raspberry/autoreg.php?'+para
req = urllib2.Request(url)
response = urllib2.urlopen(req)
output = response.read()
response.close()
if '11111' == output:
    pm2=MySQLdb.connect(host='127.0.0.1',user='root',db='raspberry')
    cur2=pm2.cursor()
    cur2.execute("delete from address")
    cur2.execute("delete from avgbw4")
    cur2.execute("delete from avgbw6")
    cur2.execute("delete from avgrtt4")
    cur2.execute("delete from avgrtt6")
    cur2.execute("delete from avgloss4")
    cur2.execute("delete from avgloss6")
    cur2.execute("delete from web_perf4")
    cur2.execute("delete from web_perf6")
    pm2.commit()
    cur2.close(); pm2.close()
    cmd = '/usr/bin/python /root/mnt/syncweb.py'
    a = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE,stderr = subprocess.PIPE )
    a.wait()
print 'autoreg:',output
directory = '/etc/openvpn/'
if not os.path.exists(directory):
    os.makedirs(directory)
with open(directory+'pass.txt','w') as fh:
    fh.write("r_{0}\nelm".format(mac))
