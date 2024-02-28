from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
import pyotp
from django.core.mail import send_mail
from django.dispatch import receiver
from django.db.models.signals import post_save
import datetime


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
    


# otp generation
def generate_otp(user):
    secret_key = pyotp.random_base32()
    otp = pyotp.TOTP(secret_key,interval=60)
    otp_code = otp.now()
    Account.objects.update(otp_secret=secret_key, otp_fld=otp_code)
    return otp_code


# Send OTP email
def send_otp_email(instance, otp_code):
    subject = "OTP Verification"
    message = f"Your OTP for verification is: {otp_code}"
    from_email = "ksajeer12@gmail.com"  # Replace with your email
    send_mail(subject, message, from_email, [instance.email])


# signal to post save
@receiver(post_save, sender=Account)
def generate_and_send_otp(sender, instance, created, **kwargs):
    if created:
        otp_code = generate_otp(instance)
        send_otp_email(instance, otp_code)