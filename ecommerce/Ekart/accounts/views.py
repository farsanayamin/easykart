from django.shortcuts import render,redirect
from .forms import RegistrationForm
from .models import Account
from django.contrib import messages,auth
from django.contrib.auth.decorators import login_required
from  .models import generate_otp,send_otp_email,is_otp_expired
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.contrib.auth.hashers import make_password
from addressbook.models import UserAddressBook
from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegistrationForm, UserForm, UserProfileForm
from .models import Account, UserProfile
from orders.models import Order, OrderProduct
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

# Verification email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

from carts.views import _cart_id
from carts.models import Cart, CartItem
#otp
import random
from django.conf import settings
from django.utils.encoding import force_text

# Create your views here.
@never_cache
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # Generate OTP
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split("@")[0]
            user = Account.objects.create_user(first_name=first_name, last_name=last_name, email=email, username=username, password=password)
            user.phone_number = phone_number
            p = generate_otp(user)
            send_otp_email(user, p)
            return redirect("otp_verification", id=user.id)
            
    else:
        form = RegistrationForm()
    context = {
        'form': form,
    }
    return render(request, 'accounts/register.html', context)

@never_cache
def login(request):
    if request.method == 'POST':
        email = request.POST['email']

        password = request.POST['password']
        user = auth.authenticate(email=email,password=password)
        if user is not None:
            if user.is_blocked:
                messages.error(request, "you are blocked")
                return redirect("login")
            auth.login(request,user)
            return redirect('home')
        else:
            messages.error(request,'invalid login credentials')
            return redirect('login')
    return render(request,'accounts/login.html')

@never_cache
@login_required(login_url = 'login')
def logout(request):
    auth.logout(request)
    messages.success(request, 'You are logged out.')
    return redirect('login')


#def enterotp(request, id):
    # Check if the request method is POST
    # If the request method is not POST or if it's the initial GET request, render the OTP submission page
    #return render(request, 'accounts/otp.html', {'id': id})
# views.py


@never_cache
def otp_verification(request, id):
    if request.method == "POST":
        account = Account.objects.get(id=id)
        entered_otp = request.POST.get("otp")
        print("Entered OTP:", int(entered_otp))
        
        if is_otp_expired(account):
            messages.error(request, "OTP has expired, please generate a new one.")
            return redirect('otp_verification', id=id)
        
        print("Generated OTP:", account.otp_fld)
        #otp_verified = generate_otp == entered_otp
        #print("OTP Verified:", otp_verified)
        
        if str(account.otp_fld) == str(entered_otp):
            account.is_active = True
            account.save()
            messages.success(request, "Email verified successfully. You can now log in.")
            return redirect('login')
        else:
            messages.error(request, "Invalid OTP. Please try again.")
            return redirect('otp_verification', id=id)  

    return render(request, 'accounts/otp.html', {'id': id})

# resend otp
@never_cache
def resendotp(request, id):
    try:
        # Retrieve the user with the given ID from the database
        user = Account.objects.get(id=id)
        
        
        # Generate a new OTP
        new_otp = generate_otp(user)
       
        # Send the new OTP via email
        send_otp_email(user, new_otp)
        
        # Redirect to the enterotp page with the user ID
        return redirect('otp_verification', id=id)
    
    except Account.DoesNotExist:
        # If the user with the given ID doesn't exist, display an error message
        messages.error(request, "User not found.")
        return redirect('otp_verification', id=id)
    
#@never_cache
#def forgotpassword(request):
    #return render(request,'accounts/forgotPassword.html')

# reset password
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Account, generate_otp, send_otp_email

from django.shortcuts import redirect


from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect

from django.core.exceptions import ObjectDoesNotExist


@never_cache
def forgotPassword(request):
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            user = Account.objects.get(email=email)
        except ObjectDoesNotExist:
            messages.error(request, "No account with that email address exists.")
            return redirect("forgotPassword")
        
        # Generate OTP and send it to the user's email
        otp = generate_otp(user)
        send_otp_email(user, otp)
        
        # Redirect to the OTP verification page with the user ID and otp_verified parameter
        return redirect("otp_password", id=user.id, otp_verified=False)  # Assuming OTP verification starts as False
        
    return render(request, "accounts/forgotPassword.html")




def otp_password(request, id, otp_verified):
    try:
        user = Account.objects.get(id=id)
    except ObjectDoesNotExist:
        messages.error(request, "User not found.")
        return redirect("forgotPassword")

    if request.method == "POST":
        entered_otp = request.POST.get("otp")
        if str(user.otp_fld) == str(entered_otp):
            otp_verified = True
            return redirect("reset_password", id=id, otp_verified=otp_verified)
        else:
            # Check if the OTP has expired
            if is_otp_expired(user):
                messages.error(request, "OTP has expired. Please request a new one.")
            else:
                messages.error(request, "Invalid OTP. Please try again.")
                
    return render(request, "accounts/otp_password.html", {'id': id, 'otp_verified': otp_verified})



def reset_password(request, id, otp_verified):
    if otp_verified:
        try:
            user = Account.objects.get(id=id)
        except ObjectDoesNotExist:
            messages.error(request, "User not found.")
            return redirect("forgotPassword")

        if request.method == "POST":
            new_password = request.POST.get("new_password")
            confirm_password = request.POST.get("confirm_password")

            if new_password == confirm_password:
                user.set_password(new_password)
                user.save()
                messages.success(request, "Password reset successfully.")
                return redirect('login')  # Assuming 'login' is the URL name for your login page
            else:
                messages.error(request, "Passwords do not match.")
                return redirect("reset_password", id=id, otp_verified=True)

        return render(request, "accounts/reset_password.html", {'id': id, 'otp_verified': otp_verified})
    else:
        return redirect("forgotPassword")  # Redirect back to OTP verification if OTP is not verified
    

@login_required(login_url='login')
def my_orders(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')
    context = {
        'orders': orders,
    }
    return render(request, 'accounts/my_orders.html', context)


@login_required(login_url='login')
def edit_profile(request):
    userprofile = get_object_or_404(UserProfile, user=request.user)
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('edit_profile')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=userprofile)
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'userprofile': userprofile,
    }
    return render(request, 'accounts/edit_profile.html', context)


@login_required(login_url='login')
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        user = Account.objects.get(username__exact=request.user.username)

        if new_password == confirm_password:
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                # auth.logout(request)
                messages.success(request, 'Password updated successfully.')
                return redirect('change_password')
            else:
                messages.error(request, 'Please enter valid current password')
                return redirect('change_password')
        else:
            messages.error(request, 'Password does not match!')
            return redirect('change_password')
    return render(request, 'accounts/change_password.html')

'''
@login_required(login_url='login')
def order_detail(request, order_id):
    order_detail = OrderProduct.objects.filter(order__order_number=order_id)
    order = Order.objects.get(order_number=order_id)
    subtotal = 0
    for i in order_detail:
        subtotal += i.product_price * i.quantity

    context = {
        'order_detail': order_detail,
        'order': order,
        'subtotal': subtotal,
    }
    return render(request, 'accounts/order_detail.html', context)
'''
@login_required(login_url='login')
def order_detail(request, order_id):
    order = get_object_or_404(Order,id = order_id)
    order_detail = OrderProduct.objects.filter(order=order)

    subtotal = sum(item.product_price * item.quantity for item in order_detail)

    context = {
        'order_detail': order_detail,
        'order': order,
        
        'subtotal': subtotal
    }
    return render(request, 'dashboard/order_detail.html', context)

@login_required(login_url = 'login')
def dashboard(request):
    orders = Order.objects.order_by('-created_at').filter(user_id=request.user.id, is_ordered=True)
    orders_count = orders.count()

    userprofile = UserProfile.objects.get(user_id=request.user.id)
    context = {
        'orders_count': orders_count,
        'userprofile': userprofile,
    }
    return render(request, 'accounts/dashboard.html', context)


def addressbook(request):
    addresses = UserAddressBook.objects.filter(user = request.user)
    context = {
        'addresses':addresses
    }
    return render(request, 'accounts/addressbook.html', context)
