from rest_framework import status, generics, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.db.models import Avg
from django.db import models
from django.db.models import Sum
import logging
import json
import os
import secrets

logger = logging.getLogger(__name__)

from .models import (
    UserProfile, Room, RoomTask, Machine,
    RoomMembership, TaskSubmission, MachineSubmission,
    VPNConfig, VPNUserConfig, MachineInstance, MachineRating, Frame
)
from .serializers import (
    UserSerializer, RegisterSerializer, RoomSerializer,
    MachineSerializer, LeaderboardSerializer, FrameSerializer
)


# ─────────── AUTH ───────────

@api_view(['POST'])
@permission_classes([AllowAny])
def create_superuser(request):
    """Create superuser endpoint - use only in development!"""
    from django.conf import settings
    if not settings.DEBUG:
        return Response({'error': 'Not available in production'}, status=status.HTTP_403_FORBIDDEN)
    
    username = request.data.get('username', 'admin')
    password = request.data.get('password', 'admin123')
    email = request.data.get('email', 'admin@cybertraining.io')
    
    if User.objects.filter(username=username).exists():
        return Response({'error': f'{username} this name already used'}, status=status.HTTP_400_BAD_REQUEST)
    
    user = User.objects.create_superuser(username, email, password)
    UserProfile.objects.create(user=user, points=15000)
    return Response({'message': f'Superuser {username} created successfully'}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'message': 'Account created successfully',
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    try:
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if not user:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
            
        # Ensure UserProfile exists before serialization to avoid 500 errors
        try:
            profile = user.profile
        except Exception:
            UserProfile.objects.get_or_create(user=user)
            
        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user).data,
        })
    except Exception as e:
        logger.error(f"Login error: {e}")
        return Response({'error': 'An internal server error occurred during login. Please try again later.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request):
    return Response(UserSerializer(request.user).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_avatar(request):
    """Update user avatar - accepts a DiceBear seed or custom URL"""
    try:
        avatar = request.data.get('avatar')
        
        if not avatar:
            return Response({'error': 'Avatar URL is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get or create user profile
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        
        # Validate that it's a valid URL or DiceBear seed
        if avatar.startswith('http'):
            # Custom URL
            profile.avatar = avatar
        else:
            # Assume it's a DiceBear seed - generate the full URL
            profile.avatar = f'https://api.dicebear.com/7.x/pixel-art/svg?seed={avatar}'
        
        profile.save()
        
        return Response({
            'success': True,
            'avatar': profile.avatar
        })
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ─────────── ROOMS ───────────

@api_view(['GET'])
@permission_classes([AllowAny])
def room_list(request):
    rooms = Room.objects.prefetch_related('tasks').all()
    category = request.query_params.get('category')
    difficulty = request.query_params.get('difficulty')
    if category:
        rooms = rooms.filter(category=category)
    if difficulty:
        rooms = rooms.filter(difficulty=difficulty)
    return Response(RoomSerializer(rooms, many=True).data)


@api_view(['GET'])
@permission_classes([AllowAny])
def room_detail(request, pk):
    try:
        room = Room.objects.prefetch_related('tasks').get(pk=pk)
    except Room.DoesNotExist:
        return Response({'error': 'Room not found'}, status=404)
    data = RoomSerializer(room).data
    if request.user.is_authenticated:
        data['is_joined'] = RoomMembership.objects.filter(user=request.user, room=room).exists()
        solved_task_ids = list(TaskSubmission.objects.filter(
            user=request.user,
            task__room=room
        ).values_list('task_id', flat=True))
        data['solved_tasks'] = solved_task_ids
    return Response(data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def join_room(request, pk):
    try:
        room = Room.objects.get(pk=pk)
    except Room.DoesNotExist:
        return Response({'error': 'Room not found'}, status=404)
    membership, created = RoomMembership.objects.get_or_create(user=request.user, room=room)
    if created:
        room.members_count += 1
        room.save()
    return Response({'message': 'Joined room successfully', 'joined': True})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_task_flag(request, room_pk, task_pk):
    try:
        task = RoomTask.objects.get(pk=task_pk, room_id=room_pk)
    except RoomTask.DoesNotExist:
        return Response({'error': 'Task not found'}, status=404)

    # Get the task order to check if previous tasks are completed
    task_order = task.order
    
    # Check if user has joined the room
    if not RoomMembership.objects.filter(user=request.user, room=room_pk).exists():
        return Response({'error': 'You must join the room first'}, status=400)
    
    # Sequential task validation: check if all previous tasks are solved
    if task_order > 0:
        prev_tasks = RoomTask.objects.filter(room_id=room_pk, order__lt=task_order)
        for prev_task in prev_tasks:
            if not TaskSubmission.objects.filter(user=request.user, task=prev_task).exists():
                return Response({'error': f'Complete Task {prev_task.order + 1} first before attempting this task'}, status=400)

    if TaskSubmission.objects.filter(user=request.user, task=task).exists():
        return Response({'message': 'Already solved!', 'correct': True})

    submitted_flag = request.data.get('flag', '').strip()
    if submitted_flag == task.flag:
        TaskSubmission.objects.create(user=request.user, task=task)
        profile = request.user.profile
        profile.points += task.points
        profile.save()
        return Response({
            'correct': True,
            'message': f'Correct flag! +{task.points} points',
            'points': task.points,
            'total_points': profile.points,
        })
    return Response({'correct': False, 'message': 'Incorrect flag. Try again!'})


# ─────────── MACHINES ───────────

@api_view(['GET'])
@permission_classes([AllowAny])
def machine_list(request):
    machines = Machine.objects.all()
    os_filter = request.query_params.get('os')
    difficulty = request.query_params.get('difficulty')
    if os_filter:
        machines = machines.filter(os=os_filter)
    if difficulty:
        machines = machines.filter(difficulty=difficulty)
    return Response(MachineSerializer(machines, many=True).data)


@api_view(['GET'])
@permission_classes([AllowAny])
def machine_detail(request, pk):
    try:
        machine = Machine.objects.get(pk=pk)
    except Machine.DoesNotExist:
        return Response({'error': 'Machine not found'}, status=404)
    data = MachineSerializer(machine).data
    if request.user.is_authenticated:
        data['user_solved'] = MachineSubmission.objects.filter(
            user=request.user, machine=machine, flag_type='user').exists()
        data['root_solved'] = MachineSubmission.objects.filter(
            user=request.user, machine=machine, flag_type='root').exists()
    return Response(data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_machine_flag(request, pk):
    try:
        machine = Machine.objects.get(pk=pk)
    except Machine.DoesNotExist:
        return Response({'error': 'Machine not found'}, status=404)

    flag_type = request.data.get('flag_type', 'user')  # 'user' or 'root'
    submitted_flag = request.data.get('flag', '').strip()

    # Check if already submitted - prevent re-submission
    existing_submission = MachineSubmission.objects.filter(
        user=request.user, machine=machine, flag_type=flag_type
    ).first()
    
    if existing_submission:
        return Response({
            'message': f'{flag_type.capitalize()} flag already submitted!',
            'already_submitted': True,
            'correct': True
        })

    expected = machine.user_flag if flag_type == 'user' else machine.root_flag
    if submitted_flag == expected:
        MachineSubmission.objects.create(user=request.user, machine=machine, flag_type=flag_type)
        points = machine.user_points if flag_type == 'user' else machine.root_points
        profile = request.user.profile
        profile.points += points
        profile.save()
        machine.solves_count += 1
        machine.save()
        return Response({
            'correct': True,
            'message': f'Correct {flag_type} flag! +{points} points!',
            'points': points,
            'total_points': profile.points,
        })
    return Response({'correct': False, 'message': 'Incorrect flag. Keep hacking!'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_machine_task(request, pk):
    """Validate machine task answers - prevents re-submission"""
    try:
        machine = Machine.objects.get(pk=pk)
    except Machine.DoesNotExist:
        return Response({'error': 'Machine not found'}, status=404)

    task_index = request.data.get('task_index')  # 0-based index
    submitted_answer = request.data.get('answer', '').strip()

    if not machine.tasks or task_index >= len(machine.tasks):
        return Response({'error': 'Invalid task'}, status=400)

    task = machine.tasks[task_index]
    correct_answer = task.get('answer', '').strip()

    if not correct_answer:
        return Response({'error': 'Task has no answer configured'}, status=400)

    # Get user's completed tasks for this machine
    profile = request.user.profile
    completed_tasks = profile.completed_tasks or {}
    
    # Check if already completed this task
    machine_id = str(machine.id)
    if machine_id not in completed_tasks:
        completed_tasks[machine_id] = []
    
    if task_index in completed_tasks[machine_id]:
        return Response({
            'correct': True,
            'message': f'Task already completed!',
            'already_completed': True,
            'task_index': task_index,
        })

    if submitted_answer.lower() == correct_answer.lower():
        points = task.get('points', 10)
        profile.points += points
        profile.save()
        
        # Mark task as completed
        if machine_id not in completed_tasks:
            completed_tasks[machine_id] = []
        completed_tasks[machine_id].append(task_index)
        profile.completed_tasks = completed_tasks
        profile.save()
        
        return Response({
            'correct': True,
            'message': f'Correct answer! +{points} points!',
            'points': points,
            'total_points': profile.points,
            'task_index': task_index,
        })
    return Response({'correct': False, 'message': 'Incorrect answer. Try again!'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_machine_rating(request, pk):
    """Submit or update machine rating - HackTheBox style"""
    try:
        machine = Machine.objects.get(pk=pk)
    except Machine.DoesNotExist:
        return Response({'error': 'Machine not found'}, status=404)

    rating_value = request.data.get('rating')
    
    if not rating_value or rating_value < 1 or rating_value > 5:
        return Response({'error': 'Rating must be between 1 and 5'}, status=400)

    # Create or update rating
    rating, created = MachineRating.objects.update_or_create(
        user=request.user,
        machine=machine,
        defaults={'rating': rating_value}
    )
    
    # Calculate new average rating for machine
    all_ratings = MachineRating.objects.filter(machine=machine)
    avg_rating = all_ratings.aggregate(avg=models.Avg('rating'))['avg']
    machine.rating = round(avg_rating, 1) if avg_rating else 0
    machine.save()
    
    return Response({
        'message': 'Rating submitted successfully!',
        'rating': rating_value,
        'machine_rating': machine.rating,
        'rating_count': all_ratings.count(),
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def complete_machine(request, pk):
    """Mark a machine as completed by the user"""
    try:
        machine = Machine.objects.get(pk=pk)
    except Machine.DoesNotExist:
        return Response({'error': 'Machine not found'}, status=404)
    
    # Get or create user profile
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    
    # Initialize completed_machines if None
    if profile.completed_machines is None:
        profile.completed_machines = []
    
    machine_id = int(pk)
    
    if machine_id not in profile.completed_machines:
        profile.completed_machines.append(machine_id)
        profile.save()
        message = 'Machine marked as completed!'
    else:
        # Already completed, remove it (toggle)
        profile.completed_machines.remove(machine_id)
        profile.save()
        message = 'Machine unmarked as completed.'
    
    return Response({
        'message': message,
        'completed': machine_id in profile.completed_machines,
        'completed_count': len(profile.completed_machines)
    })


# ─────────── LEADERBOARD ───────────

@api_view(['GET'])
@permission_classes([AllowAny])
def leaderboard(request):
    users = User.objects.select_related('profile').filter(
        profile__isnull=False
    ).order_by('-profile__points')[:50]
    data = []
    for i, user in enumerate(users, 1):
        item = LeaderboardSerializer(user).data
        item['position'] = i
        data.append(item)
    return Response(data)


# ─────────── STATS ───────────

@api_view(['GET'])
@permission_classes([AllowAny])
def platform_stats(request):
    return Response({
        'total_users': User.objects.count(),
        'total_rooms': Room.objects.count(),
        'total_machines': Machine.objects.count(),
        'total_flags_captured': TaskSubmission.objects.count() + MachineSubmission.objects.count(),
    })


# ─────────── VPN CONFIGURATION ───────────

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def vpn_custom_config(request):
    """Save custom OVPN config (e.g., from HackTheBox)"""
    if request.method == 'POST':
        config_content = request.data.get('config', '')
        
        if not config_content:
            return Response({'error': 'No config provided'}, status=400)
        
        # Validate it's an OVPN config
        if 'client' not in config_content.lower() or 'openvpn' not in config_content.lower():
            return Response({'error': 'Invalid OVPN config format'}, status=400)
        
        # Save the custom config
        vpn_user, created = VPNUserConfig.objects.update_or_create(
            user=request.user,
            defaults={
                'username': 'custom',
                'config_file': config_content,
                'active': True,
            }
        )
        
        return Response({
            'success': True,
            'message': 'Custom OVPN config saved'
        })
    return Response({'error': 'Method not allowed'}, status=405)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def vpn_config(request):
    """Get or create VPN configuration for user"""
    if request.method == 'GET':
        # Get existing config or return info
        try:
            vpn_user = VPNUserConfig.objects.get(user=request.user, active=True)
            return Response({
                'has_config': True,
                'username': vpn_user.username,
                'config_content': vpn_user.config_file,  # Include config file content
                'created_at': vpn_user.created_at.isoformat(),
            })
        except (VPNUserConfig.DoesNotExist, Exception):
            return Response({
                'has_config': False,
                'message': 'No VPN config. Send POST to create one.'
            })
    
    elif request.method == 'POST':
        # Create new VPN config
        try:
            from django.db import connection
            # Check if lab_network column exists
            try:
                with connection.cursor() as cursor:
                    cursor.execute("PRAGMA table_info(api_vpnconfig)")
                    columns = [row[1] for row in cursor.fetchall()]
            except:
                columns = []
            
            # Get or create global VPN config
            try:
                vpn_global, _ = VPNConfig.objects.get_or_create(
                    is_active=True,
                    defaults={
                        'name': 'CyberTraining VPN',
                        'server_ip': '10.10.10.1',  # VPN server on lab network
                        'server_port': 1194,
                        'server_protocol': 'udp',
                        'vpn_network': '10.8.0.0/24',  # VPN client network
                        'lab_network': '10.10.10.0/24',  # Lab machine network
                        'dns_servers': ['1.1.1.1', '8.8.8.8'],
                    }
                )
            except Exception as e:
                return Response({
                    'error': 'VPN service not available. Please contact admin.',
                    'details': str(e)
                }, status=503)
            
            # Generate unique username and password for user
            username = f"{request.user.username}_{secrets.token_hex(4)}"
            password = secrets.token_hex(16)
            
            # Get lab_network safely (may not exist if migration not run)
            lab_network = vpn_global.lab_network if hasattr(vpn_global, 'lab_network') else '10.10.10.0/24'
            
            # Get dns_servers safely (may not exist if migration not run)
            dns_servers = vpn_global.dns_servers if hasattr(vpn_global, 'dns_servers') else ['1.1.1.1', '8.8.8.8']
            
            # Generate OpenVPN config content
            config_content = generate_openvpn_config(
                server_ip=vpn_global.server_ip,
                server_port=vpn_global.server_port,
                protocol=vpn_global.server_protocol,
                username=username,
                password=password,
                vpn_network=vpn_global.vpn_network,
                dns_servers=dns_servers,
                lab_network=lab_network,
            )
            
            # Save or update user config
            vpn_user, created = VPNUserConfig.objects.update_or_create(
                user=request.user,
                defaults={
                    'username': username,
                    'config_file': config_content,
                    'active': True,
                }
            )
            
            return Response({
                'success': True,
                'username': username,
                'password': password,  # Only returned once!
                'config_content': config_content,
                'message': 'VPN config created! Save your credentials securely.'
            })
        except Exception as e:
            return Response({'error': 'VPN service unavailable: ' + str(e)}, status=503)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def vpn_status(request):
    """Get VPN connection status info"""
    from django.db import connection
    try:
        # Check if lab_network column exists
        try:
            with connection.cursor() as cursor:
                cursor.execute("PRAGMA table_info(api_vpnconfig)")
                columns = [row[1] for row in cursor.fetchall()]
        except:
            columns = []
        
        try:
            vpn_global = VPNConfig.objects.filter(is_active=True).first()
        except Exception as e:
            # Table may not exist yet
            return Response({
                'connected': False,
                'server': None,
                'message': 'VPN not configured. Please contact admin to set up VPN.'
            })
        
        if not vpn_global:
            return Response({
                'connected': False,
                'server': None,
                'message': 'VPN not configured. Please contact admin to set up VPN.'
            })
        
        # Get lab_network safely - may not exist if migration not run
        lab_network = vpn_global.lab_network if hasattr(vpn_global, 'lab_network') and 'lab_network' in columns else '10.10.10.0/24'
        
        # Get dns_servers safely - may not exist if migration not run
        dns = vpn_global.dns_servers if hasattr(vpn_global, 'dns_servers') and 'dns_servers' in columns else ['1.1.1.1', '8.8.8.8']
        
        return Response({
            'connected': True,
            'server': vpn_global.server_ip,
            'port': vpn_global.server_port,
            'protocol': vpn_global.server_protocol,
            'network': vpn_global.vpn_network,
            'lab_network': lab_network,
            'dns': dns,
        })
    except Exception as e:
        return Response({
            'connected': False,
            'server': None,
            'message': 'VPN service unavailable: ' + str(e)
        })


def generate_openvpn_config(server_ip, server_port, protocol, username, password, vpn_network, dns_servers, lab_network='10.10.10.0/24'):
    """Generate OpenVPN configuration in HackTheBox format"""
    
    config = f"""# OpenVPN Client Configuration
# CyberTraining Lab VPN - HackTheBox Format
# ===========================================

client
dev tun
proto {protocol}
remote {server_ip} {server_port}
resolv-retry infinite
nobind
persist-key
persist-tun
remote-cert-tls server
comp-lzo
verb 3
data-ciphers-fallback AES-128-CBC
data-ciphers AES-256-CBC:AES-256-CFB:AES-256-CFB1:AES-256-CFB8:AES-256-OFB:AES-256-GCM
tls-cipher DEFAULT:@SECLEVEL=0
auth SHA256
key-direction 1

# ===========================================
# User Credentials
# Username: {username}
# Password: {password}
# ===========================================

<ca>
-----BEGIN CERTIFICATE-----
MIICHTCCAc+gAwIBAgIQAY7iYDkrdfawj97imrOvBzAFBgMrZXAwZDELMAkGA1UE
BhMCR1IxFTATBgNVBAoTDEhhY2sgVGhlIEJveDEQMA4GA1UECxMHU3lzdGVtczEs
MCoGA1UEAxMjSFRCIFZQTjogUm9vdCBDZXJ0aWZpY2F0ZSBBdXRob3JpdHkwHhcN
MjQwNDE1MTUyOTAwWhcNMzQwNDE1MTUyOTAwWjBtMQswCQYDVQQGEwJHUjEVMBMG
A1UEChMMSGFjayBUaGUgQm94MRAwDgYDVQQLEwdTeXN0ZW1zMTUwMwYDVQQDEyxI
VEIgVlBOOiBldS1zdGFydGluZy1wb2ludC0xLWRoY3AgSXNzdWluZyBDQTAqMAUG
AytlcAMhAFgsADbS3r8RpJRhCrahRsK0N0HvruC0epAiZSLQDc2mo4GNMIGKMA4G
A1UdDwEB/wQEAwIBhjAnBgNVHSUEIDAeBggrBgEFBQcDAgYIKwYBBQUHAwEGCCsG
AQUFBwMJMA8GA1UdEwEB/wQFMAMBAf8wHQYDVR0OBBYEFMcenGuwh0T8bVpqliT9
Aj7uy3TDMB8GA1UdIwQYMBaAFNQHZnqD3OEfYZ6HWsjFzb9UPuDRMAUGAytlcANB
AC/m88Hk3/qti9uorVN0A1Dtp+5BVGnx49Al0AiYAeTECJ0SRSX+m2lC4oG6uSnN
xVp63pG22olz9g4nd7xXjwA=
-----END CERTIFICATE-----
-----BEGIN CERTIFICATE-----
MIIB8zCCAaWgAwIBAgIQAY7Mx8YFd9iyZFCrz3LiKDAFBgMrZXAwZDELMAkGA1UE
BhMCR1IxFTATBgNVBAoTDEhhY2sgVGhlIEJveDEQMA4GA1UECxMHU3lzdGVtczEs
MCoGA1UEAxMjSFRCIFZQTjogUm9vdCBDZXJ0aWZpY2F0ZSBBdXRob3JpdHkwIBcN
MjQwNDExMTA1MDI4WhgPMjA1NDA0MTExMDUwMjhaMGQxCzAJBgNVBAYTAkdSMRUw
EwYDVQQKEwxIYWNrIFRoZSBCb3gxEDAOBgNVBAsTB1N5c3RlbXMxLDAqBgNVBAMT
I0hUQiBWUE46IFJvb3QgQ2VydGlmaWNhdGUgQXV0aG9yaXR5MCowBQYDK2VwAyEA
FLTHpDxXnmG/Xr8aBevajroVu8dkckNnHeadSRza9CCjazBpMA4GA1UdDwEB/wQE
AwIBhjAnBgNVHSUEIDAeBggrBgEFBQcDAgYIKwYBBQUHAwEGCCsGAQUFBwMJMA8G
A1UdEwEB/wQFMAMBAf8wHQYDVR0OBBYEFNQHZnqD3OEfYZ6HWsjFzb9UPuDRMAUG
AytlcANBABl68VB0oo0rSGZWt6L+LNMnyHEJl+CQ+FTjQfzE6oqEMAvJTzdjMyeG
OOUNlQYwGRVajOauFa/IMvDsTBXOgw8=
-----END CERTIFICATE-----
</ca>

<cert>
-----BEGIN CERTIFICATE-----
MIIB1jCCAYigAwIBAgIQAZvfIYy+dwy9DmETKJAZ1TAFBgMrZXAwbTELMAkGA1UE
BhMCR1IxFTATBgNVBAoTDEhhY2sgVGhlIEJveDEQMA4GA1UECxMHU3lzdGVtczE1
MDMGA1UEAxMsSFRCIFZQTjogZXUtc3RhcnRpbmctcG9pbnQtMS1kaGNwIElzc3Vp
bmcgQ0EwHhcNMjYwMTIxMDU1NzU2WhcNMzYwMTIxMDU1NzU2WjBLMQswCQYDVQQG
EwJHUjEVMBMGA1UEChMMSGFjayBUaGUgQm94MRAwDgYDVQQLEwdTeXN0ZW1zMRMw
EQYDVQQDEwptcC0yOTMyODM3MCowBQYDK2VwAyEAKcLYKw0td1LCDsPGJjrzb/Au
98fiIfTUhU1aZFLNhFSjYDBeMA4GA1UdDwEB/wQEAwIHgDAdBgNVHSUEFjAUBggr
BgEFBQcDAgYIKwYBBQUHAwEwDAYDVR0TAQH/BAIwADAfBgNVHSMEGDAWgBTHHpxr
sIdE/G1aapYk/QI+7st0wzAFBgMrZXADQQAv23afuQ8Ih4z8IUFaFb+mnti5bqLp
B3VfoBvNV+NXmZt7ZJAF++YyjERbf2ShIrpFZk0MLMzcuoaLZbupwMgK
-----END CERTIFICATE-----
</cert>

<key>
-----BEGIN PRIVATE KEY-----
MC4CAQAwBQYDK2VwBCIEICwFXpUDAbKQKaPXq97QHi11jBF3TKYr4OAM+YrqUYf+
-----END PRIVATE KEY-----
</key>

<tls-auth>
#
# 2048 bit OpenVPN static key
#
-----BEGIN OpenVPN Static key V1-----
2d1b973f11011e440f9a1b54addd8f4d
b73f3393ccf2c8b68fdd4ee17fddbf56
def04edc1214a42c19e26b126a67556c
2c54c8942a46d9a97668a550beab0965
770757f2e07be1d02bb693f83072a86e
21027003a5da65038668ac35d92b4d0a
c0dae0343d5ffaaecfd57284e42579fb
ef01a67970d0b57098193dcc835fcdbd
6e394b09e637cb828ff015989220ab61
07c941c503296568d161763606d6d95a
a92321a50becbda3069524c0abd105da
7288e13241342e4293e4e6c339eaf282
03b125603d140d6cc6bf1b2d1411d772
036565743adf71e68119660de6f0c604
ffef8ed197a86327110db95e29205ed0
6a3936d0a99f3e3deb746a305a023f23
-----END OpenVPN Static key V1-----
</tls-auth>
"""
    return config


# ─────────── DOCKER MACHINE MANAGEMENT ───────────

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def machine_instance(request, pk):
    """Start or get status of a machine instance"""
    from django.utils import timezone
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from docker_service import docker_manager
    
    try:
        machine = Machine.objects.get(pk=pk)
    except Machine.DoesNotExist:
        return Response({'error': 'Machine not found'}, status=404)
    
    if request.method == 'GET':
        # Get instance status
        try:
            instance = MachineInstance.objects.get(machine=machine, user=request.user)
            
            # Check if Docker container is actually running
            if instance.status == 'running' and instance.container_id:
                try:
                    docker_status = docker_manager.get_machine_status(machine.id, request.user.id)
                    if not docker_status.get('running'):
                        instance.status = 'stopped'
                        instance.save()
                except Exception as e:
                    logger.warning(f"Could not check docker status: {e}")
            
            return Response({
                'machine_id': machine.id,
                'machine_name': machine.name,
                'status': instance.status,
                'container_id': instance.container_id,
                'ip': instance.container_ip,
                'docker_image': instance.docker_image,
                'started_at': instance.started_at.isoformat() if instance.started_at else None,
            })
        except MachineInstance.DoesNotExist:
            return Response({
                'machine_id': machine.id,
                'machine_name': machine.name,
                'status': 'stopped',
            })
        except Exception as e:
            return Response({
                'error': str(e),
                'machine_id': machine.id,
                'machine_name': machine.name,
                'status': 'error'
            })
    
    elif request.method == 'POST':
        # Start machine
        action = request.data.get('action', 'start')
        
        if action == 'start':
            # Get or create instance
            instance, created = MachineInstance.objects.get_or_create(
                machine=machine,
                user=request.user,
                defaults={
                    'docker_image': 'vulnerables/web-dvwa',  # Default, should be configured per machine
                    'status': 'starting'
                }
            )
            
            # Check if already running
            if instance.status == 'running':
                return Response({
                    'message': 'Machine already running',
                    'ip': instance.container_ip,
                    'status': 'running'
                })
            
            # Find an available host port (use range 10000-60000, skip common ports)
            import socket
            import random
            def find_available_port(start=10000, end=60000):
                # Skip commonly used ports
                common_ports = [8080, 8000, 3000, 5000, 8888, 8008, 8443, 9090, 80, 443]
                
                # Try random ports first to avoid conflicts
                try:
                    ports_to_try = random.sample(range(start, min(start+500, end + 1)), min(100, min(start+500, end + 1) - start))
                except:
                    ports_to_try = list(range(start, min(start+100, end + 1)))
                
                for port in ports_to_try:
                    if port in common_ports:
                        continue
                    try:
                        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        s.bind(('', port))
                        s.close()
                        return port
                    except OSError:
                        continue
                
                # Fallback: try sequentially skipping common ports
                for port in range(start, end + 1):
                    if port in common_ports:
                        continue
                    try:
                        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        s.bind(('', port))
                        s.close()
                        return port
                    except OSError:
                        continue
                return None
            
            host_port = find_available_port()
            if not host_port:
                return Response({
                    'success': False,
                    'message': 'No available ports. Please try again later.'
                }, status=500)
            
            # Start Docker container
            try:
                result = docker_manager.start_machine(
                    machine_id=machine.id,
                    user_id=request.user.id,
                    image=instance.docker_image or 'vulnerables/web-dvwa',
                    ports={'80': host_port}  # Dynamic port mapping
                )
            except Exception as e:
                import traceback
                return Response({
                    'success': False,
                    'message': f'Docker error: {str(e)}'
                }, status=500)
            
            if result['success']:
                instance.container_id = result.get('container_id', '')
                instance.container_ip = result.get('ip', '')
                instance.status = 'running'
                instance.started_at = timezone.now()
                instance.save()
                
                return Response({
                    'success': True,
                    'message': result['message'],
                    'ip': instance.container_ip,
                    'port': host_port,  # Return the allocated port
                    'url': f'http://localhost:{host_port}',
                    'container_id': instance.container_id,
                    'status': 'running'
                })
            else:
                instance.status = 'error'
                instance.save()
                return Response({
                    'success': False,
                    'message': result.get('message', 'Failed to start machine')
                }, status=500)
        
        elif action == 'stop':
            try:
                instance = MachineInstance.objects.get(machine=machine, user=request.user)
                
                result = docker_manager.stop_machine(machine.id, request.user.id)
                
                instance.status = 'stopped'
                instance.container_id = ''
                instance.container_ip = None
                instance.stopped_at = timezone.now()
                instance.save()
                
                return Response({
                    'success': True,
                    'message': 'Machine stopped'
                })
            except MachineInstance.DoesNotExist:
                return Response({'message': 'No running instance'})
    
    return Response({'error': 'Invalid action'}, status=400)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_instances(request):
    """Get all running instances for current user"""
    instances = MachineInstance.objects.filter(
        user=request.user,
        status='running'
    ).select_related('machine')
    
    data = []
    for inst in instances:
        data.append({
            'machine_id': inst.machine.id,
            'machine_name': inst.machine.name,
            'ip': inst.container_ip,
            'status': inst.status,
            'started_at': inst.started_at.isoformat() if inst.started_at else None,
        })
    
    return Response(data)


@api_view(['GET'])
@permission_classes([AllowAny])
def docker_status(request):
    """Check Docker availability"""
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    try:
        from docker_service import docker_manager
        available = docker_manager.is_available()
        return Response({
            'available': available,
            'containers': docker_manager.list_containers() if available else [],
            'error_log': getattr(docker_manager, 'last_error', 'No tracking')
        })
    except Exception as e:
        return Response({
            'available': False,
            'error': str(e),
            'containers': [],
            'error_log': getattr(docker_manager, 'last_error', '') if 'docker_manager' in locals() else ''
        })


# ─────────── PWNBOX MANAGEMENT ───────────

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def pwnbox_control(request):
    """
    Start or get status of PwnBox for current user
    POST: Start PwnBox
    GET: Get PwnBox status
    """
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    try:
        from api.pwnbox_manager import start_pwnbox, get_pwnbox_status
    except ImportError as e:
        return Response({
            'error': 'PwnBox not available on this platform. PwnBox requires Docker.',
            'available': False
        }, status=503)
    
    user_id = request.user.id
    
    try:
        if request.method == 'POST':
            result = start_pwnbox(user_id, request.user.username)
            if result.get('success'):
                return Response(result)
            else:
                return Response(result, status=500)
        else:
            # GET - return status
            status = get_pwnbox_status(user_id)
            return Response(status)
    except Exception as e:
        return Response({
            'error': 'PwnBox error: ' + str(e),
            'available': False
        }, status=503)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def pwnbox_stop(request):
    """Stop the user's PwnBox"""
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    try:
        from api.pwnbox_manager import stop_pwnbox
    except ImportError as e:
        return Response({'error': 'PwnBox not available on this platform', 'available': False}, status=503)
    
    user_id = request.user.id
    try:
        result = stop_pwnbox(user_id)
        if result.get('success'):
            return Response(result)
        else:
            return Response(result, status=500)
    except Exception as e:
        return Response({'error': 'PwnBox error: ' + str(e), 'available': False}, status=503)


# ─────────── FRAMES (PUBG Conquer Style) ───────────

@api_view(['GET'])
@permission_classes([AllowAny])
def frame_list(request):
    """Get all available frames with their unlock requirements"""
    frames = Frame.objects.filter(is_active=True).order_by('required_points')
    return Response(FrameSerializer(frames, many=True).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_frames(request):
    """Get user's unlocked frames and current frame selection"""
    try:
        profile = request.user.profile
        return Response({
            'current_frame': profile.frame,
            'unlocked_frames': profile.unlocked_frames or [],
            'points': profile.points
        })
    except UserProfile.DoesNotExist:
        return Response({
            'current_frame': 'default',
            'unlocked_frames': ['default'],
            'points': 0
        })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def select_frame(request):
    """User selects a frame to use (must be unlocked)"""
    frame_id = request.data.get('frame_id')
    
    if not frame_id:
        return Response({'error': 'frame_id is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        profile = request.user.profile
        unlocked = profile.unlocked_frames or []
        
        # Check if frame is unlocked
        # Always allow 'default' frame
        if frame_id != 'default' and frame_id not in unlocked:
            # Check if user has enough points for the frame
            try:
                frame = Frame.objects.get(frame_id=frame_id, is_active=True)
                if profile.points < frame.required_points:
                    return Response({
                        'error': f'Not enough points. Need {frame.required_points} pts to unlock {frame.name}',
                        'required_points': frame.required_points,
                        'your_points': profile.points
                    }, status=status.HTTP_400_BAD_REQUEST)
            except Frame.DoesNotExist:
                return Response({'error': 'Frame not found'}, status=status.HTTP_404_NOT_FOUND)
        
        profile.frame = frame_id
        profile.save()
        
        return Response({
            'success': True,
            'current_frame': profile.frame
        })
    except UserProfile.DoesNotExist:
        return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)


# ─────────── CERTIFICATE SYSTEM ───────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def certificate_eligibility(request):
    """Check if user is eligible for certificate - Admin only"""
    from .models import Machine, MachineSubmission
    from .certificate_generator import check_user_eligibility
    
    # Only admins can generate certificates
    if not request.user.is_superuser:
        return Response({
            'eligible': False,
            'is_admin': False,
            'message': 'Only admins can generate certificates'
        })
    
    eligibility = check_user_eligibility(request.user)
    eligibility['is_admin'] = True
    return Response(eligibility)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_certificate(request):
    """Generate certificate for user who completed all machines - Admin only"""
    import traceback
    
    # Check if user is admin
    if not request.user.is_superuser:
        return Response({
            'error': 'Only admins can generate certificates'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        from .certificate_generator import generate_user_certificate, check_user_eligibility
        
        # Check eligibility first (skip for admins - they can generate for testing)
        eligibility = check_user_eligibility(request.user)
        if not request.user.is_superuser and not eligibility['eligible']:
            return Response({
                'error': eligibility['message'],
                'eligible': False
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Generate certificate
        certificate = generate_user_certificate(request.user)
        
        if certificate:
            return Response({
                'success': True,
                'certificate_id': certificate.certificate_id,
                'issued_date': certificate.issued_date,
                'expiry_date': certificate.expiry_date,
                'download_url': request.build_absolute_uri(certificate.certificate_image.url) if certificate.certificate_image else None
            })
        else:
            return Response({
                'error': 'Failed to generate certificate'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        import traceback
        return Response({
            'error': str(e),
            'trace': traceback.format_exc()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_certificate(request):
    """Get user's certificate if exists"""
    from .models import Certificate
    
    certificate = Certificate.objects.filter(user=request.user).first()
    
    if not certificate:
        return Response({
            'has_certificate': False,
            'message': 'No certificate yet. Complete all machines to get one!'
        })
    
    return Response({
        'has_certificate': True,
        'certificate_id': certificate.certificate_id,
        'issued_date': certificate.issued_date,
        'expiry_date': certificate.expiry_date,
        'download_url': request.build_absolute_uri(certificate.certificate_image.url) if certificate.certificate_image else None
    })


# ─────────── DEEP ML SYSTEM ───────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ml_recommendations(request):
    """Get deep learning powered machine recommendations"""
    try:
        from .deep_ml_system import get_deep_recommendations, DeepLearningRecommender
        
        limit = int(request.query_params.get('limit', 5))
        recommendations = get_deep_recommendations(request.user, limit=limit)
        
        return Response({
            'success': True,
            'recommendations': [
                {
                    'id': r['machine'].id,
                    'name': r['machine'].name,
                    'difficulty': r['machine'].difficulty,
                    'rating': r['machine'].rating,
                    'score': round(r['score'], 3),
                    'reason': r['reason']
                }
                for r in recommendations
            ]
        })
    except Exception as e:
        import traceback
        return Response({
            'error': str(e),
            'trace': traceback.format_exc()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_skill_analysis(request):
    """Analyze user's skill level and performance"""
    try:
        from .deep_ml_system import get_user_skill_prediction, DeepLearningRecommender
        from .models import MachineSubmission
        
        user = request.user
        
        # Get ML predicted skill
        predicted_skill = get_user_skill_prediction(user)
        
        # Get profile info
        try:
            profile = user.profile
            points = profile.points
            rank = profile.rank
            completed_count = len(profile.completed_machines or [])
            unlocked_frames = profile.unlocked_frames or []
        except:
            points = 0
            rank = 'Newbie'
            completed_count = 0
            unlocked_frames = []
        
        # Get submission stats
        total_submissions = MachineSubmission.objects.filter(user=user).count()
        successful_submissions = MachineSubmission.objects.filter(
            user=user, 
            flag_type__in=['user', 'root']
        ).count()
        
        # Category breakdown
        category_stats = {}
        categories = ['web', 'pwn', 'crypto', 'forensics', 'network', 'reverse', 'os', 'misc']
        for cat in categories:
            cat_machines = Machine.objects.filter(name__icontains=cat)
            cat_completed = MachineSubmission.objects.filter(
                user=user,
                machine__in=cat_machines,
                flag_type__in=['user', 'root']
            ).values('machine').distinct().count()
            category_stats[cat] = {
                'completed': cat_completed,
                'total': cat_machines.count()
            }
        
        # Skill level description
        if predicted_skill >= 0.8:
            skill_level = 'Expert'
            skill_desc = 'Master of multiple domains'
        elif predicted_skill >= 0.6:
            skill_level = 'Advanced'
            skill_desc = 'Strong problem-solving abilities'
        elif predicted_skill >= 0.4:
            skill_level = 'Intermediate'
            skill_desc = 'Solid foundational skills'
        elif predicted_skill >= 0.2:
            skill_level = 'Beginner'
            skill_desc = 'Learning the basics'
        else:
            skill_level = 'Novice'
            skill_desc = 'Just starting out'
        
        return Response({
            'success': True,
            'skill_analysis': {
                'predicted_skill': round(predicted_skill, 3),
                'skill_level': skill_level,
                'skill_description': skill_desc,
                'points': points,
                'rank': rank,
                'completed_machines': completed_count,
                'total_submissions': total_submissions,
                'successful_submissions': successful_submissions,
                'success_rate': round(successful_submissions / total_submissions * 100, 1) if total_submissions > 0 else 0,
                'unlocked_frames': unlocked_frames,
                'category_stats': category_stats
            }
        })
    except Exception as e:
        import traceback
        return Response({
            'error': str(e),
            'trace': traceback.format_exc()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def train_ml_model(request):
    """Train the deep learning model (admin only)"""
    if not request.user.is_superuser:
        return Response({
            'error': 'Admin access required'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        from .deep_ml_system import train_deep_model
        
        epochs = int(request.data.get('epochs', 50))
        result = train_deep_model(epochs=epochs)
        
        return Response({
            'success': True,
            'result': result
        })
    except Exception as e:
        import traceback
        return Response({
            'error': str(e),
            'trace': traceback.format_exc()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
