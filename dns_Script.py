#https://github.com/anudeepND/blacklist
#https://github.com/senisioi/computer-networks/tree/2023/capitolul2#dns
#https://docs.pi-hole.net/
#https://www.geeksforgeeks.org/working-of-domain-name-system-dns-server/
#https://en.wikipedia.org/wiki/Domain_Name_System
#https://docs.python.org/3/library/socket.html


import subprocess
import socket
import struct
import threading
import time
import logging
import json
from datetime import datetime
from collections import defaultdict, Counter
import requests
import os
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('dns_blocker.log'),
        logging.StreamHandler()
    ]
)

class DNSServer:
    def __init__(self, host='0.0.0.0', port=53, upstream_dns='8.8.8.8'):
        self.host = host
        self.port = port
        self.upstream_dns = upstream_dns

        self.blocked_domains = set()
        self.company_stats = defaultdict(int)
        self.total_blocked = 0
        
        self.load_blocklist()
        
    def categorize_domain(self, domain):

        """Categorizare domaniu dupa companie"""
        domain_lower = domain.lower() # ma asigur ca totul e scris cu litere mici
        """
        #Verific pentru feicare companie daca domeniile blocate apartin altor domenii detinute de ei
        #Mod de functionare : ia fiecare cuvant din lista cu domenii si verifica daca acel ucvant apare ca subsir in domeniu: 'google' in 'pagead2.googlesyndication.com'  
        """

        if any(keyword in domain_lower for keyword in ['google', 'googleads', 'googlesyndication', 'doubleclick', 'googleadservices', 'googletagmanager', 'googleanalytics', 'youtube', 'googlevideo', 'gstatic']):
            return 'Google'
        elif any(keyword in domain_lower for keyword in ['facebook', 'fbcdn', 'fbsbx', 'instagram', 'whatsapp', 'meta']):
            return 'Facebook/Meta'
        elif any(keyword in domain_lower for keyword in ['microsoft', 'msn', 'live', 'outlook', 'bing', 'events.data.microsoft', 'telemetry.microsoft']):
            return 'Microsoft'
        elif any(keyword in domain_lower for keyword in ['amazon', 'amazonads', 'amazonaws']):
            return 'Amazon'
        elif any(keyword in domain_lower for keyword in ['apple', 'icloud', 'itunes']):
            return 'Apple'
        elif any(keyword in domain_lower for keyword in ['twitter', 'twimg', 'twittercdn', 'x.com']):
            return 'Twitter/X'
        elif any(keyword in domain_lower for keyword in ['tiktok', 'musical.ly', 'bytedance']):
            return 'TikTok'
        elif any(keyword in domain_lower for keyword in ['yahoo', 'yahooapis', 'yimg']):
            return 'Yahoo'
        elif any(keyword in domain_lower for keyword in ['adobe', 'adobedtm', 'omtrdc']):
            return 'Adobe'
        elif any(keyword in domain_lower for keyword in ['adsystem', 'adnxs', 'outbrain', 'taboola', 'criteo', 'pubmatic']):
            return 'Ad Networks'
        elif any(keyword in domain_lower for keyword in ['analytics', 'hotjar', 'mixpanel', 'segment', 'scorecardresearch']):
            return 'Analytics'
        else:
            return 'Other'
    
    def log_blocked_request(self, domain):
        """Simple stats tracking"""
        company = self.categorize_domain(domain)
        self.company_stats[company] += 1
        self.total_blocked += 1
        

        #dau update statisticile despre ce companii au fost blocate
        self.save_stats()
    
    def save_stats(self):
        try:
            #sortez companiile ( de la cele mai multe reclame blocate la cele mai putine)
            sorted_companies = sorted(self.company_stats.items(), 
                                        key=lambda x: x[1], 
                                        reverse=True)
            stats = {
                    'timestamp' : datetime.now().isoformat(),
                    'total_blocked' : self.total_blocked,
                    'domains_in_blocklist': len(self.blocked_domains),
                    'companies': dict(self.company_stats)
            }
            
            file = os.path.abspath('dns_stats.json')
            with open(file,'w') as f:
                json.dump(stats,f,indent=2)
                f.flush()
                os.fsync(f.fileno())

        except Exception as e:
            logging.error(f"Eroare:{e}")

    
    def load_blocklist(self):
        """Incarc domenii dupa mai multe liste de pe net/ bag si domenii custom de la mine"""


        blocklist_urls = [
    'https://raw.githubusercontent.com/anudeepND/blacklist/master/adservers.txt',
    'https://raw.githubusercontent.com/anudeepND/blacklist/master/facebook.txt',
    'https://raw.githubusercontent.com/anudeepND/blacklist/master/CoinMiner.txt',
    'https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts',
    'https://filters.adtidy.org/extension/chromium/filters/2.txt',  
    'https://filters.adtidy.org/extension/chromium/filters/3.txt',  
    'https://filters.adtidy.org/extension/chromium/filters/11.txt', 
    'https://easylist.to/easylist/easylist.txt',
    'https://easylist.to/easylist/easyprivacy.txt',
    'https://easylist.to/easylist/fanboy-annoyance.txt',
]
        
        print("Loading blocklists...")
        
        #aici iau domeniile din url-urile de pe github
        for url in blocklist_urls:
            try:
                response = requests.get(url, timeout=30)
                if response.status_code == 200:
                    self.parse_blocklist(response.text)
            except Exception as e:
                 logging.info(f"Probema la extragerea domeniilor de pe: {url}: {e}")

        
        #am mai pus eu cateva domenii care sunt frecvente sa fiu sigur ca le blocheaza
        custom_domains = [
        'adsystem.amazon.com',
        'amazon-adsystem.com',
        'googlesyndication.com',
        'googleadservices.com',
        'doubleclick.net',
        'googletag.com',
        'googletagmanager.com',
        'google-analytics.com',
        'googleanalytics.com',
        'scorecardresearch.com',
        'quantserve.com',
        'outbrain.com',
        'taboola.com',
        'criteo.com',
        'casalemedia.com',
        'rubiconproject.com',
        'adsystem.com',
        'bidswitch.net',
        'smartadserver.com',
        'pubmatic.com',
        'openx.net',
        'adsystem.windows.com',
        'ads.yahoo.com',
        'advertising.com',
        'adsystem.microsoft.com',
        'facebook.com',
        'connect.facebook.net',
        'facebook.net',
        'fbcdn.net',
        'fbsbx.com',
        'instagram.com',
        'cdninstagram.com',
        'ads.google.com',
        'adnxs.com',
        'adsystem.google.com',
        'admob.com',
        'gstatic.com',
        'youtube.com/ads',
        'ytimg.com/ads',
        'bat.bing.com',
        'ads.msn.com',
        'flex.msn.com',
        'rad.msn.com',
        'live.rads.msn.com',
        'amazonclix.com',
        'assoc-amazon.com',
        'amazon-adsystem.com',
        'amazonservices.com',
        'media-amazon.com',
        'adsystem.com',
        'adsymptotic.com',
        'adnium.com',
        'adsystem.tv',
        'adform.net',
        'adroll.com',
        'adsystem.net',
        'revcontent.com',
        'mgid.com',
        'zedo.com',
        'undertone.com',
        'turn.com',
        'spotxchange.com',
        'springserve.com',
        'hotjar.com',
        'fullstory.com',
        'mixpanel.com',
        'segment.com',
        'amplitude.com',
        'crazy egg.com',
        'mouseflow.com',
        'inspectlet.com',
        'logrocket.com',
        'smartlook.com',
        'addthis.com',
        'sharethis.com',
        'addtoany.com',
        'disqus.com',
        'zdassets.com',
        'zendesk.com/embeddable_framework',
        'mobile.events.data.microsoft.com',
        'eu-mobile.events.data.microsoft.com', 
        'settings-win.data.microsoft.com',
        'eu-teams.events.data.microsoft.com',
        'default.exp-tas.com',
        'exp-tas.com',
        'adblock.telemetry.getadblock.com',
        'telemetry.getadblock.com',
        
        ]

        for domain in custom_domains:
            self.blocked_domains.add(domain)
        

#####Extragere domenii######

    def is_valid_domain(self, domain):
            return (domain and 
                    '.' in domain and 
                    not domain.startswith('.') and
                    not domain.endswith('.') and
                    'localhost' not in domain)

    def parse_blocklist(self, content):
        """Editez diferite modele de domenii, ca in final sa ramana doar numele domeniului"""
        
        for line in content.split('\n'):
            line = line.strip().lower()
            if not line or line.startswith('#'):
                continue
            
            # aici extrag numele domeniilor si sterg informatiile in plus    

            # 0.0.0.0 domain.com
            if line.startswith('0.0.0.0') or line.startswith('127.0.0.1'):
                parts = line.split()
                if len(parts) >= 2:
                    domain = parts[1]
                    if self.is_valid_domain(domain):
                        self.blocked_domains.add(domain)
            
            # ||domain.com^
            elif line.startswith('||') and line.endswith('^'):
                domain = line[2:-1]
                if self.is_valid_domain(domain):
                    self.blocked_domains.add(domain)
            
            #cand domaniul nu contine alte informatii 
            elif self.is_valid_domain(line):
                self.blocked_domains.add(line)
    
    
    
    def is_blocked(self, domain):
        """Verifica daca domeniul se afla in lista de domenii blocate"""

        domain = domain.lower().rstrip('.') #litere mici si sterg punctul de la final in caz ca exista
        
        if domain in self.blocked_domains: #verific daca domeniul se afla in lista de domenii care ar trb blocae
            return True
        
        parts = domain.split('.')       #verific daca subdomeniile se afla in lista de domenii blocate
        for i in range(len(parts)):
            subdomain = '.'.join(parts[i:])
            if subdomain in self.blocked_domains:
                return True
        
        return False
    
    def parse_dns_query(self, data):
        """Extrag informatiile din query-ul dns"""
        #data ar trebui sa arate ceva de genul :  b'\xaa\xbb\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x03www\x06google\x03com\x00\x00\x01\x00\x01'

        if len(data) < 12: #verific daca header-ul dns-ul e valid ( 12bytes)
            return None
        
        #header:
        transaction_id = struct.unpack('!H', data[0:2])[0]
        flags = struct.unpack('!H', data[2:4])[0]
        questions = struct.unpack('!H', data[4:6])[0]
        
        if questions != 1:  #verific daca dns-ul are o intrebare
            return None
        
        #Extrag numele domeniului din "data" ,  incepem de la byte -ul 12 de aici incepe domeniul
        offset = 12
        domain_parts = []  
        
        while offset < len(data):
            length = data[offset]  # citesc lungimea textului de exemplu pentru x03www este 3
            if length == 0:
                offset += 1
                break
            
            if offset + length + 1 > len(data):
                return None
            
            domain_parts.append(data[offset+1:offset+1+length].decode('utf-8')) #data[offset+1:offset+1+length] taie de unde incepe partea pana la finalul ei pentru x03www va lua "www"
            offset += length + 1 # trec la urmatorul cuvant ( parte din domeniu )
        
        if offset + 4 > len(data):
            return None
        
        domain = '.'.join(domain_parts) # domeniul format din partile extrase ex www.google.com

        #urmatorii 4 bytes contin QTYPE(primii 2) SI QCLASS(ultimii 2)
        qtype = struct.unpack('!H', data[offset:offset+2])[0]
        qclass = struct.unpack('!H', data[offset+2:offset+4])[0]
        
        return {
            'transaction_id': transaction_id,
            'flags': flags,
            'domain': domain,
            'qtype': qtype,
            'qclass': qclass,
            'raw_query': data
        }
    

    
    def create_dns_response(self, query, blocked=False):
        """Blocarea cererilor DNS , prin returnarea ip-ului 0.0.0."""

        if blocked:
            #! Returnez 0.0.0.0 pt domenii blocate !#

            response = bytearray(query['raw_query'])  #luam cererea initiala pe care o prelucram
            
            #flag de raspuns
            response[2] = 0x81  #Recursion Available (clientul poate pune întrebări recursive)
            response[3] = 0x80  #Este un raspuns
            
            #setam nr de raspunsuri cu 1
            response[6] = 0x00
            response[7] = 0x01
            
            #pointer
            response.extend([0xc0, 0x0c])
            
            #tipl rspunsului
            # Type A (1), Class IN (1)
            response.extend([0x00, 0x01, 0x00, 0x01])
            
            # TTL (300 seconds) (cat cache-uiesc raspunsul)
            response.extend([0x00, 0x00, 0x01, 0x2c])
            
            # lungimea datelor (4 bytes pt IPv4)
            response.extend([0x00, 0x04])
            
        #### IP address 0.0.0.0
            response.extend([0x00, 0x00, 0x00, 0x00])
            
            return bytes(response)
        
        return None
    
    def forward_dns_query(self, query_data):
        """dau forward la DNS query la upstream server"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(5)
            sock.sendto(query_data, (self.upstream_dns, 53))
            response, _ = sock.recvfrom(512)
            sock.close()
            return response
        except Exception as e:
            logging.error(f"Eroare: {e}")
            return None
    
    def handle_request(self, data, client_addr, sock):
       
        """procesez un dns request"""
        
        try:
            query = self.parse_dns_query(data)  #extrag toate informatiile de care am nevoie din query-ul dns
            if not query:
                return
            
            domain = query['domain']
            client_ip = client_addr[0]  #ip-ul clientului care trimite query-ul
            
            #!!!!!
            logging.info(f"DNS query from {client_ip}: {domain}")  #Aici bag in log fiecare DNS query interceptat#
            #!!!!!

            if self.is_blocked(domain):
               

                self.log_blocked_request(domain) #aici incadrez domeniile blocate intr o lista de statistici cu companiile care le detin

                
                response = self.create_dns_response(query, blocked=True) #blochez cererea DNS 

                if response:
                    sock.sendto(response, client_addr)

                    #adaug in log ca am blocat domeniul
                    logging.info(f"BLOCKED: {domain}") 

            else:
                # Forward to upstream DNS
                response = self.forward_dns_query(data)
                if response:
                    sock.sendto(response, client_addr)
        
        except Exception as e:
            logging.error(f"Eroare in prelucrarea requestului {e}")
    

    def start(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            sock.bind((self.host, self.port))
            logging.info(f"Serverul DNS ruleaza pe: {self.host}:{self.port}")
            logging.info(f"Upstream DNS: {self.upstream_dns}")  
            logging.info(f"Blochez {len(self.blocked_domains)} de domenii") #cate domenii sunt blocate
            logging.info(f"Statisticile sunt salvate in fisierul: dns_stats.json")

            
            while True:

                try:
                    """
                    "client_addr" este de tipul : ('192.168.1.25', 54823)

                    "data" contine informatii de tipul:
                    
                    0–1	    \xaa\xbb	                ID-ul cererii (random: 0xaabb)
                    2–3	    \x01\x00	                Flags (standard query, recursion desired)
                    4–5	    \x00\x01	                QDCOUNT = 1 (1 întrebare DNS)
                    6–11	\x00\x00\x00\x00\x00\x00	ANCOUNT, NSCOUNT, ARCOUNT = 0
                    12–16	\x03www\x06google\x03com\x00Numele domeniului: www.google.com
                    ...	    \x00\x01	                QTYPE = 1 (A record = IPv4)
                    ...	    \x00\x01	                QCLASS = 1 (Internet)

                    """

                    data, client_addr = sock.recvfrom(512) # de aici se extrag datele si cine a trimis aceste date ( IP : PORT)  din query ul dns
                    
                    #Aici pe scurt apelez functia handle_request(data,client_addr,sock) ca sa procesez datele query-ului
                    thread = threading.Thread(
                        target=self.handle_request,
                        args=(data, client_addr, sock)
                    )
                    thread.start()

                
                except KeyboardInterrupt:       #daca apas CTRL + C in terminal procesul se termina
                    break
                except Exception as e:
                    logging.error(f"Eroare {e}")
        
        finally:
            sock.close()
            self.save_stats() 
            logging.info("Serverul DNS s-a oprit")



if __name__ == "__main__":
    import sys

 


    #Verific daca ruleaza pe root ( daca ruleaza pe root folosesc portul 5353 si nu 53)
    try:
            if os.geteuid() != 0:
                server = DNSServer(port=5353)
            else:
                
                test_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #verific daca portul 53 este liber
                try:
                    test_sock.bind(('0.0.0.0', 53))
                    test_sock.close()
                    server = DNSServer(port=53)
                    print("se foloseste portul 53")
                except OSError:
                    test_sock.close()
                    logging.info("portul 53 e folosit, folosim 5353")
                    server = DNSServer(port=5353)
    except Exception as e:
            logging.info(f"Eroare la crearea serverului: {e}")
            server = DNSServer(port=5353)
        
    try:
        server.start()
    except KeyboardInterrupt:
        print("\nAdblockerul s-a oprit!")








            