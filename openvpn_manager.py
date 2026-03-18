"""
OpenVPN Manager for Cyber Training Platform
Manages OpenVPN certificates and client configurations
"""
import os
import subprocess
import random
import string
from pathlib import Path

# Configuration
EASY_RSA_DIR = os.environ.get('EASY_RSA_DIR', '/etc/openvpn/easy-rsa')
OVPN_DIR = os.environ.get('OVPN_DIR', '/etc/openvpn/client-configs')
CCD_DIR = os.environ.get('CCD_DIR', '/etc/openvpn/ccd')
SERVER_IP = os.environ.get('VPN_SERVER_IP', '10.8.0.1')
OVPN_PORT = int(os.environ.get('OVPN_PORT', '1194'))
OVPN_PROTO = os.environ.get('OVPN_PROTO', 'udp')


def ensure_directories():
    """Ensure required directories exist"""
    os.makedirs(OVPN_DIR, exist_ok=True)
    os.makedirs(CCD_DIR, exist_ok=True)


def run_easyrsa_command(args):
    """Run easyrsa command"""
    cmd = [f'{EASY_RSA_DIR}/easyrsa'] + args
    result = subprocess.run(
        cmd,
        cwd=EASY_RSA_DIR,
        capture_output=True,
        text=True
    )
    return result


def generate_username():
    """Generate a random username for VPN"""
    prefix = 'user'
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f'{prefix}{suffix}'


def get_ca_cert():
    """Read CA certificate"""
    ca_path = Path(EASY_RSA_DIR) / 'pki' / 'ca.crt'
    if ca_path.exists():
        return ca_path.read_text()
    return None


def get_ta_key():
    """Read TLS auth key"""
    ta_path = Path(EASY_RSA_DIR) / 'pki' / 'ta.key'
    if ta_path.exists():
        return ta_path.read_text()
    return None


def create_client_certificate(username):
    """
    Create a new client certificate for the user
    """
    ensure_directories()
    
    # Check if certificate already exists
    cert_path = Path(EASY_RSA_DIR) / 'pki' / 'issued' / f'{username}.crt'
    if cert_path.exists():
        print(f"Certificate for {username} already exists")
        return True
    
    # Generate client certificate
    result = run_easyrsa_command(['build-client-full', username, 'nopass'])
    
    if result.returncode != 0:
        print(f"Error creating certificate: {result.stderr}")
        return False
    
    return True


def get_client_cert(username):
    """Read client certificate"""
    cert_path = Path(EASY_RSA_DIR) / 'pki' / 'issued' / f'{username}.crt'
    if cert_path.exists():
        return cert_path.read_text()
    return None


def get_client_key(username):
    """Read client private key"""
    key_path = Path(EASY_RSA_DIR) / 'pki' / 'private' / f'{username}.key'
    if key_path.exists():
        return key_path.read_text()
    return None


def assign_client_ip(username):
    """Assign a static IP to client in CCD"""
    # Simple IP assignment - 10.8.0.x where x is based on username hash
    ip_hash = sum(ord(c) for c in username)
    client_ip = f'10.8.0.{(ip_hash % 253) + 2}'
    
    ccd_path = Path(CCD_DIR) / username
    ccd_path.write_text(f'ifconfig-push {client_ip} 255.255.255.0\n')
    
    return client_ip


def generate_client_config(username):
    """
    Generate complete OpenVPN client configuration file
    """
    ensure_directories()
    
    # Create certificate if not exists
    if not create_client_certificate(username):
        return None
    
    # Get certificates
    ca_cert = get_ca_cert()
    client_cert = get_client_cert(username)
    client_key = get_client_key(username)
    ta_key = get_ta_key()
    
    if not all([ca_cert, client_cert, client_key, ta_key]):
        print("Missing certificates")
        return None
    
    # Assign static IP
    client_ip = assign_client_ip(username)
    
    # Generate OVPN config
    config = f"""# CyberTraining Lab VPN Configuration
# Generated for: {username}
# Server: {SERVER_IP}:{OVPN_PORT}
# Client IP: {client_ip}

client
dev tun
proto {OVPN_PROTO}
remote {SERVER_IP} {OVPN_PORT}
resolv-retry infinite
nobind
persist-key
persist-tun
remote-cert-tls server
cipher AES-256-CBC
auth SHA256
comp-lzo
verb 3

<ca>
{ca_cert}
</ca>

<cert>
{client_cert}
</cert>

<key>
{client_key}
</key>

<tls-auth>
{ta_key}
</tls-auth>
key-direction 1

# Keep alive
keepalive 10 60
"""
    
    # Save config file
    config_path = Path(OVPN_DIR) / f'{username}.ovpn'
    config_path.write_text(config)
    
    return {
        'config': config,
        'username': username,
        'password': '',  # Certificate-based auth, no password needed
        'client_ip': client_ip,
        'server_ip': SERVER_IP,
        'port': OVPN_PORT,
        'protocol': OVPN_PROTO
    }


def revoke_client_certificate(username):
    """
    Revoke a client certificate
    """
    result = run_easyrsa_command(['revoke', username])
    
    if result.returncode == 0:
        # Generate CRL
        run_easyrsa_command(['gen-crl'])
        return True
    
    return False


def get_vpn_status():
    """
    Get current VPN server status
    """
    status = {
        'server_ip': SERVER_IP,
        'port': OVPN_PORT,
        'protocol': OVPN_PROTO,
        'vpn_network': '10.8.0.0/24',
        'lab_network': '10.10.10.0/24',
    }
    
    # Check if OpenVPN is running
    result = subprocess.run(
        ['systemctl', 'is-active', 'openvpn@server'],
        capture_output=True,
        text=True
    )
    status['running'] = result.returncode == 0
    
    return status


if __name__ == '__main__':
    # Test generation
    import sys
    if len(sys.argv) > 1:
        username = sys.argv[1]
        print(f"Generating config for {username}...")
        result = generate_client_config(username)
        if result:
            print(f"Success! Config saved to {OVPN_DIR}/{username}.ovpn")
            print(f"Username: {result['username']}")
            print(f"Client IP: {result['client_ip']}")
        else:
            print("Failed to generate config")
    else:
        print("Usage: python openvpn_manager.py <username>")
