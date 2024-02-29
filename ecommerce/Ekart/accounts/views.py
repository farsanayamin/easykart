from django.shortcuts import render,redirect
from .forms import RegistrationForm
from .models import Account
from django.contrib import messages,auth
from django.contrib.auth.decorators import login_required
from  .models import generate_otp,send_otp_email,is_otp_expired,verify_otp

# email verification
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

#otp
import random
from django.conf import settings
from django.utils.encoding import force_text

# Create your views here.

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
            return redirect("enterotp", user.id)
            
    else:
        form = RegistrationForm()
    context = {
        'form': form,
    }
    return render(request, 'accounts/register.html', context)


def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = auth.authenticate(email=email,password=password)
        if user is not None:
            auth.login(request,user)
            return redirect('home')
        else:
            messages.error(request,'invalid login credentials')
            return redirect('login')
    return render(request,'accounts/login.html')

@login_required(login_url = 'login')
def logout(request):
    auth.logout(request)
    messages.success(request, 'You are logged out.')
    return redirect('login')


def enterotp(request, id):
    # Check if the request method is POST
    if request.method == "POST":
        # Retrieve the entered OTP from the form
        entered_otp = request.POST.get("otp")
        
        try:
            # Retrieve the user with the given ID from the database
            user = Account.objects.get(id=id)
            
            # Compare the entered OTP with the stored OTP
            if entered_otp == user.otp_fld:
                # If OTPs match, mark the user as verified
                user.is_verified = True
                user.save()
                
                # Redirect to the login page with a success message
                messages.success(request, "OTP verified successfully. You can now log in.")
                return redirect('login')
            else:
                # If OTPs don't match, display an error message
                messages.error(request, "Invalid OTP. Please try again.")
                return redirect('enterotp', id=id)
        except Account.DoesNotExist:
            # If the user with the given ID doesn't exist, display an error message
            messages.error(request, "User not found.")
            return redirect('enterotp', id=id)
    
    # If the request method is not POST or if it's the initial GET request, render the OTP submission page
    return render(request, 'accounts/otp.html', {'id': id})
# views.py

'''
def otp_verification(request, id):
    if request.method == "POST":
        account = Account.objects.get(id=id)
        otp = account.otp_fld
        entered_otp = request.POST.get("otp")
        otp = int(otp)
        entered_otp = int(entered_otp)
        if entered_otp == otp:
            user = Account.objects.get(id=id)
            user.is_active = True
            user.save()
            messages.success(request, "Email verified successfully. You can now log in.")
            return redirect('login')
        else:
            messages.error(request, "Invalid OTP. Please try again.")
            return redirect('enterotp', id=id)  # Corrected redirection

    return render(request, 'enterotp')
'''
from django.utils import timezone

def otp_verification(request, id):
    if request.method == "POST":
        account = Account.objects.get(id=id)
        entered_otp = request.POST.get("otp")
        
        if is_otp_expired(account):
            messages.error(request, "OTP has expired generate new one.", extra_tags='expire')
            #print(messages.tags)
            return redirect('enterotp', id=id)
        
        otp_verified = verify_otp(account, entered_otp)
        
        if otp_verified:
            account.is_active = True
            account.save()
            messages.success(request, "Email verified successfully. You can now log in.")
            return redirect('login')
        else:
            messages.error(request, "error:Invalid OTP. Please try again.")
            return redirect('enterotp', id=id)  

    return render(request, 'otp.html')

# resend otp
def resendotp(request, id):
    try:
        # Retrieve the user with the given ID from the database
        user = Account.objects.get(id=id)
        
        # Generate a new OTP
        new_otp = generate_otp(user)
        
        # Send the new OTP via email
        send_otp_email(user, new_otp)
        
        # Redirect to the enterotp page with a success message
        messages.success(request, "OTP has been resent successfully.")
        return redirect('otp_verification', id=id)
    
    except Account.DoesNotExist:
        # If the user with the given ID doesn't exist, display an error message
        messages.error(request, "User not found.")
        return redirect('enterotp', id=id)

