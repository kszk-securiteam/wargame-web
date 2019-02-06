from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.admin import UserAdmin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from markdownx.admin import MarkdownxModelAdmin

from .models import *


# Use custom login and logout views instead of django admin defaults
def custom_logout(request):
    return redirect(reverse_lazy('logout'))


admin.site.login = staff_member_required(admin.site.login, login_url=reverse_lazy('login'))
admin.site.logout = custom_logout

# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.register(File)
admin.site.register(Challenge, MarkdownxModelAdmin)
admin.site.register(UserChallenge)
admin.site.register(Submission)
admin.site.register(StaffMember)
