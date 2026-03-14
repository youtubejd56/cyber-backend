from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    RANK_CHOICES = [
        ('Newbie', 'Newbie'),
        ('Script Kiddie', 'Script Kiddie'),
        ('Hacker', 'Hacker'),
        ('Pro Hacker', 'Pro Hacker'),
        ('Elite Hacker', 'Elite Hacker'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    rank = models.CharField(max_length=20, choices=RANK_CHOICES, default='Newbie')
    points = models.IntegerField(default=0)
    avatar = models.URLField(blank=True)
    completed_machines = models.JSONField(default=list)  # List of machine IDs marked as completed

    def save(self, *args, **kwargs):
        # Auto-update rank based on points
        if self.points >= 10000:
            self.rank = 'Elite Hacker'
        elif self.points >= 5000:
            self.rank = 'Pro Hacker'
        elif self.points >= 2000:
            self.rank = 'Hacker'
        elif self.points >= 500:
            self.rank = 'Script Kiddie'
        else:
            self.rank = 'Newbie'
        if not self.avatar:
            self.avatar = f'https://api.dicebear.com/7.x/pixel-art/svg?seed={self.user.username}'
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.user.username} - {self.rank} ({self.points} pts)'


class Room(models.Model):
    DIFFICULTY_CHOICES = [
        ('Easy', 'Easy'), ('Medium', 'Medium'), ('Hard', 'Hard'), ('Insane', 'Insane')
    ]
    CATEGORY_CHOICES = [
        ('Learning Path', 'Learning Path'),
        ('Web Security', 'Web Security'),
        ('Networking', 'Networking'),
        ('Operating Systems', 'Operating Systems'),
        ('Post Exploitation', 'Post Exploitation'),
        ('Cryptography', 'Cryptography'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)
    tags = models.JSONField(default=list)
    rating = models.FloatField(default=4.5)
    members_count = models.IntegerField(default=0)
    image = models.URLField(blank=True)
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class RoomTask(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=200)
    description = models.TextField()
    points = models.IntegerField(default=50)
    flag = models.CharField(max_length=200)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'{self.room.title} - {self.title}'


class RoomMembership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'room']


class TaskSubmission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.ForeignKey(RoomTask, on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'task']


class Machine(models.Model):
    OS_CHOICES = [
        ('Linux', 'Linux'), ('Windows', 'Windows'), ('FreeBSD', 'FreeBSD'),
    ]
    DIFFICULTY_CHOICES = [
        ('Easy', 'Easy'), ('Medium', 'Medium'), ('Hard', 'Hard'), ('Insane', 'Insane')
    ]

    name = models.CharField(max_length=100)
    os = models.CharField(max_length=20, choices=OS_CHOICES)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)
    description = models.TextField()
    tags = models.JSONField(default=list)
    rating = models.FloatField(default=4.0)
    user_flag = models.CharField(max_length=200)
    root_flag = models.CharField(max_length=200)
    user_points = models.IntegerField(default=10)
    root_points = models.IntegerField(default=10)
    ip_address = models.GenericIPAddressField(default='10.10.10.1')
    release_date = models.DateField()
    retired = models.BooleanField(default=True)
    image = models.URLField(blank=True)
    solves_count = models.IntegerField(default=0)
    tasks = models.JSONField(default=list)
    walkthrough_url = models.URLField(blank=True, help_text="URL to download walkthrough PDF")
    download_url = models.URLField(blank=True, help_text="URL to download challenge files (ZIP, etc.)")

    @property
    def total_points(self):
        return self.user_points + self.root_points

    def __str__(self):
        return f'{self.name} ({self.os} - {self.difficulty})'


class MachineSubmission(models.Model):
    FLAG_TYPE_CHOICES = [('user', 'User'), ('root', 'Root')]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE)
    flag_type = models.CharField(max_length=4, choices=FLAG_TYPE_CHOICES)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'machine', 'flag_type']


class MachineRating(models.Model):
    """User ratings for machines - HackTheBox style"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, related_name='ratings')
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])  # 1-5 stars
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'machine']

    def __str__(self):
        return f"{self.user.username} rated {self.machine.name}: {self.rating}"


# ─────────── VPN CONFIGURATION ───────────

class VPNConfig(models.Model):
    """OpenVPN configuration for lab access"""
    name = models.CharField(max_length=100, default='CyberTraining VPN')
    server_ip = models.GenericIPAddressField(help_text="VPN server IP address")
    server_port = models.IntegerField(default=1194, help_text="OpenVPN port")
    server_protocol = models.CharField(max_length=10, choices=[('udp', 'UDP'), ('tcp', 'TCP')], default='udp')
    vpn_network = models.CharField(max_length=50, default='10.8.0.0/24', help_text="VPN client network range (OpenVPN clients)")
    lab_network = models.CharField(max_length=50, default='10.10.10.0/24', help_text="Lab network range (vulnerable machines)")
    dns_servers = models.JSONField(default=list, help_text="DNS servers for VPN")
    is_active = models.BooleanField(default=True)
    ca_cert = models.TextField(blank=True, help_text="CA Certificate")
    ta_key = models.TextField(blank=True, help_text="TLS Auth Key")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"VPN Config - {self.name}"


class VPNUserConfig(models.Model):
    """User-specific VPN configuration"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vpn_configs')
    username = models.CharField(max_length=100)
    config_file = models.TextField(help_text="OpenVPN configuration file content")
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['user', 'username']

    def __str__(self):
        return f"VPN Config for {self.username}"


# ─────────── MACHINE INSTANCES (Docker) ───────────

class MachineInstance(models.Model):
    """Track running Docker container instances"""
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, related_name='instances')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='machine_instances')
    container_id = models.CharField(max_length=64, blank=True)
    container_ip = models.GenericIPAddressField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('stopped', 'Stopped'),
        ('starting', 'Starting'),
        ('running', 'Running'),
        ('stopping', 'Stopping'),
        ('expired', 'Expired'),
        ('error', 'Error'),
    ], default='stopped')
    docker_image = models.CharField(max_length=200, help_text="Docker image to use")
    started_at = models.DateTimeField(null=True, blank=True)
    stopped_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True, help_text="When this instance expires")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['machine', 'user']

    def __str__(self):
        return f"{self.machine.name} - {self.user.username} - {self.status}"
