"""
PwnBox Manager for Cyber Training Platform
Manages browser-based attack environments (like HackTheBox PwnBox)
"""
import docker
import os
import sys
import uuid
from datetime import datetime, timedelta
from docker.errors import NotFound, APIError

# Docker configuration will be determined dynamically
PWNBOX_NETWORK = os.environ.get('PWNBOX_NETWORK', 'pwnbox_network')
LAB_NETWORK = os.environ.get('LAB_NETWORK', 'lab_network')

# PwnBox images - ttyd web terminal
TERMINAL_IMAGE = 'tsl0922/ttyd:latest'
DESKTOP_IMAGE = 'dorowu/ubuntu-desktop-lxde-vnc:latest'

# Track active PwnBox instances per user
active_pwnboxes = {}


def get_docker_client():
    """Get Docker client"""
    if sys.platform == 'win32':
        endpoints = [
            'npipe:////./pipe/docker_engine',
            'tcp://host.docker.internal:2375',
            'unix:///var/run/docker.sock'
        ]
    else:
        endpoints = ['unix:///var/run/docker.sock']

    for endpoint in endpoints:
        try:
            client = docker.DockerClient(base_url=endpoint)
            client.ping()
            return client
        except Exception:
            pass

    print("Failed to connect to Docker")
    return None


def ensure_pwnbox_network():
    """Ensure PwnBox network exists"""
    client = get_docker_client()
    if not client:
        return None
    
    try:
        network = client.networks.get(PWNBOX_NETWORK)
        return network
    except NotFound:
        try:
            network = client.networks.create(
                PWNBOX_NETWORK,
                driver='bridge',
                ipam={
                    'driver': 'default',
                    'config': [
                        {'subnet': '10.100.0.0/24'}
                    ]
                }
            )
            # Connect to lab network
            try:
                lab_network = client.networks.get(LAB_NETWORK)
                network.connect(lab_network)
            except:
                pass
            return network
        except APIError as e:
            print(f"Failed to create network: {e}")
            return None


def start_pwnbox(user_id, user_username):
    """
    Start a PwnBox for a user
    
    Returns:
        dict with connection info
    """
    client = get_docker_client()
    if not client:
        return {'success': False, 'error': 'Docker not available'}
    
    # Ensure network exists
    ensure_pwnbox_network()
    
    # Check if user already has active PwnBox
    if user_id in active_pwnboxes:
        existing = active_pwnboxes[user_id]
        try:
            container = client.containers.get(existing['container_id'])
            if container.status == 'running':
                return {
                    'success': True,
                    'status': 'already_running',
                    'terminal_url': existing['terminal_url'],
                    'desktop_url': existing.get('desktop_url'),
                    'container_id': existing['container_id']
                }
        except:
            pass
    
    # Generate unique container name
    container_name = f"pwnbox-{user_username}-{uuid.uuid4().hex[:6]}"
    
    # Find available ports
    def find_available_port(start=7681, end=9000):
        import socket
        for port in range(start, end + 1):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.bind(('', port))
                s.close()
                return port
            except OSError:
                continue
        return None
    
    terminal_port = find_available_port(7681, 9000)
    desktop_port = find_available_port(6080, 9000)
    
    if not terminal_port:
        return {'success': False, 'error': 'No available ports for terminal'}
    
    try:
        # Start web terminal (ttyd)
        terminal_container = client.containers.run(
            TERMINAL_IMAGE,
            name=f"{container_name}-term",
            detach=True,
            network=PWNBOX_NETWORK,
            ports={f'{terminal_port}/tcp': terminal_port},
            mem_limit='1g',
            cpu_period=100000,
            cpu_quota=50000,
            restart_policy={'Name': 'unless-stopped'},
            command='-p 7681 -t title="PwnBox Terminal" /bin/bash'
        )
        
        # Start desktop container (optional, can be disabled)
        desktop_container = None
        if desktop_port:
            try:
                desktop_container = client.containers.run(
                    DESKTOP_IMAGE,
                    name=f"{container_name}-desktop",
                    detach=True,
                    network=PWNBOX_NETWORK,
                    ports={f'{desktop_port}/tcp': desktop_port},
                    environment={'VNC_PASSWORD': 'cyber training'},
                    mem_limit='2g',
                    cpu_period=100000,
                    cpu_quota=100000,
                    restart_policy={'Name': 'unless-stopped'}
                )
            except Exception as e:
                print(f"Failed to start desktop: {e}")
        
        # Store info
        pwnbox_info = {
            'container_id': terminal_container.id,
            'terminal_container_id': terminal_container.id,
            'desktop_container_id': desktop_container.id if desktop_container else None,
            'terminal_port': terminal_port,
            'desktop_port': desktop_port,
            'terminal_url': f'http://localhost:{terminal_port}',
            'desktop_url': f'http://localhost:{desktop_port}' if desktop_container else None,
            'started_at': datetime.now().isoformat(),
            'username': user_username
        }
        
        active_pwnboxes[user_id] = pwnbox_info
        
        return {
            'success': True,
            'status': 'started',
            'terminal_url': pwnbox_info['terminal_url'],
            'desktop_url': pwnbox_info['desktop_url'],
            'container_id': terminal_container.id
        }
        
    except APIError as e:
        return {'success': False, 'error': str(e)}


def stop_pwnbox(user_id):
    """
    Stop a user's PwnBox
    """
    client = get_docker_client()
    if not client:
        return {'success': False, 'error': 'Docker not available'}
    
    if user_id not in active_pwnboxes:
        return {'success': False, 'error': 'No active PwnBox'}
    
    pwnbox_info = active_pwnboxes[user_id]
    
    try:
        # Stop terminal
        try:
            terminal = client.containers.get(pwnbox_info['terminal_container_id'])
            terminal.stop(timeout=10)
            terminal.remove()
        except:
            pass
        
        # Stop desktop
        if pwnbox_info.get('desktop_container_id'):
            try:
                desktop = client.containers.get(pwnbox_info['desktop_container_id'])
                desktop.stop(timeout=10)
                desktop.remove()
            except:
                pass
        
        del active_pwnboxes[user_id]
        
        return {'success': True, 'status': 'stopped'}
        
    except Exception as e:
        return {'success': False, 'error': str(e)}


def get_pwnbox_status(user_id):
    """
    Get status of user's PwnBox
    """
    client = get_docker_client()
    if not client:
        return {'status': 'unavailable', 'error': 'Docker not available'}
    
    if user_id not in active_pwnboxes:
        return {'status': 'stopped'}
    
    pwnbox_info = active_pwnboxes[user_id]
    
    try:
        terminal = client.containers.get(pwnbox_info['terminal_container_id'])
        status = terminal.status
        
        return {
            'status': status,
            'terminal_url': pwnbox_info['terminal_url'],
            'desktop_url': pwnbox_info.get('desktop_url'),
            'container_id': pwnbox_info['terminal_container_id']
        }
    except NotFound:
        del active_pwnboxes[user_id]
        return {'status': 'stopped'}
    except Exception as e:
        return {'status': 'error', 'error': str(e)}


def get_pwnbox_info(user_id):
    """Get PwnBox info for user"""
    return active_pwnboxes.get(user_id)


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python pwnbox_manager.py <action> <user_id>")
        print("Actions: start, stop, status")
        sys.exit(1)
    
    action = sys.argv[1]
    user_id = int(sys.argv[2])
    
    if action == 'start':
        result = start_pwnbox(user_id, f"user{user_id}")
        print(result)
    elif action == 'stop':
        result = stop_pwnbox(user_id)
        print(result)
    elif action == 'status':
        result = get_pwnbox_status(user_id)
        print(result)
