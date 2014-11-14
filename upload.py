#! /usr/bin/python
# -*- coding: utf-8 -*-
# upload performance data to central server search.sasm3.net

import socket, time, sys, MySQLdb, os, urllib, urllib2, logging, logging.handlers
from collections import defaultdict
from webcrawl import connect_detection
dirname, filename = os.path.split(os.path.abspath(sys.argv[0]))
#TODO check data integrity before uploading
start = {}
try:
    with open(dirname+'/code') as fh:
        code = fh.readline().rstrip()
except:
    print 'Failed to open code file'
    exit(1)
values = {'code':code}

if 0==connect_detection(6):
    domain = '115.25.86.4'
else:
    domain = 'perf.sasm3.net'
pm1=MySQLdb.connect(host='localhost',user='root',db='raspberry')
cur1=pm1.cursor()

url = 'http://'+domain+'/raspberry/time.php?code='+code
req = urllib2.Request(url)
response = urllib2.urlopen(req)
output = response.read()
response.close()
data = []
for line in output.split('\n'):
    if line.count(':'):
        table, newest = line.split(':',1)
        #print("select * from {0} where time>'{1}' order by time limit 900".format(table.replace(code,'web_perf'), newest))
        cur1.execute("select * from {0} where time>'{1}' order by time limit 900".format(table.replace(code,'web_perf'), newest))
        result = cur1.fetchall()
        for entry in result:
            #print( table+'||'+','.join([str(i) for i in entry]) )
            data.append( table+'||'+'|'.join([str(i) for i in entry]) )
noin = len(data)
if noin == 0 :
    print 0,0
else:
    values['data'] = '||||'.join(data)
    url = 'http://'+domain+'/raspberry/receive.php'
    para = urllib.urlencode(values)
    req = urllib2.Request(url, para)
    response = urllib2.urlopen(req)
    output = response.read()
    print noin, output
    response.close()
