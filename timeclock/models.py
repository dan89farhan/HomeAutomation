from django.db import models
from django.conf import settings

from django.core.exceptions import ValidationError

from django.conf import settings

from django.utils import timezone

from datetime import timedelta, datetime, time


# Create your models here.


# 1.User

# 2. Dialy Time Clock

# 3.In and Out per Day

ACTIVITY_TIME_DELTA = getattr(settings, "ACTIVITY_TIME_DELTA", timedelta(minutes = 1))

USER_ACTIVITY_CHOICES = [
    ('checkin', 'Check In'),
    ('checkout', 'Check Out')
]

class UserActivityQuerySet(models.query.QuerySet):

    def today(self):
        now = timezone.now()
        today_start = timezone.make_aware(datetime.combine(now, time.min))
        today_end = timezone.make_aware(datetime.combine(now, time.max))
        return self.filter(timeStamp__gte=today_start).filter(timeStamp__lte=today_end)

    def checkin(self):
        return self.filter(activity = 'checkin')

    def checkout(self):
        return self.filter(activity = 'checkout')

    def current(self, user=None):
        if user is None:
            return self
        return self.filter(user=user).order_by('-timestamp').first()


class UserActivityManager(models.Manager):

    def get_queryset(self):
        return UserActivityQuerySet(self.model, using=self._db)

    def checkin(self):
        return self.get_queryset().checkin()

    def checkout(self):
        return self.get_queryset().checkout()
    def current(self, user = None):
        
        if user is None:
            return None
        current_obj = self.get_queryset().current(user)
        
        return current_obj

    def toggle(self, user = None):
        if user is None:
            return None
        
        last_item = self.current(user)
        
        activity = 'checkin'
        if last_item is not None:
            
            now = timezone.now()
            diff = last_item.timeStamp + ACTIVITY_TIME_DELTA
            if diff > now:
                return None

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
    @property
    def next_activity(self):
        next = 'Check In'
        if self.activity == 'checkin':
            next = 'Check Out'
        return next

    @property
    def current(self):
        current= 'Checked Out'
        if self.activity == 'checkin':
            current = 'Checked In'
        return current
        

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