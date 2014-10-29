#! /usr/bin/python
# -*- coding: utf-8 -*-
# input id and (start - end date), dump measurement results from web_perf into a txt file for matlab processing

import socket, time, sys, MySQLdb, os
from collections import defaultdict
pm1=MySQLdb.connect(host='localhost',user='root',db='raspberry')
cur1=pm1.cursor()
cur1.execute("select id, type from ipv6server")
result = cur1.fetchall()
types={}
types_count = defaultdict(int)
rtt = defaultdict(list)
for i in result:
    types[i[0]] = i[1]
#cur1.execute("select lossrate from web_perf where time>'20140317' and lossrate>=0")
total = cur1.execute("select id, bandwidth, maxbw, latency, lossrate, hour(time) from web_perf6 where time>'20140717' and hour(time)>8 and hour(time)<23 and latency>0 and latency<600 and lossrate>=0 and bandwidth<12000000")
result = cur1.fetchall()
'''
#print latency from all websites
count = 1
for i in result:
    print i[1],i[2],i[3],i[4],i[5]
    count += 1
    #approximately a week
    if(count>43000):
        break
exit()
'''
#print performance from websites by type
for i in result:
    if(i[0] in types):
        #print i[1], types[i[0]]
        types_count[types[i[0]]] += 1
        rtt[types[i[0]]].append(str(i[1])+' '+str(i[2])+" "+str(i[3])+" "+str(i[4])+' '+str(i[5]))
wait_list = []
for i in types_count:
    if(types_count[i]> total/10):
        wait_list.append(i)
wait_list = sorted(wait_list)
length = [len(rtt[i]) for i in wait_list]
print ','.join([str(i) for i in wait_list])
print ','.join([str(i) for i in length])
for j in wait_list:
    for i in rtt[j]:
        print i
