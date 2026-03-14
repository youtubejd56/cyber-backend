from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from api.models import UserProfile, Room, RoomTask, Machine
from datetime import date, timedelta
import random


class Command(BaseCommand):
    help = 'Seed the database with initial rooms, machines, and demo users'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding database...')

        # Create demo users
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser('admin', 'admin@cybertraining.io', 'admin123')
            profile = UserProfile.objects.create(user=admin, points=15000)
            self.stdout.write(f'Created admin user (password: admin123)')

        if not User.objects.filter(username='h4cker').exists():
            h = User.objects.create_user('h4cker', 'h4cker@test.com', 'hacker123')
            UserProfile.objects.create(user=h, points=7500)

        if not User.objects.filter(username='darkwolf').exists():
            dw = User.objects.create_user('darkwolf', 'darkwolf@test.com', 'dark123')
            UserProfile.objects.create(user=dw, points=3200)

        # Seed Rooms
        rooms_data = [
            {
                'title': 'TryHackMe Basics',
                'description': 'Learn the fundamentals of ethical hacking, including reconnaissance, scanning, and exploitation.',
                'category': 'Learning Path',
                'difficulty': 'Easy',
                'tags': ['beginner', 'recon', 'linux'],
                'rating': 4.8,
                'members_count': 15234,
                'image': 'https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=400&h=200&fit=crop',
                'tasks': [
                    ('What is Ethical Hacking?', 'Understand the basics of penetration testing.', 50, 'THM{ethical_hacking_101}'),
                    ('Setting Up Your Environment', 'Install Kali Linux and basic tools.', 100, 'THM{kali_linux_ready}'),
                    ('Network Reconnaissance', 'Use nmap to scan a target network.', 150, 'THM{nmap_master}'),
                    ('Web Application Basics', 'Identify common web vulnerabilities.', 200, 'THM{burp_suite_pro}'),
                ]
            },
            {
                'title': 'Linux Fundamentals',
                'description': 'Master Linux command line skills essential for cybersecurity professionals.',
                'category': 'Operating Systems',
                'difficulty': 'Easy',
                'tags': ['linux', 'cli', 'fundamentals'],
                'rating': 4.9,
                'members_count': 32100,
                'image': 'https://images.unsplash.com/photo-1629654297299-c8506221ca97?w=400&h=200&fit=crop',
                'tasks': [
                    ('File System Navigation', 'Learn ls, cd, pwd, and more.', 50, 'THM{ls_la_master}'),
                    ('File Permissions', 'Understand chmod, chown, and file permissions.', 100, 'THM{chmod_777_danger}'),
                    ('Process Management', 'Manage processes with ps, kill, top.', 150, 'THM{process_ninja}'),
                ]
            },
            {
                'title': 'Web Application Hacking',
                'description': 'Dive deep into OWASP Top 10, SQL injection, XSS, and web exploitation techniques.',
                'category': 'Web Security',
                'difficulty': 'Medium',
                'tags': ['web', 'sqli', 'xss', 'owasp'],
                'rating': 4.7,
                'members_count': 8900,
                'image': 'https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=400&h=200&fit=crop',
                'tasks': [
                    ('SQL Injection', 'Exploit SQL injection vulnerabilities.', 200, 'THM{sqli_bypass}'),
                    ('XSS Attacks', 'Perform stored and reflected XSS.', 200, 'THM{xss_alert_1}'),
                    ('IDOR Vulnerabilities', 'Exploit insecure direct object references.', 300, 'THM{idor_exposed}'),
                    ('File Upload Bypass', 'Bypass file upload restrictions.', 350, 'THM{webshell_uploaded}'),
                ]
            },
            {
                'title': 'Network Security',
                'description': 'Learn network protocols, packet analysis with Wireshark, and network-based attacks.',
                'category': 'Networking',
                'difficulty': 'Medium',
                'tags': ['networking', 'wireshark', 'mitm', 'packets'],
                'rating': 4.6,
                'members_count': 6700,
                'image': 'https://images.unsplash.com/photo-1544197150-b99a580bb7a8?w=400&h=200&fit=crop',
                'tasks': [
                    ('Packet Analysis', 'Analyze network packets with Wireshark.', 150, 'THM{packet_sniffer}'),
                    ('ARP Spoofing', 'Perform a man-in-the-middle attack.', 300, 'THM{mitm_success}'),
                    ('DNS Enumeration', 'Enumerate DNS records of a target.', 200, 'THM{dns_recon}'),
                ]
            },
            {
                'title': 'Privilege Escalation',
                'description': 'Master Linux and Windows privilege escalation techniques from user to root/SYSTEM.',
                'category': 'Post Exploitation',
                'difficulty': 'Hard',
                'tags': ['privesc', 'linux', 'windows', 'root'],
                'rating': 4.9,
                'members_count': 4200,
                'image': 'https://images.unsplash.com/photo-1510511459019-5dda7724fd87?w=400&h=200&fit=crop',
                'tasks': [
                    ('SUID Binaries', 'Exploit SUID binaries for root access.', 400, 'THM{suid_root}'),
                    ('Sudo Misconfigs', 'Abuse sudo misconfigurations.', 400, 'THM{sudo_l_victory}'),
                    ('Cron Jobs', 'Exploit writable cron jobs.', 500, 'THM{cron_pwned}'),
                    ('Kernel Exploits', 'Use kernel exploits for privilege escalation.', 600, 'THM{kernel_0day}'),
                ]
            },
            {
                'title': 'Cryptography Basics',
                'description': 'Understand cryptographic algorithms, hash cracking, and encryption vulnerabilities.',
                'category': 'Cryptography',
                'difficulty': 'Medium',
                'tags': ['crypto', 'hash', 'rsa', 'aes'],
                'rating': 4.5,
                'members_count': 3800,
                'image': 'https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=400&h=200&fit=crop',
                'tasks': [
                    ('Hash Cracking', 'Crack MD5 and SHA1 hashes.', 200, 'THM{hashcat_master}'),
                    ('RSA Encryption', 'Break weak RSA implementations.', 400, 'THM{rsa_broken}'),
                    ('Caesar Cipher', 'Decode classic ciphers.', 100, 'THM{decode_caesar}'),
                ]
            },
            {
                'title': 'Wireless Hacking with Wifite',
                'description': 'Learn wireless penetration testing using Wifite, aircrack-ng, reaver, and bully.',
                'category': 'Networking',
                'difficulty': 'Medium',
                'tags': ['wireless', 'wifite', 'aircrack-ng', 'wpa2'],
                'rating': 4.7,
                'members_count': 5500,
                'image': 'https://images.unsplash.com/photo-1544197150-b99a580bb7a8?w=400&h=200&fit=crop',
                'tasks': [
                    ('Wifite Setup', 'Configure Wifite for wireless attacks.', 100, 'THM{wifite_ready}'),
                    ('WPA2 Cracking', 'Capture and crack WPA2 handshakes.', 300, 'THM{wpa2_cracked}'),
                    ('WPS Attack', 'Exploit WPS with Reaver.', 250, 'THM{wps_exploited}'),
                ]
            },
            {
                'title': 'Password Cracking with Hydra & John',
                'description': 'Master password cracking using Hydra, John the Ripper, Hashcat, and Rainbow tables.',
                'category': 'Cryptography',
                'difficulty': 'Medium',
                'tags': ['hydra', 'john', 'hashcat', 'password'],
                'rating': 4.8,
                'members_count': 7200,
                'image': 'https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=400&h=200&fit=crop',
                'tasks': [
                    ('Hydra Basics', 'Use Hydra for SSH login cracking.', 150, 'THM{hydra_ssh}'),
                    ('John the Ripper', 'Crack password hashes with John.', 200, 'THM{john_cracked}'),
                    ('Hashcat GPU', 'Use Hashcat with GPU acceleration.', 300, 'THM{hashcat_gpu}'),
                ]
            },
            {
                'title': 'SQL Injection Mastery',
                'description': 'Learn SQL injection attacks using SQLmap, Havij, and manual exploitation.',
                'category': 'Web Security',
                'difficulty': 'Hard',
                'tags': ['sqlmap', 'sqli', 'havij', 'injection'],
                'rating': 4.9,
                'members_count': 6100,
                'image': 'https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=400&h=200&fit=crop',
                'tasks': [
                    ('SQLmap Basics', 'Automate SQL injection with SQLmap.', 200, 'THM{sqlmap_dumper}'),
                    ('Manual SQLi', 'Perform manual SQL injection.', 300, 'THM{manual_sqli}'),
                    ('Blind SQLi', 'Exploit blind SQL injection.', 400, 'THM{blind_exploited}'),
                ]
            },
            {
                'title': 'Reverse Engineering Fundamentals',
                'description': 'Learn reverse engineering using Ghidra, IDA Pro, Radare2, and OllyDbg.',
                'category': 'Operating Systems',
                'difficulty': 'Hard',
                'tags': ['ghidra', 'ida', 'radare2', 'reverse'],
                'rating': 4.8,
                'members_count': 4800,
                'image': 'https://images.unsplash.com/photo-1518770660439-4636190af475?w=400&h=200&fit=crop',
                'tasks': [
                    ('Ghidra Basics', 'Decompile binaries with Ghidra.', 300, 'THM{ghidra_decompiled}'),
                    ('IDA Pro', 'Analyze malware with IDA Pro.', 400, 'THM{ida_analyzed}'),
                    ('Radare2', 'Use Radare2 for binary analysis.', 350, 'THM{radare_master}'),
                ]
            },
            {
                'title': 'Metasploit Framework',
                'description': 'Master exploitation with Metasploit, Meterpreter, and custom payloads.',
                'category': 'Post Exploitation',
                'difficulty': 'Hard',
                'tags': ['metasploit', 'meterpreter', 'exploit', 'payload'],
                'rating': 4.9,
                'members_count': 8900,
                'image': 'https://images.unsplash.com/photo-1510511459019-5dda7724fd87?w=400&h=200&fit=crop',
                'tasks': [
                    ('Msfconsole', 'Navigate and use msfconsole.', 150, 'THM{msf_ready}'),
                    ('Meterpreter', 'Use Meterpreter post-exploitation.', 300, 'THM{meterpreter_pwned}'),
                    ('Custom Payloads', 'Create custom payloads with msfvenom.', 400, 'THM{payload_created}'),
                ]
            },
            {
                'title': 'Social Engineering Toolkit',
                'description': 'Learn social engineering attacks using SET, phishing, and credential harvesting.',
                'category': 'Web Security',
                'difficulty': 'Hard',
                'tags': ['set', 'phishing', 'social-engineering', 'credential'],
                'rating': 4.6,
                'members_count': 5200,
                'image': 'https://images.unsplash.com/photo-1510511459019-5dda7724fd87?w=400&h=200&fit=crop',
                'tasks': [
                    ('SET Basics', 'Configure Social Engineering Toolkit.', 100, 'THM{set_configured}'),
                    ('Phishing Attack', 'Launch a phishing campaign.', 300, 'THM{phish_caught}'),
                    ('Credential Harvesting', 'Harvest credentials with fake login.', 350, 'THM{creds_harvested}'),
                ]
            },
        ]

        admin_user = User.objects.get(username='admin')
        for rdata in rooms_data:
            if not Room.objects.filter(title=rdata['title']).exists():
                room = Room.objects.create(
                    title=rdata['title'],
                    description=rdata['description'],
                    category=rdata['category'],
                    difficulty=rdata['difficulty'],
                    tags=rdata['tags'],
                    rating=rdata['rating'],
                    members_count=rdata['members_count'],
                    image=rdata['image'],
                    creator=admin_user,
                )
                for i, (title, desc, pts, flag) in enumerate(rdata['tasks']):
                    RoomTask.objects.create(
                        room=room, title=title, description=desc, points=pts, flag=flag, order=i
                    )
                self.stdout.write(f'  Created room: {room.title}')

        # Original machines
        original_machines = [
            {
                'name': 'JohnCrack',  
                'os': 'Linux',
                'difficulty': 'Easy',
                'description': 'Crack the password! Download the ZIP file, use John the Ripper to crack it, find the flag inside.',
                'tags': ['password-cracking', 'john', 'zip2john', 'forensics'],
                'rating': 4.0,
                'user_flag': 'CTF{p4ssw0rd_cr4ck3d_success}',
                'root_flag': 'CTF{no_root_flag_for_this_challenge}',
                'user_points': 10,
                'root_points': 0,
                'ip_address': '0.0.0.0',
                'release_date': date(2024, 1, 1),
                'solves_count': 100,
                'image': 'https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=400&h=200&fit=crop',
                'download_url': 'https://raw.githubusercontent.com/youtubejd56/cyber_training_johncrack/main/ctlab.zip',
            },
            {
                'name': 'Lame',
                'os': 'Linux',
                'difficulty': 'Easy',
                'description': 'Lame is a beginner level machine. It only requires one exploit to obtain root access.',
                'tags': ['samba', 'metasploit', 'linux'],
                'rating': 4.2,
                'user_flag': 'HTB{user_fl4g_l4me}',
                'root_flag': 'HTB{r00t_fl4g_l4me}',
                'user_points': 10,
                'root_points': 10,
                'ip_address': '10.10.10.3',
                'release_date': date(2017, 3, 14),
                'solves_count': 45000,
                'image': 'https://images.unsplash.com/photo-1518770660439-4636190af475?w=400&h=200&fit=crop',
            },
            {
                'name': 'Blue',
                'os': 'Windows',
                'difficulty': 'Easy',
                'description': 'Blue is the most user-friendly machine on HackTheBox, exploiting MS17-010 (EternalBlue).',
                'tags': ['windows', 'eternalblue', 'ms17-010'],
                'rating': 4.5,
                'user_flag': 'HTB{user_bl4e_3t3rn4l}',
                'root_flag': 'HTB{r00t_bl4e_3t3rn4l}',
                'user_points': 10,
                'root_points': 10,
                'ip_address': '10.10.10.40',
                'release_date': date(2017, 7, 28),
                'solves_count': 62000,
                'image': 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=400&h=200&fit=crop',
            },
            {
                'name': 'Jerry',
                'os': 'Windows',
                'difficulty': 'Easy',
                'description': 'Jerry focuses on Apache Tomcat exploitation with default credentials.',
                'tags': ['tomcat', 'windows', 'default-creds'],
                'rating': 4.0,
                'user_flag': 'HTB{user_j3rry_t0mc4t}',
                'root_flag': 'HTB{r00t_j3rry_t0mc4t}',
                'user_points': 10,
                'root_points': 10,
                'ip_address': '10.10.10.95',
                'release_date': date(2018, 6, 30),
                'solves_count': 38000,
                'image': 'https://images.unsplash.com/photo-1563013544-824ae1b704d3?w=400&h=200&fit=crop',
            },
            {
                'name': 'Nibbles',
                'os': 'Linux',
                'difficulty': 'Easy',
                'description': 'Nibbles is a fairly simple machine, exploiting a vulnerable CMS.',
                'tags': ['cms', 'linux', 'sudo'],
                'rating': 4.3,
                'user_flag': 'HTB{user_n1bbl3s}',
                'root_flag': 'HTB{r00t_n1bbl3s}',
                'user_points': 10,
                'root_points': 10,
                'ip_address': '10.10.10.75',
                'release_date': date(2018, 1, 13),
                'solves_count': 29000,
                'image': 'https://images.unsplash.com/photo-1504639725590-34d0984388bd?w=400&h=200&fit=crop',
            },
            {
                'name': 'Bank',
                'os': 'Linux',
                'difficulty': 'Medium',
                'description': 'Bank focuses on web application vulnerabilities and DNS enumeration.',
                'tags': ['web', 'dns', 'linux', 'suid'],
                'rating': 4.4,
                'user_flag': 'HTB{user_b4nk_h3ist}',
                'root_flag': 'HTB{r00t_b4nk_h3ist}',
                'user_points': 15,
                'root_points': 15,
                'ip_address': '10.10.10.29',
                'release_date': date(2017, 6, 16),
                'solves_count': 18000,
                'image': 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=400&h=200&fit=crop',
            },
            {
                'name': 'Poison',
                'os': 'FreeBSD',
                'difficulty': 'Medium',
                'description': 'Poison involves LFI vulnerability exploitation and VNC tunneling.',
                'tags': ['lfi', 'freebsd', 'vnc', 'ssh-tunneling'],
                'rating': 4.6,
                'user_flag': 'HTB{user_p0is0n_lf1}',
                'root_flag': 'HTB{r00t_p0is0n_lf1}',
                'user_points': 15,
                'root_points': 15,
                'ip_address': '10.10.10.84',
                'release_date': date(2018, 5, 24),
                'solves_count': 15000,
                'image': 'https://images.unsplash.com/photo-1614064641938-3bbee52942c7?w=400&h=200&fit=crop',
            },
            {
                'name': 'Haircut',
                'os': 'Linux',
                'difficulty': 'Medium',
                'description': 'Haircut demonstrates command injection via a web application.',
                'tags': ['command-injection', 'linux', 'web'],
                'rating': 4.1,
                'user_flag': 'HTB{user_h41rcut_cmd}',
                'root_flag': 'HTB{r00t_h41rcut_cmd}',
                'user_points': 15,
                'root_points': 15,
                'ip_address': '10.10.10.24',
                'release_date': date(2017, 5, 26),
                'solves_count': 12000,
                'image': 'https://images.unsplash.com/photo-1593642632559-0c6d3fc62b89?w=400&h=200&fit=crop',
            },
            {
                'name': 'Holiday',
                'os': 'Linux',
                'difficulty': 'Hard',
                'description': 'Holiday is a hard machine requiring node.js exploitation and complex privilege escalation.',
                'tags': ['nodejs', 'sqli', 'linux', 'hard'],
                'rating': 4.8,
                'user_flag': 'HTB{user_h0l1d4y_n0de}',
                'root_flag': 'HTB{r00t_h0l1d4y_n0de}',
                'user_points': 20,
                'root_points': 20,
                'ip_address': '10.10.10.25',
                'release_date': date(2017, 7, 1),
                'solves_count': 8000,
                'image': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=400&h=200&fit=crop',
            },
        ]

        # Generate 200+ additional machines with various tools
        new_machines = []
        ip_base = 10
        machine_id = 50
        
        # Define categories of machines
        categories = [
            # Wireless
            ('Wifite', 'Wireless', ['wifite', 'aircrack-ng', 'wpa2', 'handshake'], 'Easy', 4.3),
            ('Aircrack', 'Wireless', ['aircrack-ng', 'wep', 'wireless'], 'Easy', 4.2),
            ('ReaverPro', 'Wireless', ['reaver', 'wps', 'bruteforce'], 'Medium', 4.4),
            ('BullyBox', 'Wireless', ['bully', 'wps', 'pixiewps'], 'Medium', 4.3),
            ('EvilTwin', 'Wireless', ['hostapd', 'mdk3', 'evil-twin'], 'Hard', 4.6),
            ('Airgeddon', 'Wireless', ['airgeddon', 'deauth', 'wpa2'], 'Medium', 4.5),
            ('Fluxion', 'Wireless', ['fluxion', 'phishing', 'wifi'], 'Hard', 4.7),
            
            # Password Cracking
            ('HydraSSH', 'Password', ['hydra', 'ssh', 'bruteforce'], 'Easy', 4.2),
            ('HydraFTP', 'Password', ['hydra', 'ftp', 'bruteforce'], 'Easy', 4.1),
            ('HydraHTTP', 'Password', ['hydra', 'http', 'login'], 'Medium', 4.3),
            ('HydraSMB', 'Password', ['hydra', 'smb', 'bruteforce'], 'Medium', 4.3),
            ('JohnLinux', 'Password', ['john', 'linux', 'hash'], 'Easy', 4.4),
            ('JohnWindows', 'Password', ['john', 'ntlm', 'windows'], 'Medium', 4.3),
            ('JohnRAR', 'Password', ['john', 'rar', 'archive'], 'Medium', 4.4),
            ('HashcatMD5', 'Password', ['hashcat', 'md5', 'gpu'], 'Medium', 4.5),
            ('HashcatSHA', 'Password', ['hashcat', 'sha256', 'cracking'], 'Medium', 4.4),
            ('HashcatWPA', 'Password', ['hashcat', 'wpa', 'handshake'], 'Hard', 4.6),
            ('HashcatNTLM', 'Password', ['hashcat', 'ntlm', 'windows'], 'Medium', 4.5),
            ('CainAbel', 'Password', ['cain', 'windows', 'arp'], 'Medium', 4.0),
            ('Medusa', 'Password', ['medusa', 'smb', 'ssh'], 'Medium', 4.2),
            
            # SQL Injection
            ('SQLmapBasic', 'Web', ['sqlmap', 'sqli', 'basic'], 'Easy', 4.3),
            ('SQLmapDork', 'Web', ['sqlmap', 'dork', 'google'], 'Medium', 4.4),
            ('SQLmapWAF', 'Web', ['sqlmap', 'waf', 'bypass'], 'Hard', 4.6),
            ('Havij', 'Web', ['havij', 'sqli', 'automated'], 'Easy', 4.1),
            ('UnionInject', 'Web', ['union', 'sqli', 'injection'], 'Medium', 4.4),
            ('BlindSQLi', 'Web', ['blind', 'sqli', 'inference'], 'Hard', 4.7),
            ('TimeBased', 'Web', ['time-based', 'sqli', 'sleep'], 'Hard', 4.5),
            ('ErrorBased', 'Web', ['error-based', 'sqli', 'mysql'], 'Medium', 4.3),
            
            # Web Security
            ('BurpSuite', 'Web', ['burp', 'web', 'scanning'], 'Easy', 4.4),
            ('OWASPZAP', 'Web', ['zap', 'owasp', 'scanner'], 'Easy', 4.3),
            ('NiktoScan', 'Web', ['nikto', 'web', 'vulnerability'], 'Easy', 4.2),
            ('DirbScan', 'Web', ['dirb', 'directory', 'enumeration'], 'Easy', 4.1),
            ('Gobuster', 'Web', ['gobuster', 'fuzzing', 'directory'], 'Medium', 4.4),
            ('WPScan', 'Web', ['wpscan', 'wordpress', 'cms'], 'Medium', 4.5),
            ('Sublist3r', 'Web', ['sublist3r', 'subdomain', 'dns'], 'Easy', 4.3),
            ('XSSBasic', 'Web', ['xss', 'web', 'javascript'], 'Easy', 4.4),
            ('XSSStored', 'Web', ['xss', 'stored', 'cookie'], 'Medium', 4.5),
            ('CSRFAttack', 'Web', ['csrf', 'web', 'token'], 'Medium', 4.3),
            ('SSRFExploit', 'Web', ['ssrf', 'web', 'internal'], 'Hard', 4.7),
            ('XXEVuln', 'Web', ['xxe', 'xml', 'web'], 'Medium', 4.6),
            ('LFIWeb', 'Web', ['lfi', 'file-inclusion', 'web'], 'Medium', 4.4),
            ('RFIWeb', 'Web', ['rfi', 'file-inclusion', 'web'], 'Medium', 4.3),
            ('IDORWeb', 'Web', ['idor', 'web', 'authorization'], 'Easy', 4.2),
            
            # Reverse Engineering
            ('Ghidra', 'Reverse', ['ghidra', 'decompiler', 'malware'], 'Easy', 4.5),
            ('IDAMalware', 'Reverse', ['ida', 'disassembler', 'malware'], 'Medium', 4.7),
            ('Radare2', 'Reverse', ['radare2', 'cli', 'analysis'], 'Medium', 4.4),
            ('OllyDbg', 'Reverse', ['ollydbg', 'debugger', 'windows'], 'Medium', 4.2),
            ('Immunity', 'Reverse', ['immunity', 'debugger', 'exploit'], 'Medium', 4.4),
            ('Binwalk', 'Reverse', ['binwalk', 'firmware', 'extraction'], 'Easy', 4.3),
            ('Reversing101', 'Reverse', ['reverse', 'basic', 'crackme'], 'Easy', 4.4),
            
            # Exploitation
            ('Metasploit', 'Exploit', ['metasploit', 'msfconsole', 'exploit'], 'Easy', 4.5),
            ('MsfVenom', 'Exploit', ['msfvenom', 'payload', 'shellcode'], 'Medium', 4.6),
            ('Meterpreter', 'Exploit', ['meterpreter', 'post-exploit', 'session'], 'Medium', 4.7),
            ('CobaltStrike', 'Exploit', ['cobalt', 'red-team', 'beacon'], 4.8),
            ('Empire', 'Exploit', ['empire', 'powershell', 'agent'], 'Hard', 4.7),
            ('Covenant', 'Exploit', ['covenant', 'c2', 'grunt'], 'Hard', 4.6),
            ('BeEF', 'Exploit', ['beef', 'browser', 'hook'], 'Medium', 4.5),
            ('ExploitDev', 'Exploit', ['exploit', 'buffer-overflow', 'development'], 'Hard', 4.8),
            
            # Network Security
            ('NmapScan', 'Network', ['nmap', 'scanning', 'recon'], 'Easy', 4.4),
            ('NmapScripts', 'Network', ['nmap', 'nse', 'scripts'], 'Medium', 4.5),
            ('NmapStealth', 'Network', ['nmap', 'stealth', 'syn-scan'], 'Medium', 4.6),
            ('Wireshark', 'Network', ['wireshark', 'packet', 'analysis'], 'Easy', 4.5),
            ('Ettercap', 'Network', ['ettercap', 'mitm', 'arp-spoofing'], 'Medium', 4.4),
            ('Nessus', 'Network', ['nessus', 'vulnerability', 'scan'], 'Medium', 4.5),
            ('OpenVAS', 'Network', ['openvas', 'vulnerability', 'scanner'], 'Medium', 4.3),
            ('Netcat', 'Network', ['netcat', 'nc', 'shell'], 'Easy', 4.3),
            ('Responder', 'Network', ['responder', 'poisoning', 'ntlm'], 'Medium', 4.6),
            ('Impacket', 'Network', ['impacket', 'smb', 'ldap'], 'Medium', 4.5),
            ('DNSEnum', 'Network', ['dns', 'enum', 'recon'], 'Easy', 4.2),
            ('SNMPScan', 'Network', ['snmp', 'enum', 'bruteforce'], 'Medium', 4.3),
            ('SMBEnum', 'Network', ['smb', 'enum', 'null-session'], 'Medium', 4.4),
            
            # Social Engineering
            ('SETPhish', 'Social', ['set', 'phishing', 'email'], 'Medium', 4.4),
            ('Gophish', 'Social', ['gophish', 'phishing', 'campaign'], 'Medium', 4.4),
            ('Maltego', 'Social', ['maltego', 'osint', 'recon'], 'Easy', 4.3),
            ('TheHarvester', 'Social', ['theharvester', 'email', 'recon'], 'Easy', 4.2),
            
            # Privilege Escalation
            ('Linpeas', 'Privesc', ['linpeas', 'linux', 'privesc'], 'Medium', 4.6),
            ('Winpeas', 'Privesc', ['winpeas', 'windows', 'privesc'], 'Medium', 4.6),
            ('GTFOBins', 'Privesc', ['gtfobins', 'suid', 'binary'], 'Medium', 4.5),
            ('SudoMisconfig', 'Privesc', ['sudo', 'misconfig', 'linux'], 'Easy', 4.3),
            ('CronPrivesc', 'Privesc', ['cron', 'privesc', 'scheduled'], 'Medium', 4.4),
            ('KernelExploit', 'Privesc', ['kernel', 'exploit', 'root'], 'Hard', 4.7),
            ('DirtyCow', 'Privesc', ['dirtycow', 'kernel', 'cve'], 'Hard', 4.6),
            ('SUIDExploit', 'Privesc', ['suid', 'privesc', 'binary'], 'Medium', 4.5),
            ('WindowsPrivesc', 'Privesc', ['windows', 'privesc', 'system'], 'Medium', 4.5),
            ('ServiceExploit', 'Privesc', ['service', 'windows', 'system'], 'Hard', 4.6),
            
            # Cryptography
            ('HashCrack', 'Crypto', ['hashcat', 'md5', 'cracking'], 'Easy', 4.3),
            ('RSAcrack', 'Crypto', ['rsa', 'crypto', 'factoring'], 'Hard', 4.7),
            ('AESattack', 'Crypto', ['aes', 'crypto', 'analysis'], 'Hard', 4.6),
            ('SSL_TLS', 'Crypto', ['ssl', 'tls', 'heartbleed'], 'Medium', 4.5),
            ('PGPCrack', 'Crypto', ['gpg', 'pgp', 'encryption'], 'Hard', 4.7),
            ('Base64Decode', 'Crypto', ['base64', 'encoding', 'crypto'], 'Easy', 4.1),
            ('X509Attack', 'Crypto', ['x509', 'certificate', 'tls'], 'Medium', 4.4),
            
            # Forensics
            ('Volatility', 'Forensic', ['volatility', 'memory', 'forensic'], 'Hard', 4.7),
            ('Autopsy', 'Forensic', ['autopsy', 'disk', 'forensic'], 'Medium', 4.5),
            ('Foremost', 'Forensic', ['foremost', 'carving', 'forensic'], 'Easy', 4.3),
            ('Steghide', 'Forensic', ['steghide', 'steganography', 'hidden'], 'Medium', 4.4),
            ('StegSolve', 'Forensic', ['stegsolve', 'steganography', 'image'], 'Medium', 4.3),
            ('BinwalkFirmware', 'Forensic', ['binwalk', 'firmware', 'extraction'], 'Hard', 4.6),
            ('MemoryDump', 'Forensic', ['memory', 'dump', 'forensic'], 'Hard', 4.7),
        ]
        
        # Generate machines by varying the base categories
        num_categories = len(categories)
        # Filter out incomplete tuples
        valid_categories = [c for c in categories if len(c) >= 5]
        valid_count = len(valid_categories)
        for i in range(valid_count):
            base_name = valid_categories[i % valid_count][0]
            cat = valid_categories[i % valid_count][1]
            tags = valid_categories[i % valid_count][2].copy()
            difficulty = valid_categories[i % valid_count][3]
            rating = valid_categories[i % valid_count][4]
            
            # Add variation
            suffix = ''
            if i >= valid_count:
                suffix = f'_v{i // valid_count + 1}'
            
            # Vary difficulty occasionally
            if i % 7 == 0:
                difficulty = 'Hard'
                rating = min(5.0, rating + 0.2)
            elif i % 5 == 0:
                difficulty = 'Easy'
                rating = max(3.5, rating - 0.2)
            
            # Add more tools to tags
            extra_tools = ['python', 'bash', 'linux', 'windows', 'scripting', 'automation']
            tags.append(extra_tools[i % len(extra_tools)])
            
            machine = {
                'name': f'{base_name}{suffix}' if suffix else base_name,
                'os': 'Linux' if i % 3 != 2 else 'Windows',
                'difficulty': difficulty,
                'description': f'Practice {cat.lower()} skills with this machine. Tags: {", ".join(tags)}',
                'tags': tags,
                'rating': round(rating, 1),
                'user_flag': f'CTF{{{base_name.lower()}_user_{machine_id}}}',
                'root_flag': f'CTF{{{base_name.lower()}_root_{machine_id}}}',
                'user_points': 10 if difficulty == 'Easy' else (15 if difficulty == 'Medium' else 20),
                'root_points': 10 if difficulty == 'Easy' else (15 if difficulty == 'Medium' else 20),
                'ip_address': f'10.10.10.{machine_id}',
                'release_date': date(2020, 1, 1) + timedelta(days=i),
                'solves_count': random.randint(500, 15000),
                'image': f'https://images.unsplash.com/photo-1518770660439-4636190af475?w=400&h=200&fit=crop',
            }
            new_machines.append(machine)
            machine_id += 1
        
        # Add original machines first
        for mdata in original_machines:
            if not Machine.objects.filter(name=mdata['name']).exists():
                machine = Machine.objects.create(**mdata)
                self.stdout.write(f'  Created machine: {machine.name}')
        
        # Add all new machines
        for mdata in new_machines:
            if not Machine.objects.filter(name=mdata['name']).exists():
                machine = Machine.objects.create(**mdata)
                self.stdout.write(f'  Created machine: {machine.name}')

        self.stdout.write(self.style.SUCCESS('\nDatabase seeded successfully!'))
        self.stdout.write(f'Total machines: {Machine.objects.count()}')
        self.stdout.write('\nDemo accounts:')
        self.stdout.write('  admin / admin123  (superuser + Elite Hacker)')
        self.stdout.write('  h4cker / hacker123  (Pro Hacker)')
        self.stdout.write('  darkwolf / dark123  (Hacker)')
