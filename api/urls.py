from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('auth/register/', views.register, name='register'),
    path('auth/login/', views.login_view, name='login'),
    path('auth/me/', views.me, name='me'),
    path('auth/create-superuser/', views.create_superuser, name='create-superuser'),

    # Rooms
    path('rooms/', views.room_list, name='room-list'),
    path('rooms/<int:pk>/', views.room_detail, name='room-detail'),
    path('rooms/<int:pk>/join/', views.join_room, name='join-room'),
    path('rooms/<int:room_pk>/tasks/<int:task_pk>/submit/', views.submit_task_flag, name='submit-task'),

    # Machines
    path('machines/', views.machine_list, name='machine-list'),
    path('machines/<int:pk>/', views.machine_detail, name='machine-detail'),
    path('machines/<int:pk>/submit-flag/', views.submit_machine_flag, name='submit-machine-flag'),
    path('machines/<int:pk>/submit-task/', views.submit_machine_task, name='submit-machine-task'),
    path('machines/<int:pk>/rate/', views.submit_machine_rating, name='submit-machine-rating'),
    path('machines/<int:pk>/complete/', views.complete_machine, name='complete-machine'),

    # Leaderboard & Stats
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('stats/', views.platform_stats, name='stats'),

    # VPN Configuration
    path('vpn/config/', views.vpn_config, name='vpn-config'),
    path('vpn/custom-config/', views.vpn_custom_config, name='vpn-custom-config'),
    path('vpn/status/', views.vpn_status, name='vpn-status'),
    
    # PwnBox Configuration
    path('pwnbox/', views.pwnbox_control, name='pwnbox-control'),
    path('pwnbox/stop/', views.pwnbox_stop, name='pwnbox-stop'),

    # Docker Machine Management
    path('machines/<int:pk>/instance/', views.machine_instance, name='machine-instance'),
    path('instances/', views.user_instances, name='user-instances'),
    path('docker/status/', views.docker_status, name='docker-status'),
]
