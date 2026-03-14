from django.core.management.base import BaseCommand
from api.models import Machine
import random

class Command(BaseCommand):
    help = 'Add unique starting and ending questions to all machines (1-106)'

    def handle(self, *args, **kwargs):
        # Starting questions pool - unique for each machine
        starting_questions = [
            # Reconnaissance
            {'title': '1. Initial Recon', 'question': 'Perform an nmap scan to discover open ports on the target', 'hint': 'nmap -sV -sC 10.10.10.X', 'points': 10, 'answer': 'scan'},
            {'title': '1. Port Discovery', 'question': 'What ports are open on the target machine?', 'hint': 'nmap -p- 10.10.10.X', 'points': 10, 'answer': 'ports'},
            {'title': '1. Service Enum', 'question': 'Identify all services running on the target', 'hint': 'nmap -sV 10.10.10.X', 'points': 10, 'answer': 'services'},
            {'title': '1. OS Detection', 'question': 'Determine the operating system of the target', 'hint': 'nmap -O 10.10.10.X', 'points': 10, 'answer': 'os'},
            {'title': '1. Network Map', 'question': 'Create a network map of the target', 'hint': 'netdiscover -r 10.10.10.0/24', 'points': 10, 'answer': 'network'},
            # Web
            {'title': '1. Web Enum', 'question': 'Enumerate the web server for hidden directories', 'hint': 'gobuster dir -u http://10.10.10.X', 'points': 10, 'answer': 'web'},
            {'title': '1. Web Scan', 'question': 'Run a nikto scan to find vulnerabilities', 'hint': 'nikto -h 10.10.10.X', 'points': 10, 'answer': 'nikto'},
            {'title': '1. Directory Search', 'question': 'Find hidden files and directories', 'hint': 'dirb http://10.10.10.X', 'points': 10, 'answer': 'dirs'},
            {'title': '1. Subdomain Enum', 'question': 'Enumerate subdomains', 'hint': 'sublist3r -d target.com', 'points': 10, 'answer': 'subdomains'},
            {'title': '1. HTTP Methods', 'question': 'Check allowed HTTP methods', 'hint': 'nmap --script http-methods 10.10.10.X', 'points': 10, 'answer': 'methods'},
            # Password
            {'title': '1. Hash Identify', 'question': 'Identify the hash type', 'hint': 'hash-identifier', 'points': 10, 'answer': 'hash'},
            {'title': '1. Password List', 'question': 'Prepare a password list for brute force', 'hint': 'crunch 8 8', 'points': 10, 'answer': 'wordlist'},
            {'title': '1. Credential Gathering', 'question': 'Search for default credentials', 'hint': 'searchsploit default', 'points': 10, 'answer': 'creds'},
            # Network
            {'title': '1. Packet Capture', 'question': 'Start capturing network packets', 'hint': 'tcpdump -i eth0', 'points': 10, 'answer': 'capture'},
            {'title': '1. Traffic Analysis', 'question': 'Analyze network traffic for suspicious activity', 'hint': 'wireshark', 'points': 10, 'answer': 'traffic'},
            {'title': '1. ARP Scan', 'question': 'Perform ARP scan to find hosts', 'hint': 'arp-scan -l', 'points': 10, 'answer': 'arp'},
            # Linux
            {'title': '1. System Info', 'question': 'Gather system information', 'hint': 'uname -a', 'points': 10, 'answer': 'systeminfo'},
            {'title': '1. User Check', 'question': 'Check current user and privileges', 'hint': 'whoami && id', 'points': 10, 'answer': 'user'},
            {'title': '1. Process List', 'question': 'List running processes', 'hint': 'ps aux', 'points': 10, 'answer': 'processes'},
            {'title': '1. Network Connections', 'question': 'Check network connections', 'hint': 'netstat -tuln', 'points': 10, 'answer': 'connections'},
            # Windows
            {'title': '1. Windows Info', 'question': 'Get Windows system information', 'hint': 'systeminfo', 'points': 10, 'answer': 'systeminfo'},
            {'title': '1. User Accounts', 'question': 'List user accounts', 'hint': 'net user', 'points': 10, 'answer': 'users'},
            {'title': '1. Service List', 'question': 'List Windows services', 'hint': 'sc query', 'points': 10, 'answer': 'services'},
            {'title': '1. Registry Check', 'question': 'Check registry for persistence', 'hint': 'reg query', 'points': 10, 'answer': 'registry'},
            # Wireless
            {'title': '1. Interface Setup', 'question': 'Set wireless interface to monitor mode', 'hint': 'airmon-ng start wlan0', 'points': 10, 'answer': 'monitor'},
            {'title': '1. AP Discovery', 'question': 'Discover access points', 'hint': 'airodump-ng wlan0mon', 'points': 10, 'answer': 'aps'},
            {'title': '1. Handshake Capture', 'question': 'Capture WPA handshake', 'hint': 'airodump-ng --bssid', 'points': 10, 'answer': 'handshake'},
            # Exploitation
            {'title': '1. Exploit Search', 'question': 'Search for relevant exploits', 'hint': 'searchsploit', 'points': 10, 'answer': 'exploit'},
            {'title': '1. Vulnerability Scan', 'question': 'Run a vulnerability assessment', 'hint': 'nmap --script vuln', 'points': 10, 'answer': 'vuln'},
            {'title': '1. CVE Lookup', 'question': 'Look up CVEs for the target service', 'hint': 'searchsploit -j', 'points': 10, 'answer': 'cve'},
            # Malware
            {'title': '1. File Analysis', 'question': 'Analyze suspicious file', 'hint': 'file sample', 'points': 10, 'answer': 'file'},
            {'title': '1. String Extraction', 'question': 'Extract strings from binary', 'hint': 'strings malware.exe', 'points': 10, 'answer': 'strings'},
            {'title': '1. Hash Calculation', 'question': 'Calculate file hashes', 'hint': 'md5sum sample', 'points': 10, 'answer': 'hash'},
            # Forensics
            {'title': '1. Image Mount', 'question': 'Mount the forensic image', 'hint': 'mount -o loop image.img', 'points': 10, 'answer': 'mount'},
            {'title': '1. Deleted Files', 'question': 'Recover deleted files', 'hint': 'foremost -i image.img', 'points': 10, 'answer': 'deleted'},
            {'title': '1. Timeline Analysis', 'question': 'Create a timeline of events', 'hint': 'log2timeline', 'points': 10, 'answer': 'timeline'},
        ]
        
        # Ending questions pool - unique for each machine
        ending_questions = [
            # Privilege Escalation
            {'title': '6. Root Access', 'question': 'Escalate privileges to root', 'hint': 'sudo -l', 'points': 25, 'answer': 'root'},
            {'title': '6. System Shell', 'question': 'Obtain a system shell', 'hint': '/bin/sh', 'points': 25, 'answer': 'shell'},
            {'title': '6. Admin Rights', 'question': 'Gain administrator access', 'hint': ' Administrator', 'points': 25, 'answer': 'admin'},
            {'title': '6. Domain Admin', 'question': 'Escalate to domain admin', 'hint': 'psexec', 'points': 25, 'answer': 'domainadmin'},
            {'title': '6. PowerShell Admin', 'question': 'Get PowerShell admin shell', 'hint': 'Start-Process powershell -Verb RunAs', 'points': 25, 'answer': 'psadmin'},
            # Flags
            {'title': '6. User Flag', 'question': 'Capture the user flag', 'hint': 'find /home -name *.txt', 'points': 20, 'answer': 'user'},
            {'title': '6. Root Flag', 'question': 'Capture the root flag', 'hint': 'cat /root/root.txt', 'points': 30, 'answer': 'root'},
            {'title': '6. Admin Flag', 'question': 'Get the administrator flag', 'hint': 'C:\\Users\\Administrator', 'points': 30, 'answer': 'admin'},
            {'title': '6. Secret Flag', 'question': 'Find the secret flag', 'hint': 'Check /root/.secret', 'points': 25, 'answer': 'secret'},
            {'title': '6. Hidden Flag', 'question': 'Locate the hidden flag', 'hint': 'ls -la', 'points': 20, 'answer': 'hidden'},
            # Post Exploitation
            {'title': '6. Persistence', 'question': 'Establish persistence', 'hint': 'cron, systemd', 'points': 25, 'answer': 'persistence'},
            {'title': '6. Lateral Movement', 'question': 'Move laterally to another system', 'hint': 'psexec, wmi', 'points': 25, 'answer': 'lateral'},
            {'title': '6. Data Exfiltration', 'question': 'Exfiltrate sensitive data', 'hint': 'nc, scp', 'points': 25, 'answer': 'exfil'},
            {'title': '6. Cover Tracks', 'question': 'Cover your tracks', 'hint': 'Clear logs', 'points': 20, 'answer': 'cover'},
            {'title': '6. Pivot Point', 'question': 'Use the compromised host as pivot', 'hint': 'proxychains', 'points': 25, 'answer': 'pivot'},
            # Cracking
            {'title': '6. Password Crack', 'question': 'Crack the password hash', 'hint': 'hashcat -m 0', 'points': 20, 'answer': 'cracked'},
            {'title': '6. WPA Key', 'question': 'Recover the WPA key', 'hint': 'aircrack-ng', 'points': 25, 'answer': 'wpa'},
            {'title': '6. Private Key', 'question': 'Extract private key', 'hint': 'openssl rsa', 'points': 25, 'answer': 'private'},
            {'title': '6. SSL Cert', 'question': 'Get the SSL certificate', 'hint': 'openssl s_client', 'points': 20, 'answer': 'cert'},
            # Web
            {'title': '6. Admin Panel', 'question': 'Access the admin panel', 'hint': '/admin', 'points': 20, 'answer': 'admin'},
            {'title': '6. Database Dump', 'question': 'Dump the database', 'hint': 'sqlmap --dump', 'points': 25, 'answer': 'database'},
            {'title': '6. Session Hijack', 'question': 'Hijack admin session', 'hint': 'document.cookie', 'points': 25, 'answer': 'session'},
            {'title': '6. RCE', 'question': 'Achieve remote code execution', 'hint': 'Command injection', 'points': 30, 'answer': 'rce'},
            # Wireless
            {'title': '6. Network Access', 'question': 'Connect to the network', 'hint': 'iwconfig', 'points': 20, 'answer': 'connect'},
            {'title': '6. Traffic Sniff', 'question': 'Sniff network traffic', 'hint': 'ettercap', 'points': 25, 'answer': 'sniff'},
            {'title': '6. MITM Attack', 'question': 'Perform MITM attack', 'hint': 'arpspoof', 'points': 25, 'answer': 'mitm'},
            {'title': '6. Creds Sniff', 'question': 'Sniff credentials', 'hint': 'ettercap -Tq', 'points': 25, 'answer': 'credentials'},
            # Malware
            {'title': '6. Reverse Shell', 'question': 'Get a reverse shell', 'hint': 'msfvenom', 'points': 25, 'answer': 'shell'},
            {'title': '6. Keylogger', 'question': 'Deploy keylogger', 'hint': 'logkeys', 'points': 25, 'answer': 'keylog'},
            {'title': '6. Backdoor', 'question': 'Install backdoor', 'hint': 'netcat', 'points': 25, 'answer': 'backdoor'},
            {'title': '6. Malware Analysis', 'question': 'Analyze the malware sample', 'hint': 'strings, hexeditor', 'points': 20, 'answer': 'analyzed'},
            # Forensics
            {'title': '6. Evidence Find', 'question': 'Find incriminating evidence', 'hint': 'grep -r', 'points': 25, 'answer': 'evidence'},
            {'title': '6. Artifact Recovery', 'question': 'Recover deleted artifacts', 'hint': 'scalpel', 'points': 25, 'answer': 'artifact'},
            {'title': '6. Memory Dump', 'question': 'Dump memory for analysis', 'hint': 'win32dd', 'points': 30, 'answer': 'memory'},
            {'title': '6. Network Forensics', 'question': 'Analyze network captures', 'hint': 'wireshark', 'points': 25, 'answer': 'network'},
        ]

        # Middle tasks - shared across similar machines
        middle_tasks = [
            {'title': '2. Enumeration', 'question': 'Enumerate the target for vulnerabilities', 'hint': 'nmap --script vuln', 'points': 15, 'answer': 'enum'},
            {'title': '3. Initial Access', 'question': 'Gain initial access to the system', 'hint': 'exploit', 'points': 20, 'answer': 'access'},
            {'title': '4. Shell Access', 'question': 'Obtain a shell on the target', 'hint': 'nc -lvnp', 'points': 15, 'answer': 'shell'},
            {'title': '5. User Access', 'question': 'Escalate to user level', 'hint': 'basic privesc', 'points': 15, 'answer': 'user'},
        ]

        machines = Machine.objects.all().order_by('id')
        total_machines = machines.count()
        
        self.stdout.write(f'Found {total_machines} machines in database')
        
        # Shuffle question pools
        random.seed(42)
        starting_pool = starting_questions.copy()
        ending_pool = ending_questions.copy()
        random.shuffle(starting_pool)
        random.shuffle(ending_pool)
        
        updated_count = 0
        
        # Special case: JohnCrack is a challenge machine - only 1 question
        johncrack_machine = machines.filter(name='JohnCrack').first()
        if johncrack_machine:
            johncrack_machine.tasks = [
                {'title': '1. Find the Flag', 'question': 'Download the challenge file, crack the password with John the Ripper, and find the flag inside', 'hint': 'zip2john, john, unzip', 'points': 10, 'answer': 'CTF{p4ssw0rd_cr4ck3d_success}'}
            ]
            johncrack_machine.save()
            updated_count += 1
            self.stdout.write(f'Updated machine {johncrack_machine.id}: {johncrack_machine.name} - Single challenge question')
        
        # Process remaining machines (skip JohnCrack)
        other_machines = machines.exclude(name='JohnCrack').order_by('id')
        
        for idx, machine in enumerate(other_machines):
            # Assign unique starting question
            start_idx = idx % len(starting_pool)
            start_q = starting_pool[start_idx].copy()
            
            # Assign unique ending question
            end_idx = idx % len(ending_pool)
            end_q = ending_pool[end_idx].copy()
            
            # Build task list for this machine
            tasks = [start_q] + middle_tasks + [end_q]
            
            # Update machine with tasks
            machine.tasks = tasks
            machine.save()
            
            updated_count += 1
            self.stdout.write(f'Updated machine {machine.id}: {machine.name} - Start: "{start_q["question"][:50]}..." End: "{end_q["question"][:50]}..."')
        
        self.stdout.write(self.style.SUCCESS(f'\nSuccessfully updated {updated_count} machines with unique starting and ending questions!'))
