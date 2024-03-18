from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
import pyotp
from django.core.mail import send_mail
from django.dispatch import receiver
from django.db.models.signals import post_save
import datetime
from django.utils import timezone


# Create your models here.
class MyAccountManager(BaseUserManager):
    def create_user(self, first_name,last_name, username, email, password=None):
        if not email:
            raise ValueError('User must have an email address')
        
        if not username:
            raise ValueError('User must have an username')
        
        user = self.model(
            email = self.normalize_email(email),
            username = username,
            first_name = first_name,
            last_name =last_name,

        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, first_name, last_name,email,username,password):
        user = self.create_user(
            email = self.normalize_email(email),
            username = username,
            password = password,
            first_name = first_name,
            last_name = last_name,
        )
        user.is_admin = True
        user.is_active =True
        user.is_staff = True
        user.is_superadmin = True
        user.save(using = self._db)
        return user







class Account(AbstractBaseUser):
    first_name   = models.CharField(max_length=50)
    last_name    = models.CharField(max_length=50)
    username     = models.CharField(max_length=50, unique=True)
    email        = models.EmailField(max_length=100,unique=True)
    phone_number = models.CharField(max_length=50)
    otp_fld = models.CharField(max_length=10, blank=True, null=True)
    is_blocked = models.BooleanField(default=False)
    otp_secret = models.CharField(max_length=200,null=True)
    otp_created = models.DateTimeField(auto_now_add=True)
    otp_expiry_time = models.DateTimeField(blank=True, null=True)
    #profile = models.ImageField(upload_to="images/", null=True, blank=True)
    #is_verified = models.BooleanField(default=False)
    #referral_link = models.CharField(max_length=255, unique=True)

    

    #required fieldes -custom model
    date_joined  = models.DateTimeField(auto_now_add=True)
    last_login   = models.DateTimeField(auto_now_add=True)
    is_admin     = models.BooleanField(default = False)
    is_staff     = models.BooleanField(default = False)
    is_active    = models.BooleanField(default = False)
    is_superadmin     = models.BooleanField(default = False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username','first_name','last_name']
    
    objects = MyAccountManager()

    def __str__(self):
        return self.email
    
    def has_perm(self,perm,obj=None):
        return self.is_admin
    
    def has_module_perms(self,add_label):
        return True
    



from datetime import datetime, timedelta
from pyotp import TOTP
from django.core.mail import send_mail
from .models import Account
import pyotp

# OTP generation
def generate_otp(user):
    secret_key = pyotp.random_base32()
    otp = pyotp.TOTP(secret_key, interval=60)
    otp_code = otp.now()
    user.otp_secret = secret_key
    user.otp_fld = otp_code
    user.otp_created = timezone.now() 
    print("hiiiiiiiiii",user.otp_created) # Call timezone.now() as a function
    # Set the OTP expiry time (e.g., 2 minutes from now)
    user.otp_expiry_time = timezone.now() + timezone.timedelta(minutes=2)
    print("model-Generated OTP:", otp_code)
    print("model-User:", user)
    # Save the user object
    user.save()
    return otp_code

# Send OTP email
def send_otp_email(instance, otp_code):
    subject = "OTP Verification"
    message = f"Your OTP for verification is: {otp_code}"
    from_email = "ksajeer12@gmail.com"  # Replace with your email
    send_mail(subject, message, from_email, [instance.email])
'''
# Verify OTP
def verify_otp(user, otp_code):
    generated_otp = user.otp_fld
    secret_key = user.otp_secret
    print("otpcode",otp_code)
    print("secretkey",secret_key)
    return otp_code == generated_otp 
# Verify OTP
    
def verify_otp(user, otp_code):
    secret_key = user.otp_secret
    otp = TOTP(secret_key, interval=60)
    verification_result = otp.verify(otp_code)
    print("Verification Result:", verification_result)
    return verification_result
'''

# Identify expired OTP
from django.utils import timezone

def is_otp_expired(account):
    current_time = timezone.now()
    otp_expiry_time = account.otp_created + timezone.timedelta(minutes=2)  # Adjust as needed
    
    return current_time > otp_expiry_time