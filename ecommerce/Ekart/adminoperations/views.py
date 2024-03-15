from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.views.decorators.cache import never_cache
from accounts.models import Account
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate
from django.views.decorators.cache import never_cache

from django.http import HttpResponseServerError
from datetime import date, timedelta
from django.db.models import Sum, Count
from datetime import datetime
from django.db.models import Q
from datetime import datetime


from django.db.models import Q

@never_cache
def admin_login(request):
    if request.method == "POST":
        email = request.POST.get('email')
        print("email:",email)
        password = request.POST.get('password')
        user = authenticate(email=email, password=password)
        if user is not None and user.is_active and user.is_admin:
            login(request, user)
            print("this is farsana")
            messages.success(request, "Welcome, admin!")
            return redirect("adminhome")  # Redirect to admin dashboard
        else:
            messages.error(request, "Invalid email or password for admin.")
            return redirect("adminlogin")  # Redirect back to login page if authentication fails
    return render(request, "admin/admin_login.html")

    

@never_cache
def admin_home(request):

    if "email" not in request.session:
        if "username" in request.session:
            today = date.today()
            year = date.today().year
            start_week = today - timedelta(days=today.weekday())
            end_week = start_week + timedelta(days=6)
            current_date = datetime.now().date()
    return render(request, 'admin/admin_home.html')

# admin  logout
@never_cache
def admin_logout(request):
    if "username" in request.session:
        request.session.flush()
    return redirect("adminlogin")

from django.shortcuts import render
from django.contrib.auth.models import User

def user_manage(request):
    if request.user.is_authenticated:
        # Assuming Account model is your custom user model, replace it with your actual user model
        #user = request.user
        user = Account.objects.filter(is_admin=False)
        context = {"user": user}
        return render(request, "admin/user_management.html", context)
    else:
        return render(request, "404.html", status=404)
    

# block user


def block_user(request, id):
    if request.user.is_authenticated:
        obj = Account.objects.get(id=id)
        obj.is_blocked = True
        obj.save()
        return redirect("usermanage")


# un block user


def un_block_user(request, id):
    if request.user.is_authenticated:
        obj = Account.objects.get(id=id)
        obj.is_blocked = False
        obj.save()
        return redirect("usermanage")
    
# search for user


def search_for_user(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            query = request.POST["query"]
            user = Account.objects.filter(username__icontains=query, is_admin=False)
            context = {
                "user": user,
            }
        return render(request, "admin/user_management.html", context)

