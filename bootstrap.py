#! /usr/bin/python

import socket, time, sys, MySQLdb, os, urllib, urllib2, logging, logging.handlers
from collections import defaultdict
dirname, filename = os.path.split(os.path.abspath(sys.argv[0]))
pm1=MySQLdb.connect(host='localhost',user='root',db='test')
cur1=pm1.cursor()
url = 'http://perf.sasm3.net/raspberry/bootstrap.php'
req = urllib2.Request(url)
response = urllib2.urlopen(req)
output = response.read()
for line in output.split('\n'):
    #print line
    cur1.execute(line)
cur1.close()
pm1.close()
