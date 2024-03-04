from django.shortcuts import render,redirect
from .forms import RegistrationForm
from .models import Account
from django.contrib import messages,auth
from django.contrib.auth.decorators import login_required
from  .models import generate_otp,send_otp_email,is_otp_expired,verify_otp
from django.utils import timezone
from django.views.decorators.cache import never_cache

# email verification
#from django.contrib.sites.shortcuts import get_current_site
#from django.template.loader import render_to_string
#from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
#from django.utils.encoding import force_bytes
#from django.contrib.auth.tokens import default_token_generator
#from django.core.mail import EmailMessage

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
def otp_verification(request, id , reset=None):
    if request.method == "POST":
        account = Account.objects.get(id=id)
        entered_otp = request.POST.get("otp")
        
        if is_otp_expired(account):
            messages.error(request, "OTP has expired, please generate a new one.")
            return redirect('otp_verification', id=id)
        
        otp_verified = verify_otp(account, entered_otp)
        
        if otp_verified:
            if reset:
                # OTP verification for password reset
                return redirect("reset_password", id=id)  # Redirect to password reset page
            else:
                return redirect("login")  # Redirect to login page if not resetting password
        else:
            messages.error(request, "Invalid OTP. Please try again.")
            return render(request, 'accounts/reset_password.html', {'id': account.id})  

    return render(request, 'accounts/otp.html', {'id': id, 'reset': reset})


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
from .models import Account, generate_otp, send_otp_email, verify_otp
from django.urls import reverse

@never_cache
def forgotPassword(request):
    if request.method == "POST":
        email = request.POST.get("email")
        reset =True
        try:
            user = Account.objects.get(email=email)
        except Account.DoesNotExist:
            messages.error(request, "No account with that email address exists.")
            return redirect("forgotPassword")
        
        # Generate OTP
        otp_code = generate_otp(user)
        
        # Send OTP via email
        send_otp_email(user, otp_code)
     
        redirect_url = reverse("otp_verification", kwargs={'id': user.id, 'reset': True})
        print("Redirect URL:", redirect_url)
        return redirect(redirect_url)
        
        
        # Verify OTP
        '''
        entered_otp = request.POST.get("otp")
        if verify_otp(user, entered_otp):
            # If OTP is verified, redirect to password reset form
            return redirect("reset_password", id=user.id)
        else:
            messages.error(request, "Invalid OTP. Please try again.")
            return redirect("forgotPassword")  
'''
    return render(request, "accounts/forgotPassword.html")

from django.shortcuts import render, get_object_or_404
from django.views.decorators.cache import never_cache
from .models import Account


@never_cache
def reset_password(request, id):
    user = get_object_or_404(Account, id=id)
    return render(request, 'accounts/reset_password.html', {'id': user.id})

    
