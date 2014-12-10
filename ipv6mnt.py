#! /usr/bin/python
# download webpage using wget, estimate latency with hping3

import os, time, glob, sys, subprocess, shlex, logging
import MySQLdb, dns.resolver, maxminddb
from webcrawl import *
from collections import defaultdict
from random import shuffle

version = 6
if 0==connect_detection(version):
    print "No IPv6 connection detected. Starting Openvpn"
    os.system("/usr/sbin/service openvpn start")
    exit()

if 1==vpn_detection():
    print "Openvpn detected. Quiting"
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

mac = mac_addr()

verbose = logging.INFO
bw = defaultdict(list)
bwreal = defaultdict(list)
rtt = defaultdict(list)
loss = defaultdict(list)
statistics = []
cur2.execute("select id, ip, asn, webdomain, time, bandwidth, pagesize, latency, lossrate, maxbw, type from web_perf{0} where time > '{1}'".format(str(version), strtime))
strtime = time.strftime("%Y-%m-%d %H:%M:%S")
result = cur2.fetchall()
for entry in result:
    if(entry[5]>0 and entry[6]>200000):
        bw[entry[10]].append(1/entry[5])
        bw['overall'].append(1/entry[5])
        bwreal[entry[10]].append(entry[5])
        bwreal['overall'].append(entry[5])
    if(entry[7]>0):
        rtt[entry[10]].append(entry[7])
        rtt['overall'].append(entry[7])
    if(entry[8]>=0):
        loss[entry[10]].append(entry[8])
        loss['overall'].append(entry[8])
for key in bw:
    avgbw = len(bw[key])/sum(bw[key])
    vmin = min(bwreal[key])
    vmax = max(bwreal[key])
    vmean, stdv = meanstdv(bwreal[key])
    cur2.execute("insert into avgbw{0} values('{1}', '{4}',{2}, '{3}')".format(str(version), mac, vmean, key, strtime))
    statistics.append('bw|{0}|{1}|{2}|{3}|{4}'.format(  key, vmin, vmax, vmean, stdv))
for key in rtt:
    avgrtt = sum(rtt[key])/len(rtt[key])
    cur2.execute("insert into avgrtt{0} values('{1}', now(),{2}, '{3}')".format(str(version), mac, avgrtt, key))
    vmin = min(rtt[key])
    vmax = max(rtt[key])
    vmean, stdv = meanstdv(rtt[key])
    statistics.append('rtt|{0}|{1}|{2}|{3}|{4}'.format(  key, vmin, vmax, vmean, stdv))
for key in loss:
    avgloss = sum(loss[key])/len(loss[key])
    cur2.execute("insert into avgloss{0} values('{1}', now(),{2}, '{3}')".format(str(version), mac, avgloss, key))
    vmin = min(loss[key])
    vmax = max(loss[key])
    vmean, stdv = meanstdv(loss[key])
    statistics.append('loss|{0}|{1}|{2}|{3}|{4}'.format(  key, vmin, vmax, vmean, stdv))
pm2.commit()
cur2.close(); pm2.close()
with open(dirname+'/current-'+str(mac)+'-'+str(version),'w') as fh:
    fh.write(strtime+'||||'+'||'.join(statistics))
logger.info( "Main thread done @ "+time.strftime("%Y-%m-%d %H:%M:%S")+" Total time: "+str(etime-stime)+" secs\n\n")
