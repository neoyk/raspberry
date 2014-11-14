#! /usr/bin/python

import socket, time, sys, MySQLdb, os, urllib, urllib2, logging, logging.handlers
from collections import defaultdict
from webcrawl import connect_detection
dirname, filename = os.path.split(os.path.abspath(sys.argv[0]))
pm1=MySQLdb.connect(host='localhost',user='root',db='test')
cur1=pm1.cursor()
if 0==connect_detection(6):
    domain = '115.25.86.4'
else:
    domain = 'perf.sasm3.net'
url = 'http://'+domain+'/raspberry/bootstrap.php'
req = urllib2.Request(url)
response = urllib2.urlopen(req)
output = response.read()
for line in output.split('\n'):
    #print line
    cur1.execute(line)
cur1.close()
pm1.close()
