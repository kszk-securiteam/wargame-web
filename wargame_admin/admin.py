from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import redirect
from django.urls import reverse_lazy

# Use custom login and logout views instead of django admin defaults
from wargame_admin.models import StaticContent, Config


def custom_logout(request):
    return redirect(reverse_lazy('logout'))


admin.site.login = staff_member_required(admin.site.login, login_url=reverse_lazy('login'))
admin.site.logout = custom_logout

# Register your models here.
admin.site.register(Config)
admin.site.register(StaticContent)
