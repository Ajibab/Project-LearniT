from django.contrib import admin

from .models import User, PendingUser, UserProfile, Token

admin.site.register(User)
admin.site.register(PendingUser)
admin.site.register(UserProfile)
