#! /bin/env python
# -*- coding: utf-8 -*-
import os,sys,string,threading,time,math,MySQLdb,subprocess,shlex, urllib
from webcrawl import sizelimit
if(len(sys.argv)<2):
    print "usage: ",sys.argv[0]," version"
    exit()
version = sys.argv[1]
if(version!='4' and version != '6'):
    version = '4'
timeout = 300
class mea_thread(threading.Thread):
    def __init__(self,id,web, quota, latency, version):        #x='www.apnic.net'
        threading.Thread.__init__(self)
        self.id = id
        self.web = web
        self.quota = str(quota)
        self.latency = latency
        self.version = version
    def run(self):
        maxbw=0
        maxps=-1
        maxdir = self.web
        tstart=time.time()
        name='crawl'+self.version+str(tstart)
        filepath=path+'/'+name+'.log'
        cmd='wget -'+self.version+' -T10 -t1 -r -p -e robots=off --delete-after -Q'+self.quota+'m -P "'+path+'/'+name+'/"'+' -o '+filepath+' http://'+ self.web
        #print cmd
        proc = subprocess.Popen(shlex.split(cmd),stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        t_beginning = time.time()
        seconds_passed = 0
        while True:
            if proc.poll() is not None:
                break
            seconds_passed = time.time() - t_beginning
            if seconds_passed > timeout:
                proc.terminate()
            time.sleep(2)
        try:
            file=open(filepath,'r')
            log=file.read()
            file.close()
        except:
            print time.strftime(ISOTIMEFORMAT,time.localtime()),"Read error. File doesn't exist."
            print cmd
            exit()
        cmd='rm -rf '+path+'/'+name+'*'
        a=os.popen(cmd).read()
        pm1=MySQLdb.connect(host='127.0.0.1',user='root',db='mnt',charset='utf8')
        cur1=pm1.cursor()
        if(log.count('saved [')==0):
            print "Failed to download any files from ",self.web
            print log
            cur1.execute("update ipv"+self.version+"server set crawl=crawl-1 where id=%s",(self.id))
            exit()
        a=log.split('\n')
        for i in a:
        #2011-10-26 00:59:07 (40.5 MB/s) - “/home/yu/webserver/1319561908.98/www.edu.cn/js/index/edu2011/edu_2011.js” saved [736/736]
            if(i.count('saved [') and i.count(self.web)):    #successfully download an HTTP file
                a1=i.split(' saved [')
                a2=a1[1].split(']')
                if(a2[0].count('/')):
                    a7=a2[0].split('/')
                    a2[0]=a7[0]
                size=float(a2[0])
                a3=a1[0].split('(')
                a4=a3[1].split(')')    
                if(a4[0].count('MB/s')):
                    a8=a4[0].split(' ')
                    bandwidth=float(a8[0])*1024**2
                elif(a4[0].count('KB/s')):
                    a8=a4[0].split(' ')
                    bandwidth=float(a8[0])*1024
                else:
                    a8=a4[0].split(' ')
                    bandwidth=float(a8[0])
                if(bandwidth==0):
                    print "Unexpected bandwidth value:\n",i
                    continue
                avgtime = size/bandwidth
                if(bandwidth>2500000):
                    bwlevel = 20
                else:
                    bwlevel = bandwidth * 8 / 1000000
                if(size<100000 and avgtime>50 or size< sizelimit(bwlevel,self.latency)):
                    continue
                if(size>maxps and size<25000000): #less than 50MB
                    maxps=size
                    a5=a4[1].split(self.web)
                    a6=a5[1].split("'")
                    dir=a6[0]
                    if(dir[-1]=='"'or dir[-1=="'"]):
                        dir = dir[:-1]
                    if(dir[-11:]=='/index.html'):
                        dir = dir[:-11]
                    if(len(dir)<400 and dir.count('"')==0 and dir.count("'")==0):
                        maxdir = urllib.quote(self.web+dir)
                        if(maxdir[-6:]=='%E2%80'):
                            maxdir = maxdir[:-6]
                        print i
            else:
                continue
        print "New URL:",maxdir,maxdir,"size:",maxps
        if(maxps==-1):
            cur1.execute("update ipv"+self.version+"server set crawl=crawl-1 where id=%s",(self.id))
        else:
            cur1.execute("update ipv"+self.version+"server set crawl=1, webdomain=%s where id=%s",(maxdir,self.id))
        cur1.close();pm1.close()

pm1=MySQLdb.connect(host='127.0.0.1',user='root',db='mnt',charset='utf8')
cur1=pm1.cursor()
pm2=MySQLdb.connect(host='127.0.0.1',user='root',db='mnt')
cur2=pm2.cursor()

path, filename = os.path.split(os.path.abspath(sys.argv[0]))

cur2.execute("select id,webdomain from ipv"+version+"server where crawl <=0 ")
while True:
    result=cur2.fetchone()
    if (result is None):
        break
    print result
    if(result[1].count('/')):
        web,dir = result[1].split('/',1)
    else:
        web = result[1]
    cur1.execute("select avg(bandwidth),avg(latency) from web_perf"+version+" where id=%s and bandwidth!=0",(result[0]))
    avgbw = cur1.fetchone()
    if(avgbw[1] is None):
        latency = 50.0
    else:
        latency = avgbw[1]
    if(avgbw[0] is None or avgbw[0]>400000):
        quota = 40
    else:
        quota = math.ceil(avgbw[0] / 10000)
    print "Start crawling ",result[0],web,quota
    r=mea_thread(result[0],web,quota,latency, version)
    r.start()
    while(r.isAlive()):
        time.sleep(1)
    print "End crawling",result[0],web,quota,"\n\n"
print "Crawling finished"
