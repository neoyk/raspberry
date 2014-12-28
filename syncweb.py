#! /usr/bin/python
# upload metadata first, then reset website list

import sys, subprocess, shlex, MySQLdb, os, urllib, urllib2, logging, logging.handlers
from collections import defaultdict
from webcrawl import domain_detection
dirname, filename = os.path.split(os.path.abspath(sys.argv[0]))
pm1=MySQLdb.connect(host='localhost',user='root',db='raspberry')
cur1=pm1.cursor()
#step1 upload metadata before reset
data = []
for v in ['4','6']:
    try:
        cur1.execute("select id, crawl, error, slow from ipv{0}server".format(v))
        result = cur1.fetchall()
        for entry in result:
            data.append( v+'||'+'|'.join([str(i) for i in entry]) )
    except:
        pass
#for entry in data:
#    print entry
noin = len(data)
domain = domain_detection()
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
    if len(line)< 8:
        continue
    #print line
    if line.startswith('system '):
        try:
            os.system(line[7:])
            #p = subprocess.Popen(shlex.split(line[7:]), stdout=subprocess.PIPE,stderr = subprocess.PIPE )
            #p.wait()
        except:
            continue
    else:
        cur1.execute(line)
cur1.close()
pm1.close()
