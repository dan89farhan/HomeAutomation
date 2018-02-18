from django.shortcuts import render

from django.views import View

from .models import UserActivity

from .forms import LoginForm, UserActivityForm

from django.contrib.auth import authenticate, login, logout, get_user_model

from django.http import HttpResponseRedirect
# Create your views here.

User = get_user_model()

class UserActivityView(View):
    def get(self, request):
        print(UserActivity.objects.checkin.count())
        print(UserActivity.objects.checkin.today().count())
        queryset_list = User.objects.all()
        checked_in_list = []
        for u in queryset_list:
            act = u.useractivity_set.checkin().order_by('-timeStamp').today().first()
            print(act)
        context = {
            'queryset_list':queryset_list
        }
        return render(request, 'timeclock/user-activity-view.html', context)

class ActivityView(View):
    def get(self, request, *args, **kwargs):
        # current activity
        
        if not request.user.is_authenticated:
            return HttpResponseRedirect("/login/")
        # print("User Auth {} User Session ".format(request.session.get('username')))
        if request.session.get('username'):
            
            username_auth = request.user.username
            username_sess = request.session.get('username')
            
        if username_auth == username_sess:
            username = username_auth

            context = {}
            if username:
                form = UserActivityForm(initial={"username": username})
                context['form']  = form
                    
                print(request.user)
                if request.user.is_authenticated:
                    
                    obj = UserActivity.objects.current(request.user)
                    context['object'] = obj
        else:
            logout(request)
            return HttpResponseRedirect("/login/")
        return render(request, "timeclock/activity-view.html",context)

    def post(self, request, *args, **kwargs):
        
        form = UserActivityForm(request.POST)
        context = {'form':form}
        obj = UserActivity.objects.current(request.user)
        context['object'] = obj
        if form.is_valid():
            
            toggle = UserActivity.objects.toggle(request.user)
            context['object'] = toggle

            return HttpResponseRedirect("/")

        return render(request, 'timeclock/activity-view.html', context)

class UserLoginView(View):
    def get(self, request, *args, **kwargs):
        # current activity
        form = LoginForm()
        context = {
            'form': form
            }
        
        return render(request, "timeclock/login-view.html",context)

    def post(self, request, *args, **kwargs):
        
        form = LoginForm(request.POST)
        
        if form.is_valid():
            
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username = username, password = password)
            if user is not None:
                login(request, user)
                request.session['username'] = username
                
            return HttpResponseRedirect("/")
        context = {'form':form}

        return render(request, 'timeclock/login-view.html', context)

class UserLogOutView(View):
    def get(self, request):
        logout(request)
        return HttpResponseRedirect('/')

def activity_view(request, *args, **kwargs):

    if request.method == 'POST':

        new_act = UserActivity.objects.create(user=request.user, activity='checkin')

    return render(request, 'timeclock/activity-view.html', {})