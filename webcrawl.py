#! /bin/env python
# -*- coding: utf-8 -*-
import os,sys,threading,time,re,shlex,subprocess,urllib,urlparse, logging, logging.handlers, glob, signal, locale, math, uuid, urllib2
import MySQLdb, maxminddb, IPy
import dns.resolver #install dnspython first http://www.dnspython.org/

ISOTIMEFORMAT='%Y-%m-%d %X'
dirname, _ = os.path.split(os.path.abspath(sys.argv[0]))
geo = maxminddb.Reader(dirname+'/../topology/GeoLite2-City.mmdb')

def aspath(ip,version=4):
    return 'N/A'
    if(version==6):
        cmd='expect '+dirname+'/quagga-com 115.25.86.11 bgpd "sh ipv6 bgp '+ip+'"'
    else:
        cmd='expect '+dirname+'/quagga-com 115.25.86.11 bgpd "sh ip bgp '+ip+'"'
    try:
        a = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE,stderr = subprocess.PIPE )
    except:
        return 'N/A'
    out  = a.stdout.read()
    info = out.split('\n')
    path = 'N/A'
    for i in info:
        if((version==4 and i.count("202.112.60.243 from 202.112.60.243 (202.112.60.243)")) or ( version==6 and i.count("2001:250:0:1::3 from 2001:250:0:1::3 (202.112.60.247)") ) ):
            path = info[info.index(i)-1].lstrip().rstrip()
            if(path.count(',')):
                info = path.split(',')
                path = info[0]
    # remove duplicates preserve order
    seen = set()
    aslist = path.split(' ')
    return ' '.join([x for x in aslist if x not in seen and not seen.add(x)])

def burstdetect(totalpacket,loss):
    Prandom = 1e-4
    if(totalpacket<loss or loss==0):
        return 0
    cmn = math.factorial(totalpacket) / math.factorial(loss) / math.factorial(totalpacket-loss)
    P = cmn * Prandom**loss * (1-Prandom)**(totalpacket-loss)
    if(P<Prandom):
        return 1
    else:
        return 0

def bwftop(bw):
    "change bw from float to string with proper unit"
    if(bw>1024**2):
        p = str(round(bw/1024**2,2))+' mbps'
    elif(bw>1024):
        p = str(round(bw/1024,2))+' kbps'
    elif(bw>0):
        p = str(round(bw,2))+' bps'
    else:
        p = 'NA'
    return p

def connect_detection(version=4):       
    domainlist=['www.cernet2.edu.cn', 'www.google.com','www.akamai.com']
    for domain in domainlist:
        con, _, _, _ = rttmeasure(domain,version)
        if con:
            return True
    return False

def domain_detection():
    if connect_detection(6):
        return 'perf.sasm3.net'
    con, _, _, _ = rttmeasure('2001:da8:243:8601::1',6)
    if con:
        return '2001:da8:243:8601::864'
    else:
        domain = '115.25.86.4'

def vpn_detection():       
    con, _, _, _ = rttmeasure('10.8.0.1',4)
    if con:
        return True
    return False

def dnslookup(querydomain,type='A'):
    #only for IP addr to ASN mapping
    type=type.upper()
    response=[]
    resolver = dns.resolver.Resolver()
    try:
        answer=resolver.query(querydomain,type)
    #except dns.exception.DNSException:
    except:
        #Local DNS may return "NXDOMAIN" error, if this happens, pathperf queries authoritative DNS server for answer
        try:
            resolver.nameservers=['115.25.86.11']
            answer=resolver.query(querydomain,type)
        except:
            return 'N/A'
    #dir(answer)
    if(type=='A' or type=='AAAA'):
        response.append(str(answer.response.answer[0][0]))  #CNAME
        response.append(str(answer.response.answer[1][0]))  #A/AAAA
        return response
    if(type=='TXT'):
        response.append(str(answer.response.answer[0][0]))  #ASN or URL
        return response

def ip2asn(ip,version=4):
    if(version==4):
        ip2list = ip.split('.')
        ip2list.reverse()
        domain='.'.join(ip2list)+'.ip2asn.sasm4.net'
    elif(version==6):
        ipt = IPy.IP(ip)
        ipfull = ipt.strFullsize(0)
        ip2list = ipfull.split(':')
        ip2list.reverse()
        domain='.'.join(ip2list)+'.ip6asn.sasm4.net'
    else:
        return "Wrong IP version"
    asn=dnslookup(domain,'txt')
    asn=asn[0].replace('"','')
    if(asn.count('23456')): # 4 bytes ASN
        return ip2origin(ip,version)
    else:
        return asn.upper()

def ip2origin(ip,version=4):
    if(version==4):
        ip2list = ip.split('.')
        ip2list.reverse()
        domain='.'.join(ip2list)+'.origin.asn.cymru.com'
    elif(version==6):
        ipt = IPy.IP(ip)
        ipfull = ipt.strFullsize(0).replace(':','')
        ip2list = [n for n in ipfull]
        ip2list.reverse()
        domain='.'.join(ip2list)+'.origin6.asn.cymru.com'
    else:
        return "Wrong IP version"
    asn=dnslookup(domain,'txt')
    asn=asn[0].replace('"','').split('|')[0]
    if asn.startswith('23456 '):
        asn = asn[6:]
    #text = "198171 | 2a03:b780::/32 | CZ | ripencc | 2011-10-25"
    return 'AS'+asn.rstrip()

def downloader(domain,directory,pattern, version = 4):
    try:
        response = urllib2.urlopen(url='http://'+domain+directory,timeout=10)
        data = response.read()
        #conn.close()
        m = re.search(pattern,data)
        if m:
            return True,m.group(1),ip2asn(m.group(1), version)
    except:
        pass
    if version==4:
        return False,'0.0.0.0','NO RECORD'
    else:
        return False,'::','NO RECORD'

def mac_addr():
    mac_int = uuid.getnode()
    if (mac_int>>40)%2:
        mac = '0'*12
    else:
        mac = '{0:012x}'.format(mac_int)
    return mac

def meanstdv(x):
    if len(x)==0:
        return 0,0
    from math import sqrt
    n, mean, std = len(x), 0, 0
    for a in x:
        mean = mean + a
    mean = mean / float(n)
    for a in x:
        std = std + (a - mean)**2
    if n==1:
        std = 0
    else:
        std = sqrt(std / float(n-1))
    return mean, std

def rttmeasure(domain,version=4):
    # accpet as input both domain and ip address
    succeed=0
    rtt_list = []
    errmsg = ''
    if(version==4):
        ip = '0.0.0.0'
        cmd = '/usr/sbin/hping3 -S -p 80 -c 5 --fast '+ domain
        p1 = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        p1.wait()
        log = p1.stdout.read()
        if(log.count('Unable to resolve')):
            return (0,'0.0.0.0',-1,'Unable to resolve IP address')  #success, ipaddr, rtt
        m = re.findall('len=.*ip=(.*)\sttl=(\d+)\s.*rtt=(.*)\sms',log)
        if m:
            succeed=1
            rtt_list = [ float(i[2]) for i in m ]
        rtt_list = sorted(rtt_list)
        if(rtt_list and rtt_list[len(rtt_list)/2]==0):
            errmsg += "hping3 failed: "+cmd+'\n'+log+'\n'
            succeed = 0
        if (succeed==0):
            cmd = '/bin/ping -n -c 5 '+ domain
            p1 = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            p1.wait()
            log = p1.stdout.read()
            m = re.findall('\d+ bytes from\s(.*):\s.*ttl=(\d+)\stime=(.*)\sms',log)
            if m:
                succeed=1
                rtt_list = [ float(i[2]) for i in m ]
    if(version==6):
        ip = '::'
        cmd = '/bin/ping6 -n -c 5 '+ domain
        p1 = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        p1.wait()
        log = p1.stdout.read()
        if(log.count('unknown host')):
            return (0,'::',-1,'Unable to resolve IP address')
        m = re.findall('\d+ bytes from\s(.*):\s.*ttl=(\d+)\stime=(.*)\sms',log)
        if m:
            succeed=1
            rtt_list = [ float(i[2]) for i in m ]
    if(succeed): 
        rtt_list = sorted(rtt_list)
        if(rtt_list[len(rtt_list)/2]==0):
            errmsg += "RTT estimation failed: "+cmd+'\n'+log+'\n'
            return (0,ip,-1,errmsg)
        return (1,ip,rtt_list[len(rtt_list)/2], errmsg)
    else:
        return (0,ip,-1, errmsg)

def sizelimit(bw, rtt):
    """calculate minimum pagesize to reach a certain bw(in mbps) for a certain RTT(in ms)"""
    if(bw<0 or rtt<0):
        return 100000
    if(rtt>300):
        rtt = 300
    MSS = 1460.0
    Wmax = bw * rtt * 128 / MSS
    Tss = 2*bw*rtt*128 - MSS # (2Wmax-1)*MSS
    Tcubic = 1.26 * (bw * rtt * 128)**(4/3.0) / MSS**(1.0/3)
    return Tss+Tcubic

class webperf(threading.Thread):
    def __init__(self,idlist, version, name, verbose = logging.INFO ):
        threading.Thread.__init__(self)
        self.mac = mac_addr()
        self.idlist = idlist
        if(version!=4 and version !=6):
            version = 4
        self.version = version
        self.pm1=MySQLdb.connect(host='localhost',user='root',db='raspberry',charset='utf8')
        self.cur1 = self.pm1.cursor()
        self.errorcount = 0
        self.setName(name)
        self.logger = logging.getLogger(name)
        formatter = logging.Formatter('%(name)s %(levelname)s %(message)s')
        if(name.count('Test')):
            self.hdlr = logging.handlers.RotatingFileHandler(dirname+'/log.test.ipv'+str(version)+'mnt')
            self.hdlr.setFormatter(formatter)
            self.logger.addHandler(self.hdlr) 
            self.logger.setLevel(verbose)
        else:
            self.hdlr = logging.handlers.RotatingFileHandler(dirname+'/tmp.'+name)
            self.hdlr.setFormatter(formatter)
            self.logger.addHandler(self.hdlr) 
            self.logger.setLevel(verbose)
    
    def __del__(self):
        self.cur1.close()
        self.pm1.close()
    
    def insertfailure(self,webid,webdomain):
        if(self.version==6):
            ip = '::'
        else:
            ip = '0.0.0.0'
        self.cur1.execute("insert into web_perf"+str(self.version)+" values(%s, %s, %s, 'AS0', %s, now(), 0, 0, 0, -1, -1, 0, %s)",(self.mac, webid, ip, webdomain, self.wtype))
        self.cur1.execute("update ipv"+str(self.version)+"server set error=error-1,performance='N/A' where id = %s",( webid, ))

    def ipchange(self,webid,ip,asn):
        path = aspath(ip, self.version)
        if (path == 'N/A'):
            self.logger.warning("AS path lookup failed:"+ip)
        record=geo.get(ip)
        if(record is not None):
            if 'city' in record.keys():
                city = record['city']['names']['en']+', '
            else:
                city = ''
            if 'country' in record.keys():
                city += record['country']['names']['en']+', '
            if 'continent' in record.keys():
                city += record['continent']['names']['en']
            if(city==''):
                city = 'N/A'
            #city = city.encode('utf8')
            if(record.keys().count('location')==0):
                record['location'] = {'latitude':0,'longitude':0}
            self.logger.info( "{0} {1} {2} {3}".format(ip,city.encode('utf8'),record['location']['latitude'], record['location']['longitude']))
            self.cur1.execute("update ipv"+str(self.version)+"server set asn=%s,ip=%s, location=%s, latitude=%s, longitude=%s,aspath=%s where id = %s",( asn, ip, city, record['location']['latitude'], record['location']['longitude'],path, webid))
        else:   #no geolocation info available
            self.cur1.execute("update ipv"+str(self.version)+"server set asn=%s,ip=%s, location='N/A',longitude=0,latitude=0, aspath=%s where id = %s",( asn, ip, path, webid ))

    def wgetip(self,log):
        if self.wtype.startswith('C'):
            m = re.findall("Connecting to (\d+\.\d+\.\d+\.\d+).* connected.",log)
        else:
            m = re.findall("Connecting to [^\|]+\|([^|]+).* connected.",log)
        if(m):
            ip = m[-1]
            asn = ip2asn(ip,self.version)    
            return (ip, asn)
        else:
            if(self.version==6):
                ip = '::'
            else:
                ip = '0.0.0.0'
            return (ip,'AS0')
    def tsharkparse(self,packets,latency,ip):
        #calculate instantaneous bw using tshark
        #fast_retransmission vs lost_segment: fast_retransmission may underestimate loss rate due to fail to indntify all duplicate acks, lost_segment may overestimate loss rate due to bursty losses during congestion
        tsharkfile = packets+'tshark'
        if(self.version==6):
            tshark = "/usr/sbin/tshark -q -r "+packets+' -z io,stat,100,"ipv6.src=='+ip+'","tcp.analysis.retransmission" '
        else:
            tshark = "/usr/sbin/tshark -q -r "+packets+' -z io,stat,100,"ip.src == '+ip+'","tcp.analysis.retransmission" '
        if(latency>0):
            if latency<5:
                latency = 5.0
            tshark = tshark.replace('io,stat,100','io,stat,'+str(latency/1000.0))
        else:
            tshark = tshark.replace('io,stat,100','io,stat,0.4')
        self.logger.info(tshark)
        c = subprocess.Popen(shlex.split(tshark), stdout=open(tsharkfile,'w'), stderr = subprocess.PIPE)
        c.wait()
        log = open(tsharkfile,'r').read()
        self.logger.info(log)
        if(log.count("appears to be damaged or corrupt")):
            self.logger.warning("Damaged pcap file detected.")
            return (0,0,0,0,-1)
        m = re.search("Interval.*:(.*) secs",log)
        if(m):
            interval = float(m.group(1))
        else:
            interval = 0
            self.errorcount += 1
            self.logger.warning("errorcount: Unable to determine interval")
        m = re.findall("\d+\.\d+[ -<>]+\d+\.\d+\s.*\s(\d+)\s.*\s(\d+)\s.*\s(\d+)\s.*\s\d+\s",log)
        #m = re.search("\d+\.\d+[ -<>]+\d+\.\d+\s.*\s(\d+)\s.*\s(\d+)\s.*\s(\d+)\s.*\s\d+\s",log)
        maxbw = 0
        avgbw = 0
        bwlist = []
        maxdata = 0 # the maximum data block in one bulk transfer (between two dull intervals)
        curdata = 0 # the current data block
        totaldata = 0
        lossrate = -1
        actual_loss = -1
        serverslow = 0 # 1: slow, 0 not slow, -1 bursty loss detected -> server fast enough and pagesize large enough
        if(interval and len(m)):
            lossinterval = 0
            losscount = 0
            lossbeforedull = 0 #boolean
            totalpacket = 0
            nopacket = 0 # # of consective intervals without any data 
            datastart = 0 # the first few packets contain only token such as HTTP 200, 304, start calculating only after data transfer
            for i in xrange(len(m)):
                packetcount = int(m[i][0])
                datasize = float(m[i][1])
                losspacket = int(m[i][2])
                if( packetcount ==0 and datasize>0):
                    continue
                if((datastart==0 and packetcount == 0) or (datastart==0 and datasize/packetcount<300)):
                    continue
                else:
                    datastart = 1
                totaldata += datasize
                curdata += datasize
                totalpacket += packetcount
                if(nopacket==0):  # packet loss two intervals ago can cause server timeout
                    if(i>1 and m[i-2][2]!='0'):
                        lossbeforedull = 1
                    else:
                        lossbeforedull = 0
                if(serverslow != -1 and packetcount==0 and 0==lossbeforedull): # count consective dull intervals only when no packet loss happened two RTT before
                    nopacket += 1
                    if(nopacket>1): # two intervals without data leads to the decision of a slow server
                        serverslow = 1
                        if(curdata>maxdata):
                            maxdata = curdata
                        curdata = 0
                else:
                    nopacket = 0
                if(losspacket>0):
                    lossinterval += 1
                    losscount += losspacket
                    if(burstdetect(packetcount, losspacket)==1):
                        serverslow = -1
                        self.logger.warning("Bursty loss detected")
                else:
                    # if there is packet loss in every interval then maxbw = 0
                    bwnow = 8*datasize/interval *1460/1514.0
                    bwlist.append(bwnow)
                    if(bwnow>maxbw):
                        maxbw = bwnow
                self.logger.debug( (m[i],nopacket,curdata,maxdata,serverslow,totaldata) )
            if(curdata>maxdata):
                maxdata = curdata
            if(totalpacket):
                actual_loss = 100.0*losscount/totalpacket
                lossrate = 100.0*lossinterval/totalpacket
            if(bwlist):
                avgbw = sum(bwlist)/len(bwlist)
            totaldata = totaldata *1460 / 1514.0 # payload / packet length
            self.logger.info( "interval: {0}, totalpackets: {1}, totaldata:{2}, maxbw:{3}, avgbw:{4}, maxdata:{5}, lossrate:{6}, actual lossrate:{7}, serverslow:{8}".format(interval,totalpacket,totaldata,maxbw, avgbw, maxdata,lossrate,actual_loss,serverslow) )
        return (totaldata, maxdata, maxbw, avgbw, serverslow, lossrate, actual_loss)

    def perfsuccess(self, webid, webdomain, ip, asn, pagesize, oldpagesize, bandwidth, maxbw, latency, lossrate, actual_loss, serverslow):
        peak = bwftop(maxbw)
        avgbw = bwftop(bandwidth)
        perf = "Page size: "+locale.format("%d",pagesize, grouping=True)+"B, BTC: "+avgbw+'(peak:'+peak+"), RTT: "+str(latency)+"ms, lossrate: "+str(round(lossrate,2))+" % @ "+time.strftime("%Y-%m-%d %H:%M:%S")
        self.cur1.execute("update ipv"+str(self.version)+"server set performance=%s, bandwidth=%s where id = %s",(perf, maxbw, webid))
        if(pagesize>1.5*oldpagesize or pagesize*1.5<oldpagesize):
            self.cur1.execute("update ipv"+str(self.version)+"server set pagesize=%s where id = %s",(pagesize, webid))
        self.cur1.execute("insert into web_perf"+str(self.version)+" values(%s, %s, %s, %s, %s, now(), %s, %s, %s, %s, %s, %s, %s)",(self.mac, webid, ip, asn, webdomain, bandwidth, pagesize, latency, lossrate, actual_loss, maxbw, self.wtype))
        if(bandwidth>2500000 or maxbw>2500000): # Bps to bps to mbps
            bwlevel = 20
        else:
            bwlevel = maxbw * 8 / 1000000.0
        if(bandwidth ==0): #empty page
            self.cur1.execute("update ipv"+str(self.version)+"server set crawl=crawl-1 where id = %s",( webid, ))
        if(serverslow!=-1 and maxbw<2500000 and pagesize<sizelimit(bwlevel,latency)):
            self.logger.info( "pagesize not large enough")
            self.cur1.execute("update ipv"+str(self.version)+"server set crawl=crawl-1 where id = %s",( webid, ))
        else:
            self.cur1.execute("update ipv"+str(self.version)+"server set crawl=1 where id = %s",( webid, ))
            self.logger.info( "pagesize large enough")
        
    def run(self):
        dirname, filename = os.path.split(os.path.abspath(sys.argv[0]))
        name = dirname+'/'+self.getName()+'.'
        logpath = name+'wget.log'
        packets = name+'pcap'
        dumplog = name+'tcpdump.log'
        try:
            locale.setlocale(locale.LC_ALL, 'en_US')
        except:
            locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
        
        self.logger.info( " thread started @ "+time.strftime("%Y-%m-%d %H:%M:%S"))
        tstart = time.time()
        totalsize = 0
        #tcpdump to capture packets, wget to download webpage, tshark to analyze packet loss rate and peak bw
        for webid in self.idlist:
            self.cur1.execute("select webdomain,asn,ip,pagesize,type,location from ipv"+str(self.version)+"server where id= "+str(webid))
            result = self.cur1.fetchone()
            self.logger.info("Start: %s"%(result,) )
            try:
                webdomain = str(result[0])
                self.wtype = str(result[4])
                self.wip = str(result[2])
            except:
                self.logger.warning( "Wrong webdomain: "+str(webid))
                continue
            if result[5] is None and self.wtype.startswith('C'):
                asn = ip2asn(self.wip, self.version)
                self.ipchange(webid,self.wip,asn)
            #cmd='wget -vt 1 -T 10 -o $name/log.txt -O /home/yk/mnt/wget.html '+webdomain
            try:
                domain = webdomain.split('/',1)
                if self.wtype.startswith('C'):
                    snippet = result[2]
                else:
                    if(self.version==6):
                        answers = dns.resolver.query(domain[0], 'AAAA')
                    else:
                        answers = dns.resolver.query(domain[0], 'A')
                    snippet = ' or host '.join([i.to_text() for i in answers])
            except:
                self.logger.warning( "DNS resolve failed."+webdomain)
                self.insertfailure(webid, webdomain)
                continue
            webdomain = webdomain.replace("'","\\'")
            webdomain = webdomain.replace('"','\\"')
            if self.wtype.startswith('C'):
                wgetcmd = 'wget -{0} -vt 1 -T 10 -o {1} -O /dev/null --header="Host:{2}" {3}/{4}'.format(self.version, logpath, domain[0], self.wip, domain[1])
            else:
                wgetcmd = 'wget -'+str(self.version)+' -vt 1 -T 10 -o '+logpath+' -O /dev/null '+webdomain
            #wgetcmd = 'wget -'+str(self.version)+' -vt 1 -T 10 -U "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.89 Safari/537.1; 360Spider" -o '+logpath+' -O /dev/null '+webdomain
            wgettimeout = 25 # kill wget if it takes longer than 300 secs
            killed = 0
            tcpdump = "/usr/sbin/tcpdump -s 120 -i any -nn host "+snippet+" -w "+packets
            if(result[3]>1000000):
                tcpdump += " -B "+str(int(1.5*result[3]/1000))
            else:
                tcpdump += " -B 1500"
            self.logger.info( wgetcmd )
            self.logger.info( tcpdump )
            try:
                b = subprocess.Popen(shlex.split(tcpdump), stdout=subprocess.PIPE, stderr = open(dumplog,'w'))
                time.sleep(1.5)
                a = subprocess.Popen(shlex.split(wgetcmd))
                t_beginning = time.time()
                seconds_passed = 0 
                while True:
                    if a.poll() is not None:
                        break
                    seconds_passed = time.time() - t_beginning
                    if seconds_passed > wgettimeout:
                        a.terminate()
                        killed = 1 # killing wget may cause incomplete log, no bw, pagesize info in log 
                        self.logger.info( "wget timeout, subprocess terminated")
                    time.sleep(2)
                b.send_signal(signal.SIGINT)
                #b.kill()
                b.wait()
            except:
                self.logger.warning( "errorcount: Error in subprocess/shlex detected. %s"%(result,))
                self.errorcount += 1
                continue
            log = open(dumplog,'r').read()
            self.logger.info( log )
            m = re.search("(\d+) packets captured",log)
            success = 1
            if(m):
                total = int(m.group(1))
                if(total==0):
                    self.logger.warning("Tcpdump fails to capture any packets")
                    success = 0
            else:
                self.logger.warning( "Tcpdump fails")
                success = 0
            log = open(logpath,'r').read()
            self.logger.info( log )
            # Location: http://sports.bovada.lv/sportsbook/index.jsp [following]
            m = re.findall("Location.*://(.*)\s\[following\]",log)
            if(len(m)):
                webdomain = m[-1]
                if(webdomain.count('/')>1 and webdomain[-1]=='/'):
                    webdomain = webdomain[:-1]
                try:
                    self.cur1.execute("update ipv"+str(self.version)+"server set webdomain=%s where id = %s",( webdomain, webid ))
                except:
                    pass
                self.logger.info( "HTTP redirection found. Changing webdomain to "+webdomain)
            ip, asn = self.wgetip(log)
            #if self.wtype.startswith('C') and ip!='0.0.0.0' and ip != self.wip:
            if self.wtype.startswith('C') and ip != self.wip:
                self.logger.warning( "Multihoming measurement failed: IP address mismatch {0} {1}".format(ip, self.wip))
            _,_,latency, errmsg = rttmeasure(ip, self.version)
            if(errmsg != ''):
                self.logger.warning("RTT measure alert:")
                self.logger.warning(errmsg)
            if(ip!='127.0.0.1' and ip!='::' and result[2]!=ip and 0==self.wtype.startswith('C') ):
            #def ipchange(self,cur,webid,ip,asn):
                self.ipchange(webid,ip,asn)
            m = re.search("\((.*B\/s)\).*dev\/null.*saved \[(.*)\]",log)
            if(m):
                a7=m.group(2).split('/')
                pagesize=int(a7[0])

                a8=m.group(1).split(' ')
                if(a8[1].count('MB/s')):
                    bandwidth=8*float(a8[0])*(1024**2)
                elif(a8[1].count('KB/s')):
                    bandwidth=8*float(a8[0])*1024
                else:
                    bandwidth=8*float(a8[0])
                self.logger.info( "webid, ip, asn, webdomain, bandwidth, pagesize, latency:")
                self.logger.info( "%s"%((webid, ip, asn, webdomain, bandwidth, pagesize, latency),) )
                totalsize += pagesize
                if(success==0):
                    lossrate = -1
                    peak = 'N/A'
                    maxbw = bandwidth
                else:
                #def tsharkparse(self,packets,latency,ip, pagesize):
                #return (totaldata, maxdata, maxbw, serverslow, lossrate)
                    _, maxdata, maxbw, _ ,serverslow, lossrate, actual_loss = self.tsharkparse(packets, latency, ip)
                    if(maxdata<3*pagesize/4 and serverslow>0):
                        self.logger.warning( "slow server detected")
                        # no traffic during more than three intervals and maxbw < 2.5MBps
                        # indicates this website is too slow for link performance estimation
                        self.cur1.execute("update ipv"+str(self.version)+"server set slow=slow-1 where id = %s",( webid, ))

                    self.perfsuccess( webid, webdomain, ip, asn, pagesize, result[3], bandwidth, maxbw, latency, lossrate, actual_loss, serverslow)
                
                self.logger.info( "Finish successfully: %s\n"%(result,))
            elif(killed and success):
                totaldata, maxdata, maxbw, bandwidth, serverslow, lossrate, actual_loss = self.tsharkparse(packets, latency, ip)
                if(maxdata<3*totaldata/4 and serverslow>0):
                    self.logger.warning( "slow server detected")
                    # no traffic during more than three intervals and maxbw < 2.5MBps
                    # indicates this website is too slow for link performance estimation
                    self.cur1.execute("update ipv"+str(self.version)+"server set slow=slow-1 where id = %s",( webid, ))
                self.perfsuccess( webid, webdomain, ip, asn, totaldata, result[3], bandwidth, maxbw, latency, lossrate, actual_loss, serverslow)
            elif(log.count("HTTP request sent, awaiting response... 4")):
                # 404 not found, 403 forbidden, 400 bad request
                bandwidth = 0
                pagesize = 0
                lossrate = -1
                maxbw = 0
                self.logger.info( "Finish 4xx error: %s"%( (webid, ip, asn, webdomain, bandwidth, pagesize, latency, lossrate, success),) )
                self.cur1.execute("insert into web_perf"+str(self.version)+" values(%s, %s, %s, %s, %s, now(), %s, %s, %s, %s, %s, %s, %s)",(self.mac, webid, ip, asn, webdomain, bandwidth,pagesize, latency, lossrate, lossrate, maxbw, self.wtype))
                self.cur1.execute("update ipv"+str(self.version)+"server set crawl=crawl-1 where id = %s",( webid, ))
            else:
                # connection timed out, 5xx server error
                self.insertfailure(webid, webdomain)
                self.logger.info( "Finish other error:%s"%(result,))

        filelist = glob.glob(name+"*")
        for fh in filelist:
            os.remove(fh)
        tend = time.time()
        #self.logger.info( "Time used for downloading "+locale.format("%d",totalsize, grouping=True),'B from '+str(len(self.idlist))+" websites: "+str(tend-tstart)+'secs, speed:'+str(totalsize/(tend-tstart))+'B/s, '+str(self.errorcount)+' errors')
        self.logger.info( "Finish downloading {0}B from {1} websites in {2} secs, avg speed {3}B/s, {4} errors.".format(locale.format("%d",totalsize, grouping=True), len(self.idlist), int(tend-tstart), int(totalsize/(tend-tstart)), self.errorcount))
        self.logger.info( " thread done @ "+time.strftime("%Y-%m-%d %H:%M:%S")+'\n')
