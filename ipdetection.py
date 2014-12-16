#! /usr/bin/python
# wget --delete-after --header="Host:1111.ip138.com" 112.84.191.168/ic.asp

import os,sys,string,re, httplib,  collections, shlex, MySQLdb, urllib, urllib2, uuid, time
from webcrawl import *
user_agent = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.89 Safari/537.1'
headers = { 'User-agent':user_agent, "Accept": "text/plain" }
if 0==connect_detection(6):
    print "No IPv6 connection detected. Starting Openvpn"
    os.system("/usr/sbin/service openvpn start")
    time.sleep(2)
    domain = '115.25.86.4'
else:
    domain = 'perf.sasm3.net'

if len(sys.argv)>1:
    idle = int(sys.argv[1])
    time.sleep(idle)

def ip138(web,headers):
    cmd = 'wget -T 5 -t 2 --header="'+headers+'" -o /dev/null -O - http://'+web+'/ic.asp'
    #print cmd
    proc = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr = subprocess.PIPE)
    proc.wait()
    data = proc.stdout.read()
    m = re.search('<center>.*\[(.*)\].*</center>',data)
    if m:
        return m.group(1)
    else:
        return '0.0.0.0'
def refresh():
    global weblist_138,headers_138
    url = 'http://'+domain+'/raspberry/ipresolver.php'
    try:
        response = urllib2.urlopen(url)
        content = response.read()
    except:
        return False
    weblist_138.clear()
    headers_138=''
    for line in content.split('\n'):
        if line.count(':') == 0 :
            continue
        m = re.search('IP:(.*)\s(.*)', line)
        if m:
            weblist_138[m.group(2)] = m.group(1)
        else:
            headers_138 += line
    #print weblist_138
    #print headers_138
    return True
dirname, _ = os.path.split(os.path.abspath(sys.argv[0]))
with open(dirname+os.sep+'hour') as f:
    try:    
        hour = int(f.readline().rstrip())
    except:
        hour = 0

ip = collections.defaultdict(str)
asn = collections.defaultdict(str)
mac = mac_addr()

weblist_138 = {'CU':'112.84.191.168','CM':'183.238.101.232', 'CT':'117.25.157.119'}
headers_138 =  'Host:1111.ip138.com' 
#headers_138 =  'H' 

_,ip['CE'],asn['CE'] = downloader('115.25.86.4','/clientip.php','(.*)')
ip['IF'] = re.search("inet addr:(\d+\.\d+\.\d+\.\d+)\s+Bcast",subprocess.Popen(shlex.split('/sbin/ifconfig'),stdout=subprocess.PIPE).stdout.read()).group(1)
_,ipv6,asn6 = downloader('[2001:da8:243:8601::864]','/clientip.php','(.*)', 6)
#print downloader('1111.ip138.com','/ic.asp','<center>.*\[(.*)\].*</center>')
if hour == int(time.strftime("%H")):
    _,ip['I1'],asn['I1'] = downloader('checkmyip.com','/','Your.*IP.*is:.*>(\d+\.\d+\.\d+\.\d+)</span')
    _,ip['I2'],asn['I2'] = downloader('whatismyipaddress.com','/ip-lookup','name="LOOKUPADDRESS" value="(\d+\.\d+\.\d+\.\d+)"\ssize="')
    try:
        for key in weblist_138.keys():
            ip[key] = ip138(weblist_138[key], headers_138)
            if ip[key] == '0.0.0.0':
                raise
            asn[key] = ip2asn(ip[key])
    except:
        print 'Refreshing resolver IP and URL'
        if refresh():
            for key in weblist_138:
                try:
                    ip[key] = ip138(weblist_138[key], headers_138)
                    asn[key] = ip2asn(ip[key])
                except:
                    continue
ip4str = '+'.join([i+':'+ip[i] for i in sorted(ip.keys())])
asn4str = '+'.join([i+':'+asn[i] for i in sorted(asn.keys())])

url = 'http://'+domain+'/raspberry/rasp_address.php'
values = {}

pm1=MySQLdb.connect(host='localhost',user='root',db='raspberry',charset='utf8')
cur1 = pm1.cursor()
cur1.execute('select mac,ipv4,ipv6,asn4 from address order by id desc limit 1')
entry = cur1.fetchone()
needupload = 0
if entry is None or entry[0]!=mac:
    needupload = 1
elif hour== int(time.strftime("%H")) and ( entry[1]!=ip4str or entry[2]!=ipv6 ):
    needupload = 1
else:
    m = re.search("CE:(\d+\.\d+\.\d+\.\d+)",entry[1])
    if m and m.group(1)!=ip['CE']:
        needupload = 1
        #ip4str = entry[1].replace(m.group(1), ip['CE'], 1)
        #asn4str = entry[3].replace(re.search("CE:(.*)\+CM",entry[3]).group(1),asn['CE'], 1)
    elif entry[2]!=ipv6:
        needupload = 1
        ip4str = entry[1]
        asn4str = entry[3]

if needupload:
    print "IP address change detected. New address:"
    print mac,"\n",ip4str,"\n", asn4str,"\n",ipv6,asn6
    cur1.execute('insert into address values(null,%s,%s,%s,%s,%s,now())',(mac,ip4str,asn4str,ipv6,asn6))
    pm1.commit()
    #upload
    values['mac'] = mac
    values['ipv4'] = ip4str
    values['asn4'] = asn4str
    values['ipv6'] = ipv6
    values['asn6'] = asn6
    para = urllib.urlencode(values)
    req = urllib2.Request(url, para)
    response = urllib2.urlopen(req)
    output = response.read()
    #print output
    print "Uploaded to central server."
else:
    print "IP address remain unchanged."
