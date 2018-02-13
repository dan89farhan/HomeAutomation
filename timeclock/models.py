from django.db import models
from django.conf import settings

from django.core.exceptions import ValidationError
# Create your models here.


# 1.User

# 2. Dialy Time Clock

# 3.In and Out per Day



USER_ACTIVITY_CHOICES = [
    ('checkin', 'Check In'),
    ('checkout', 'Check Out')
]

class UserActivityManager(models.Manager):

    def current(self, user = None):
        if user is None:
            return None
        current_obj = self.get_queryset().filter(user=user).order_by('-timeStamp').first()
        return current_obj

    def toggle(self, user):
        last_item = self.current(user)
        
        activity = 'checkin'
        if last_item is not None:
            if last_item.activity == 'checkin':
                activity = 'checkout'

        obj = self.model(
            user = user,
            activity = activity
        )    
        obj.save()
        return obj


            


class UserActivity(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    activity = models.CharField(max_length = 120, default = 'checkin', choices = USER_ACTIVITY_CHOICES)
    timeStamp = models.DateTimeField(auto_now_add=True)

    objects = UserActivityManager()

    def __str__(self):
        return str(self.activity)

    class Meta:
        verbose_name = 'Activity'
        verbose_name_plural = 'User Activities'

    def next_activity(self):
        next = 'Check In'
        if self.activity == 'checkin':
            next = 'Check Out'
        return next

    def clean(self, *args, **kwargs):
        if self.user:
            user_activities = UserActivity.objects.exclude(
                id = self.id
            ).filter(
                user = self.user
            ).order_by('-timeStamp')
            if user_activities.exists():
                recent_ = user_activities.first()
                if self.activity == recent_.activity:
                    raise ValidationError("{} is not a valid activity for this user".format(self.get_activity_display()))
            
            else:
                if self.activity != "checkin":
                    raise ValidationError("{} is not a valid activity for this user as first activity".format(self.get_activity_display()))
        return super(UserActivity, self).clean(*args, **kwargs)