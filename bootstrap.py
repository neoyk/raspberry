#! /usr/bin/python

import socket, time, sys, MySQLdb, os, urllib, urllib2, logging, logging.handlers
from collections import defaultdict
from webcrawl import connect_detection
dirname, filename = os.path.split(os.path.abspath(sys.argv[0]))
pm1=MySQLdb.connect(host='localhost',user='root',db='test')
cur1=pm1.cursor()
domain = domain_detection()
url = 'http://'+domain+'/raspberry/bootstrap.php'
req = urllib2.Request(url)
response = urllib2.urlopen(req)
output = response.read()
for line in output.split('\n'):
    #print line
    cur1.execute(line)
cur1.close()
pm1.close()
