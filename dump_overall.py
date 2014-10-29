#! /usr/bin/python
# -*- coding: utf-8 -*-
# input id and (start - end date), dump measurement results from web_perf into a txt file for matlab processing

import socket, time, sys, MySQLdb, os
from collections import defaultdict
pm1=MySQLdb.connect(host='localhost',user='root',db='raspberry')
cur1=pm1.cursor()
cur1.execute("select ipv4server.id,type,substring(location,1,locate(',',location)-1),aspath,floor(avg(web_perf4.pagesize)) as pagesize, floor(avg(web_perf4.bandwidth))as bw from web_perf4 join ipv4server on web_perf4.id=ipv4server.id  group by id order by type,bw")
result = cur1.fetchall()
for entry in result:
    print ','.join([str(i) for i in entry])
