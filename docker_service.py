#!/usr/bin/env python
"""
Docker management service for spawning vulnerable containers
With security controls, network isolation, and automatic cleanup
"""
import docker
import logging
import sys
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import threading
import time

logger = logging.getLogger(__name__)

# Lab network configuration
LAB_NETWORK = "lab_network"
VPN_NETWORK = "10.8.0.0/24"
LAB_SUBNET = "10.10.10.0/24"

# Container limits
DEFAULT_MEMORY = "512m"
DEFAULT_CPU = 0.5  # 50% of one CPU
CONTAINER_TIMEOUT_HOURS = 1  # Auto-stop after 1 hour

class DockerManager:
    """Manage Docker containers for vulnerable machines with security"""
    
    def __init__(self):
        self.client = None
        self.last_error = ""
        self._ensure_connection()
        
    def _ensure_connection(self):
        if self.client:
            try:
                self.client.ping()
                return True
            except:
                self.client = None

        try:
            # Try different connection methods for Docker
            if sys.platform == 'win32':
                endpoints = [
                    'npipe:////./pipe/docker_engine',
                    'tcp://host.docker.internal:2375',
                    'unix:/var/run/docker.sock'
                ]
            else:
                endpoints = ['unix:/var/run/docker.sock']
                
            for ep in endpoints:
                try:
                    client = docker.DockerClient(base_url=ep)
                    client.ping()
                    self.client = client
                    self.last_error = ""
                    break
                except Exception as e:
                    import traceback
                    msg = f"Failed to connect to {ep}: {e}\n{traceback.format_exc()}"
                    self.last_error += msg + "\n"

            if not self.client and sys.platform != 'win32':
                try:
                    client = docker.from_env()
                    client.ping()
                    self.client = client
                    self.last_error = ""
                except Exception as e:
                    import traceback
                    msg = f"Failed from_env: {e}\n{traceback.format_exc()}"
                    self.last_error += msg + "\n"

            if self.client:
                self._ensure_networks()
                logger.info("Docker connection established")
                return True
        except Exception as e:
            import traceback
            err = f"Outer Exception in ensure_connection: {e}\n{traceback.format_exc()}"
            self.last_error += err
            logger.error(f"Docker not available: {e}")

        return False
    
    def _ensure_networks(self):
        """Create lab network if not exists"""
        try:
            networks = self.client.networks.list(names=[LAB_NETWORK])
            if not networks:
                self.client.networks.create(
                    LAB_NETWORK,
                    driver="bridge",
                    ipam=docker.types.IPAMConfig(
                        pool_configs=[docker.types.IPAMPool(
                            subnet=LAB_SUBNET
                        )]
                    )
                )
                logger.info(f"Created lab network: {LAB_SUBNET}")
        except Exception as e:
            logger.warning(f"Could not create network: {e}")
    
    def is_available(self) -> bool:
        """Check if Docker is available"""
        return self._ensure_connection()
    
    def list_containers(self) -> List[Dict]:
        """List all running containers in lab"""
        if not self._ensure_connection():
            return []
        try:
            containers = self.client.containers.list()
            return [
                {
                    'id': c.id[:12],
                    'name': c.name,
                    'image': c.image.tags[0] if c.image.tags else c.image.short_id,
                    'status': c.status,
                    'ports': c.ports,
                }
                for c in containers
                if c.name.startswith('lab_')
            ]
        except Exception as e:
            logger.error(f"Error listing containers: {e}")
            return []
    
    def start_machine(self, machine_id: int, user_id: int, image: str, 
                     ports: Dict[str, int] = None, timeout_hours: int = None) -> Dict:
        """
        Start a vulnerable machine container with security controls
        Returns: {success: bool, container_id: str, ip: str, expires_at: str, message: str}
        """
        if getattr(self, 'last_error', None) is None:
            self.last_error = ""
        if not self._ensure_connection():
            return {'success': False, 'message': 'Docker not available: ' + self.last_error}
        
        container_name = f"lab_u{user_id}_m{machine_id}"
        timeout = timeout_hours or CONTAINER_TIMEOUT_HOURS
        
        # Check if already running
        try:
            existing = self.client.containers.get(container_name)
            if existing.status == 'running':
                network = existing.attrs.get('NetworkSettings', {}).get('Networks', {})
                ip = list(network.values())[0].get('IPAddress', 'N/A') if network else 'N/A'
                return {
                    'success': True,
                    'container_id': existing.id[:12],
                    'ip': ip,
                    'expires_at': (datetime.now() + timedelta(hours=timeout)).isoformat(),
                    'message': 'Container already running'
                }
            # Remove stopped container
            existing.remove(force=True)
        except docker.errors.NotFound:
            pass
        except Exception as e:
            logger.warning(f"Error checking container: {e}")
        
        # Default ports - bind port 80 to a host port if not specified
        port_bindings = {}
        if ports:
            for container_port, host_port in ports.items():
                if host_port:
                    port_bindings[f"{container_port}/tcp"] = host_port
        elif machine_id:
            # Default: map container port 80 to host port 10000+machine_id
            host_port = 10000 + machine_id
            port_bindings = {'80/tcp': host_port}
        
        try:
            # Pull image if needed
            try:
                self.client.images.get(image)
            except docker.errors.NotFound:
                logger.info(f"Pulling image {image}...")
                self.client.images.pull(image)
            
            # Security options
            security_opts = [
                "no-new-privileges",
                "seccomp:unconfined"  # Allow syscalls needed for exploits
            ]
            
            # Create container with security controls
            container = self.client.containers.run(
                image,
                name=container_name,
                detach=True,
                network=LAB_NETWORK,
                mem_limit=DEFAULT_MEMORY,
                cpu_period=100000,
                cpu_quota=int(100000 * DEFAULT_CPU),
                security_opt=security_opts,
                read_only=False,  # Need writable filesystem for MySQL and Apache
                tmpfs={'/tmp': 'rw,noexec,nosuid,size=64m'},
                ports=port_bindings if port_bindings else None,
                environment={
                    'FLAG': f'HTB{{{machine_id}_{user_id}}}',  # Auto-generate flag
                },
                restart_policy={'Name': 'no'}
            )
            
            # Get container IP
            container.reload()
            network = container.attrs.get('NetworkSettings', {}).get('Networks', {})
            ip = list(network.values())[0].get('IPAddress', 'N/A') if network else 'N/A'
            
            # Calculate expiry
            expires_at = datetime.now() + timedelta(hours=timeout)
            
            logger.info(f"Started container {container.id[:12]} for user {user_id}, machine {machine_id}")
            
            return {
                'success': True,
                'container_id': container.id[:12],
                'ip': ip,
                'expires_at': expires_at.isoformat(),
                'expires_in': timeout * 3600,
                'message': f'Machine started! IP: {ip}. Expires in {timeout} hour(s).'
            }
            
        except Exception as e:
            logger.error(f"Error starting container: {e}")
            return {'success': False, 'message': str(e)}
    
    def stop_machine(self, machine_id: int, user_id: int) -> Dict:
        """Stop and remove a container"""
        if not self._ensure_connection():
            return {'success': False, 'message': 'Docker not available'}
        
        container_name = f"lab_u{user_id}_m{machine_id}"
        
        try:
            container = self.client.containers.get(container_name)
            container.stop(timeout=5)
            container.remove(force=True)
            logger.info(f"Stopped and removed container for machine {machine_id}, user {user_id}")
            return {'success': True, 'message': 'Machine stopped and cleaned up'}
        except docker.errors.NotFound:
            return {'success': True, 'message': 'Container not found'}
        except Exception as e:
            logger.error(f"Error stopping container: {e}")
            return {'success': False, 'message': str(e)}
    
    def get_machine_status(self, machine_id: int, user_id: int) -> Dict:
        """Get status of a machine container"""
        if not self._ensure_connection():
            return {'running': False, 'message': 'Docker not available'}
        
        container_name = f"lab_u{user_id}_m{machine_id}"
        
        try:
            container = self.client.containers.get(container_name)
            network = container.attrs.get('NetworkSettings', {}).get('Networks', {})
            ip = list(network.values())[0].get('IPAddress', 'N/A') if network else 'N/A'
            
            return {
                'running': container.status == 'running',
                'status': container.status,
                'container_id': container.id[:12],
                'ip': ip,
                'ports': container.ports
            }
        except docker.errors.NotFound:
            return {'running': False, 'status': 'not_found'}
        except Exception as e:
            return {'running': False, 'error': str(e)}
    
    def cleanup_expired(self, instances: List[Dict]) -> int:
        """Clean up expired containers. Returns count of cleaned containers."""
        if not self._ensure_connection():
            return 0
        
        cleaned = 0
        now = datetime.now()
        
        for instance in instances:
            if instance.get('expires_at'):
                expires = datetime.fromisoformat(instance['expires_at'])
                if expires < now:
                    result = self.stop_machine(
                        instance['machine_id'], 
                        instance['user_id']
                    )
                    if result['success']:
                        cleaned += 1
        
        return cleaned
    
    def get_container_logs(self, machine_id: int, user_id: int, lines: int = 50) -> str:
        """Get container logs"""
        if not self._ensure_connection():
            return "Docker not available"
        
        container_name = f"lab_u{user_id}_m{machine_id}"
        
        try:
            container = self.client.containers.get(container_name)
            logs = container.logs(tail=lines).decode('utf-8')
            return logs
        except:
            return "No logs available"


# Pre-configured vulnerable images for your platform
VULNERABLE_IMAGES = {
    # Web Vulnerabilities
    'dvwa': 'vulnerables/web-dvwa',
    'juiceshop': 'bkimminich/juice-shop',
    'sqlol': 'passwordlab/sqlol',
    'webgoat': 'webgoat/webgoat-8.0',
    
    # Linux Machines
    'metasploitable': 'tleemcjr/metasploitable2',
    'droopy': 'redteam冗/droopy',
    
    # Windows
    'owasp-bricks': 'explicit/owasp-bricks',
    
    # CTF
    'dvwa': 'vulnerables/web-dvwa',
    
    # Practice
    'nginx-hack': 'nginx:1.19',  # Base for custom labs
    
    # === Custom Lab Machine Images ===
    # These can be built from lab-machine/ directory
    'basic-lab': 'cyber-training/basic-lab',
    'web-lab': 'cyber-training/web-lab',
    'ctf-lab': 'cyber-training/ctf-lab',
    'network-lab': 'cyber-training/network-lab',
}


# Singleton instance
docker_manager = DockerManager()
