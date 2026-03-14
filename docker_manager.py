"""
Docker Machine Manager for Cyber Training Platform
Spawns vulnerable Docker containers for lab machines
"""
import os
import sys
import docker
import random
import string
from docker.errors import APIError, NotFound
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# Docker configuration - Use Windows named pipe or Unix socket based on OS
if sys.platform == 'win32':
    # Windows Docker Desktop: try multiple connection methods
    DOCKER_HOST = os.environ.get('DOCKER_HOST', 'tcp://host.docker.internal:2375')
    try:
        # Try named pipe first
        client = docker.DockerClient(base_url='npipe:////./pipe/docker_engine')
        client.ping()
        DOCKER_HOST = 'npipe:////./pipe/docker_engine'
    except:
        try:
            # Try TCP
            client = docker.DockerClient(base_url='tcp://host.docker.internal:2375')
            client.ping()
            DOCKER_HOST = 'tcp://host.docker.internal:2375'
        except:
            # Fall back to Unix socket
            DOCKER_HOST = os.environ.get('DOCKER_HOST', 'unix:///var/run/docker.sock')
else:
    DOCKER_HOST = os.environ.get('DOCKER_HOST', 'unix:///var/run/docker.sock')
LAB_NETWORK = os.environ.get('LAB_NETWORK', 'lab_network')
LAB_SUBNET = os.environ.get('LAB_SUBNET', '10.10.10.0/24')

# Common vulnerable images for lab machines
VULNERABLE_IMAGES = {
    'linux_easy': 'vulhub/vulnhub:metasploitable2',
    'linux_medium': 'vulhub/vulnhub:dvwa',
    'linux_hard': 'vulhub/vulnhub:holynix',
    'web_easy': 'vulhub/vulnhub:webgoat',
    'web_medium': 'vulhub/vulnhub:bwapp',
    'windows_easy': 'windows/servercore:ltsc2019',
}


def get_docker_client():
    """Get Docker client"""
    try:
        client = docker.DockerClient(base_url=DOCKER_HOST)
        client.ping()
        return client
    except Exception as e:
        logger.error(f"Failed to connect to Docker: {e}")
        return None


def ensure_lab_network():
    """Create lab network if it doesn't exist"""
    client = get_docker_client()
    if not client:
        return None
    
    try:
        network = client.networks.get(LAB_NETWORK)
        return network
    except NotFound:
        # Create network
        try:
            network = client.networks.create(
                LAB_NETWORK,
                driver='bridge',
                ipam={
                    'driver': 'default',
                    'config': [
                        {'subnet': LAB_SUBNET}
                    ]
                }
            )
            return network
        except APIError as e:
            logger.error(f"Failed to create network: {e}")
            return None


def get_available_ip():
    """Get an available IP in the lab network"""
    # Simple allocation - use random IP from subnet
    # In production, you'd track allocated IPs in database
    return f"10.10.10.{random.randint(10, 250)}"


def generate_container_name(machine_name, username):
    """Generate unique container name"""
    suffix = ''.join(random.choices(string.ascii_lowercase, k=4))
    return f"lab-{machine_name.lower()}-{username.lower()}-{suffix}"


def start_machine(machine_id, machine_name, os_type, difficulty, image=None):
    """
    Start a vulnerable machine container
    
    Args:
        machine_id: Database machine ID
        machine_name: Name of the machine
        os_type: Linux, Windows, etc.
        difficulty: easy, medium, hard, insane
        image: Docker image to use (optional)
    
    Returns:
        dict with container info
    """
    client = get_docker_client()
    if not client:
        return {'success': False, 'error': 'Docker not available'}
    
    # Ensure lab network exists
    ensure_lab_network()
    
    # Determine image based on difficulty
    if not image:
        image = get_image_for_difficulty(os_type, difficulty)
    
    container_name = generate_container_name(machine_name, f"machine{machine_id}")
    
    # Get available IP
    container_ip = get_available_ip()
    
    try:
        # Pull image if not exists
        try:
            client.images.get(image)
        except NotFound:
            logger.info(f"Pulling image: {image}")
            client.images.pull(image)
        
        # Create and start container
        container = client.containers.run(
            image,
            name=container_name,
            detach=True,
            network=LAB_NETWORK,
            ip=container_ip,
            environment={
                'FLAG': f'flag{{{machine_id}_{random.randint(1000, 9999)}}}',
            },
            # Disable auto-remove for persistence
            auto_remove=False,
            # Resource limits
            mem_limit='512m',
            cpu_period=100000,
            cpu_quota=50000,  # 50% CPU limit
        )
        
        return {
            'success': True,
            'container_id': container.id,
            'container_name': container_name,
            'ip_address': container_ip,
            'image': image,
            'status': 'running',
            'started_at': datetime.now().isoformat(),
        }
        
    except APIError as e:
        logger.error(f"Failed to start container: {e}")
        return {'success': False, 'error': str(e)}


def stop_machine(container_id):
    """
    Stop a running machine container
    """
    client = get_docker_client()
    if not client:
        return {'success': False, 'error': 'Docker not available'}
    
    try:
        container = client.containers.get(container_id)
        container.stop(timeout=10)
        return {'success': True, 'status': 'stopped'}
    except NotFound:
        return {'success': False, 'error': 'Container not found'}
    except APIError as e:
        return {'success': False, 'error': str(e)}


def remove_machine(container_id):
    """
    Remove a machine container
    """
    client = get_docker_client()
    if not client:
        return {'success': False, 'error': 'Docker not available'}
    
    try:
        container = client.containers.get(container_id)
        container.remove(force=True)
        return {'success': True, 'status': 'removed'}
    except NotFound:
        return {'success': False, 'error': 'Container not found'}
    except APIError as e:
        return {'success': False, 'error': str(e)}


def get_machine_status(container_id):
    """
    Get status of a machine container
    """
    client = get_docker_client()
    if not client:
        return {'status': 'unknown', 'error': 'Docker not available'}
    
    try:
        container = client.containers.get(container_id)
        return {
            'status': container.status,
            'container_id': container.id,
            'name': container.name,
            'image': container.image.tags[0] if container.image.tags else 'unknown',
            'created': container.attrs.get('Created', 'unknown'),
            'ports': container.ports,
        }
    except NotFound:
        return {'status': 'not_found'}
    except APIError as e:
        return {'status': 'error', 'error': str(e)}


def list_lab_machines():
    """
    List all running lab containers
    """
    client = get_docker_client()
    if not client:
        return []
    
    try:
        containers = client.containers.list(
            all=True,
            filters={'name': 'lab-'}
        )
        return [
            {
                'id': c.id[:12],
                'name': c.name,
                'status': c.status,
                'image': c.image.tags[0] if c.image.tags else 'unknown',
            }
            for c in containers
        ]
    except APIError as e:
        logger.error(f"Failed to list containers: {e}")
        return []


def get_image_for_difficulty(os_type, difficulty):
    """
    Get appropriate Docker image for OS type and difficulty
    """
    # This is a simplified mapping - you'd customize this
    # based on your machine definitions
    
    if os_type.lower() == 'windows':
        return 'mcr.microsoft.com/windows/servercore:ltsc2019'
    
    # Linux images by difficulty
    linux_images = {
        'easy': 'vulhub/vulnhub:metasploitable2',
        'medium': 'vulhub/vulnhub:dvwa', 
        'hard': 'vulhub/vulnhub:holynix',
        'insane': 'vulhub/vulnhub:kioptrix1',
    }
    
    return linux_images.get(difficulty.lower(), 'vulhub/vulnhub:metasploitable2')


def get_machine_console(container_id):
    """
    Get console/terminal access to a machine
    Note: This requires additional setup with docker exec
    """
    client = get_docker_client()
    if not client:
        return None
    
    try:
        container = client.containers.get(container_id)
        return {
            'exec_command': f'docker exec -it {container_id} /bin/bash',
            'container_id': container_id,
        }
    except NotFound:
        return None


# Example usage
if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python docker_manager.py <action> <args>")
        print("Actions: start, stop, status, list")
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == 'start':
        if len(sys.argv) < 5:
            print("Usage: python docker_manager.py start <machine_name> <difficulty>")
            sys.exit(1)
        machine_name = sys.argv[2]
        difficulty = sys.argv[3]
        result = start_machine(1, machine_name, 'Linux', difficulty)
        print(result)
    
    elif action == 'stop':
        if len(sys.argv) < 3:
            print("Usage: python docker_manager.py stop <container_id>")
            sys.exit(1)
        container_id = sys.argv[2]
        result = stop_machine(container_id)
        print(result)
    
    elif action == 'status':
        if len(sys.argv) < 3:
            print("Usage: python docker_manager.py status <container_id>")
            sys.exit(1)
        container_id = sys.argv[2]
        result = get_machine_status(container_id)
        print(result)
    
    elif action == 'list':
        machines = list_lab_machines()
        for m in machines:
            print(m)
