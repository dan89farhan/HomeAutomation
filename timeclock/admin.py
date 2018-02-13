from django.contrib import admin

# Register your models here.
from .models import UserActivity
# from timeclock.models import UserActivity


class UserActivityAdmin(admin.ModelAdmin):

    search_fields = ['user__username', 'user__email']
    list_display = ('user','__str__', 'timeStamp')
    list_filter = ['timeStamp']

    class Meta:
        model = UserActivity

admin.site.register(UserActivity, UserActivityAdmin)