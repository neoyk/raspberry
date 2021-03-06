#! /usr/bin/python
# upload metadata first, then reset website list

import sys, subprocess, shlex, MySQLdb, os, urllib, urllib2, logging, logging.handlers
from collections import defaultdict
from webcrawl import connect_detection
dirname, filename = os.path.split(os.path.abspath(sys.argv[0]))
pm1=MySQLdb.connect(host='localhost',user='root',db='raspberry')
cur1=pm1.cursor()
#step1 upload metadata before reset
data = []
for v in ['4','6']:
    cur1.execute("select id, crawl, error, slow from ipv{0}server".format(v))
    result = cur1.fetchall()
    for entry in result:
        data.append( v+'||'+'|'.join([str(i) for i in entry]) )
#for entry in data:
#    print entry
noin = len(data)
if 0==connect_detection(6):
    domain = '115.25.86.4'
else:
    domain = 'perf.sasm3.net'
if noin :
    values= {'data' : '||||'.join(data) }
    url = 'http://'+domain+'/raspberry/meta_receive.php'
    para = urllib.urlencode(values)
    req = urllib2.Request(url, para)
    response = urllib2.urlopen(req)
    output = response.read()
    print "Meta uploaded:", noin, output
    response.close()
#step2 reset website list
url = 'http://'+domain+'/raspberry/bootstrap.php'
req = urllib2.Request(url)
response = urllib2.urlopen(req)
output = response.read()
for line in output.split('\n'):
    #print line
    if line.startswith('system '):
        try:
            subprocess.Popen(shlex.split(line[7:]), stdout=subprocess.PIPE,stderr = subprocess.PIPE )
        except:
            continue
    else:
        cur1.execute(line)
cur1.close()
pm1.close()
