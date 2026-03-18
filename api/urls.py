from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('auth/register/', views.register, name='register'),
    path('auth/login/', views.login_view, name='login'),
    path('auth/me/', views.me, name='me'),
    path('auth/update-avatar/', views.update_avatar, name='update-avatar'),
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

    # Frames (PUBG Conquer Style)
    path('frames/', views.frame_list, name='frame-list'),
    path('frames/my/', views.my_frames, name='my-frames'),
    path('frames/select/', views.select_frame, name='select-frame'),

    # Certificate System
    path('certificate/eligibility/', views.certificate_eligibility, name='certificate-eligibility'),
    path('certificate/generate/', views.generate_certificate, name='generate-certificate'),
    path('certificate/my/', views.my_certificate, name='my-certificate'),

    # Deep ML System
    path('ml/recommendations/', views.ml_recommendations, name='ml-recommendations'),
    path('ml/skill-analysis/', views.user_skill_analysis, name='user-skill-analysis'),
    path('ml/train/', views.train_ml_model, name='train-ml-model'),
]
