from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

# Register your models here.

admin.site.register(User, UserAdmin)
admin.site.register(File)
admin.site.register(Tag)
admin.site.register(Challenge)
admin.site.register(UserChallenge)
admin.site.register(Submission)
