from django.contrib import admin
from .models import UserProfile, Room, RoomTask, Machine, RoomMembership, TaskSubmission, MachineSubmission

admin.site.register(UserProfile)
admin.site.register(Room)
admin.site.register(RoomTask)
admin.site.register(Machine)
admin.site.register(RoomMembership)
admin.site.register(TaskSubmission)
admin.site.register(MachineSubmission)
