"""TrustedUX URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from register import views as v
from esurvey import views as sv
from . import views
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('admin/', admin.site.urls),
    path("register/", v.register, name="register"),
    path("password_reset/",v.password_reset_request, name='password_reset'),
    path("password_reset/done",auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
    path('password_reset/confirm/<slug:uidb64>/<slug:token>/',auth_views.PasswordResetConfirmView.as_view(template_name="password_reset_confirm.html"), name='password_reset_confirm'),
    path('password_reset/complete/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),
    path('api-auth/', include('rest_framework.urls')),


    path('account_activation_sent/', v.account_activation_sent, name='account_activation_sent'),
    path('activate/<slug:uidb64>/<slug:token>/',v.activate, name='activate'),
    path('',include("esurvey.urls")),  # <-- added
    path('', v.login,name='login'),
    path('logout/',v.logout,name='logout'),
    path('home/',views.index,name='home'),
    path('accounts/', include('allauth.urls')),
    path('changeLang/<lang_code>',views.changLang,name='change_language'),
    path('djrichtextfield/', include('djrichtextfield.urls'))
]
