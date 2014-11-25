#! /usr/bin/python
# -*- coding: utf-8 -*-
# upload performance data to central server search.sasm3.net

import socket, time, sys, MySQLdb, os, urllib, urllib2, logging, logging.handlers
from collections import defaultdict
from webcrawl import *
dirname, filename = os.path.split(os.path.abspath(sys.argv[0]))
mac = mac_addr()
#TODO check data integrity before uploading
start = {}
values = {'mac':mac}

if 0==connect_detection(6):
    domain = '115.25.86.4'
else:
    domain = 'perf.sasm3.net'
pm1=MySQLdb.connect(host='localhost',user='root',db='raspberry')
cur1=pm1.cursor()

url = 'http://'+domain+'/raspberry/time.php?mac='+mac
req = urllib2.Request(url)
response = urllib2.urlopen(req)
output = response.read()
response.close()
data = []
for line in output.split('\n'):
    if line.count(':'):
        table, newest = line.split(':',1)
        cur1.execute("select * from {0} where time>'{1}' and mac='{2}' order by time limit 900".format(table.replace('perf_'+mac+'_v','web_perf'), newest, mac))
        result = cur1.fetchall()
        for entry in result:
            #print( table+'||'+','.join([str(i) for i in entry]) )
            data.append( table+'||'+'|'.join([str(i) for i in entry]) )
noin = len(data)
if noin == 0 :
    print 0,0
else:
    values['data'] = '||||'.join(data)
    with open(dirname+'/current-'+str(mac)+'-4','r') as fh:
        values['v4stat'] = fh.readline().rstrip()
    with open(dirname+'/current-'+str(mac)+'-6','r') as fh:
        values['v6stat'] = fh.readline().rstrip()
    url = 'http://'+domain+'/raspberry/receive.php'
    para = urllib.urlencode(values)
    req = urllib2.Request(url, para)
    response = urllib2.urlopen(req)
    output = response.read()
    print noin, output
    response.close()

