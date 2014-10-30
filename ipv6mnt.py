#! /usr/bin/python
# download webpage using wget, estimate latency with hping3

import os, time, glob, sys, subprocess, shlex, logging
import MySQLdb, dns.resolver, maxminddb
from webcrawl import *
from collections import defaultdict
from random import shuffle

version = 6
if 0==connect_detection(version):
    exit()

verbose = logging.INFO
dirname, filename = os.path.split(os.path.abspath(sys.argv[0]))

logger = logging.getLogger('Main'+str(version))
formatter = logging.Formatter('%(name)s %(levelname)s %(message)s')
nameprefix = str(version)+time.strftime("%Y%m%d%H")
logfile = dirname+'/log.ipv'+str(version)+'.'+nameprefix[1:-2]
hdlr = logging.handlers.RotatingFileHandler( logfile )
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(verbose)
strtime = time.strftime("%Y-%m-%d %H:%M:%S")
starter = "Main thread started @ "+strtime+'\n'
stime = time.time()
pm2=MySQLdb.connect(host='127.0.0.1',user='root',db='raspberry')
cur2=pm2.cursor()

cur2.execute("select id from ipv"+str(version)+"server ")
idlist1 = [ i[0] for i in cur2.fetchall()]
shuffle(idlist1)

fast = webperf(idlist1, version, nameprefix+'MB', verbose)
fast.start()
fast.join()

etime = time.time()
logger.info( starter )

filelist = [dirname+'/tmp.'+nameprefix+'MB'] 
for fname in filelist:
    with open(fname,'r') as fh:
        logger.info( fh.read() )
    os.remove(fname)

try:
    with open(dirname+'/code') as fh:
        code = fh.readline().rstrip()
        #print code
except:
    logger.error( 'Failed to open code file')
    exit(1)
verbose = logging.INFO
bw = defaultdict(list)
rtt = defaultdict(list)
loss = defaultdict(list)
cur2.execute("select id, ip, asn, webdomain, time, bandwidth, pagesize, latency, lossrate, maxbw, type from web_perf{0} where time > '{1}'".format(str(version), strtime))
result = cur2.fetchall()
for entry in result:
    if(entry[9]>0 and entry[6]>200000):
        bw[entry[10]].append(1/entry[9])
        bw['overall'].append(1/entry[9])
    if(entry[7]>0):
        rtt[entry[10]].append(entry[7])
        rtt['overall'].append(entry[7])
    if(entry[8]>=0):
        loss[entry[10]].append(entry[8])
        loss['overall'].append(entry[8])
for key in bw:
    avgbw = len(bw[key])/sum(bw[key])
    cur2.execute("insert into avgbw{0} values('{1}', '{4}',{2}, '{3}')".format(str(version), code, avgbw, key, strtime))
for key in rtt:
    avgrtt = sum(rtt[key])/len(rtt[key])
    cur2.execute("insert into avgrtt{0} values('{1}', now(),{2}, '{3}')".format(str(version), code, avgrtt, key))
for key in loss:
    avgloss = sum(loss[key])/len(loss[key])
    cur2.execute("insert into avgloss{0} values('{1}', now(),{2}, '{3}')".format(str(version), code, avgloss, key))
pm2.commit()
cur2.close(); pm2.close()


logger.info( "Main thread done @ "+time.strftime("%Y-%m-%d %H:%M:%S")+" Total time: "+str(etime-stime)+" secs\n\n")
