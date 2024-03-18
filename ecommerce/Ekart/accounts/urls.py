from django.urls import path
from .import views


urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    #path('accounts/activate/<str:uidb64>/<str:token>/',views.activate,name='activate'),
    #path('otpsubmition/<int:id>/', views.enterotp, name='enterotp'),
    #path('otpsubmition/<int:id>/', views.otp_verification, name='enterotp'),
    #path('otpsubmission/enter/<int:id>/', views.enterotp, name='enterotp'),
    path('otpsubmission/verify/<int:id>/', views.otp_verification, name='otp_verification'),
    path('resendotp/<int:id>/',views.resendotp,name='resendotp' ),
    path('forgotPassword/',views.forgotPassword, name='forgotPassword'),
    #path('forgotPassword/otp/<int:id>/', views.otp_verification_forgot,name ='otp_verification_forgot'),
    path('otp_password/<int:id>/<str:otp_verified>/', views.otp_password, name='otp_password'),
    path('reset_password/<int:id>/<str:otp_verified>/', views.reset_password, name='reset_password'),
    
]