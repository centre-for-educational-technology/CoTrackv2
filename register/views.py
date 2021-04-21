from mailjet_rest import Client
import os
from django.shortcuts import render
from django.db import transaction
from .forms import RegisterForm
from .forms import LoginForm
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, redirect
from django.utils.encoding import force_bytes
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode
from django.utils.http import urlsafe_base64_encode
from django.contrib import messages
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.conf import settings
from django.utils.translation import gettext as _
from esurvey import views as esurvey_views

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from django.contrib.auth.hashers import check_password
from esurvey.models import AuthorMap

from esurvey.models import Role

from . import tokens as t
from mailjet_rest import Client
import os
import requests
api_key = '490b3c2a909478327e52ad2c921495b4'
api_secret = '5f97d6d72439c79fd395b2a27cdc2955'
mailjet = Client(auth=(api_key, api_secret), version='v3.1')

user_number = 1


def send_mail(data):
    #The mail addresses and password
    sender_address = 'pankajch@tlu.ee'
    sender_pass = 'hanu23man'
    receiver_address = data['Messages']['To']['Email']
    mail_content = data['Messages']['TextPart']

    #Setup the MIME
    message = MIMEMultipart()
    message['From'] = 'CoTrack Team'
    message['To'] = receiver_address
    message['Subject'] = data['Messages']['Subject']   #The subject line
    #The body and the attachments for the mail
    message.attach(MIMEText(mail_content, 'plain'))
    #Create SMTP session for sending the mail
    session = smtplib.SMTP('smtp.gmail.com', 587) #use gmail with port
    session.starttls() #enable security
    session.login(sender_address, sender_pass) #login with mail_id and password
    text = message.as_string()
    session.sendmail(sender_address, receiver_address, text)
    session.quit()
    print('Mail Sent')


# Etherpad interacting function
def call(function,arguments=None):
    try:
        url = settings.ETHERPAD_URL + '/api/1.2.12/' +function+'?apikey='+settings.ETHERPAD_KEY
        print('calling call:',url,' args:',arguments)
        response = requests.post(url,arguments)
        x = response.json()
        print(x)
        return x
    except:

        return False


def login(request):
    #messages.add_message(request, messages.INFO, 'Hello world.')
    if request.method=="POST":
        form=LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            pwd = form.cleaned_data['password']

            try:
                if len(User.objects.all().filter(email=email)) == 0:
                    messages.error(request, 'User does not exists.')
                    return redirect('login')

                user = User.objects.get(email=email)
                print('user exists:',user.username,' pwd:',pwd)
                if not user.is_active:
                    messages.warning(request, 'Your account is not activated.')
                    return redirect('login')

                user_login_status = authenticate(username=user.username,password=pwd)

                print(user_login_status)

                if user_login_status is not None:
                    print('before use backend')
                    user.backend = 'django.contrib.auth.backends.ModelBackend'

                    print('after user backend')
                    auth_login(request,user)



                    print('Checking etherpad id')

                    objs = AuthorMap.objects.all().filter(user=request.user)

                    print(objs,' ',objs.count())
                    if objs.count()>0:
                        authorid = objs[0].authorid
                    else:
                        print('making etherpad api request')
                        res = call('createAuthorIfNotExistsFor',{'authorMapper':request.user.id,'name':request.user.username})
                        authorid = res['data']['authorID']
                        AuthorMap.objects.create(user=request.user,authorid=authorid)

                    user_role = Role.objects.all().filter(user=request.user)

                    print(user_role)

                    if user_role[0].role == 'teacher':
                        return redirect('project_home')
                    else:
                        return redirect('student_entry')


                else:
                    messages.error(request, 'Entered password is wrong.')
                    return redirect('login')
            except Exception as e:
                messages.error(request, 'Etherpad server is not running. Please report it to your service administrator.')
                print(e)
                messages.error(request,e)
                return redirect('login')



        else:
            print('not valid')
            form = LoginForm()
    else:
        if request.user.is_authenticated:
            return redirect('student_entry')
        else:
            form = LoginForm()
    return render(request, "sign_in.html", {"form":form,"title":'Login',"button":'Login'})

# Create your views here.
@transaction.atomic
def register(request):
    if request.method == "POST":
        form=RegisterForm(request.POST)

        print(form)

        if form.is_valid():
            print('form is valid')
            user = form.save(commit=False)

            email = user.email

            user.is_active = False
            user.username = user.email

            user.save()

            subject = 'Activate Your CoTrackV2 Account'
            message = render_to_string('account_activation_email.html', {
                'user': user.first_name,
                'domain': 'www.cotrack.website', #current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': t.account_activation_token.make_token(user),
                })


            print('user pk',user.pk)
            print('base64 code uid:',urlsafe_base64_encode(force_bytes(user.pk)))
            print(t.account_activation_token.make_token(user))
            data = {
              'Messages': {
                  "From": {
                    "Email": "reetkase@tlu.ee",
                    "Name": "CoTrack Team "
                  },
                  "To": {
                      "Email": user.email,
                    },
                  "Subject": "Activate your CoTrack account.",
                  "TextPart": message,
                }
            }



            result = mailjet.send.create(data=data)

            messages.info(request, 'An email with instructions to activate your account has been sent.')

            return redirect('login')


        else:
            print('Form is not valid')

    else:

        form = RegisterForm()

    #return render(request, "register.html", {"form":form})
    return render(request, "sign_up.html", {"form":form})

# Create your views here.


def activate(request, uidb64, token):
    print(uidb64)
    print(force_text(urlsafe_base64_decode(uidb64)))
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        print(uid)
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
        print('user does not exists')
    print('Account activation status:')
    print(t.account_activation_token.check_token(user, token))

    if user is not None and t.account_activation_token.check_token(user, token):
        user.is_active = True

        user.save()
        messages.success(request, 'Your account is activated successfully!.You can login now.')
        return redirect('login')
    else:
        return render(request,'base_page.html',{"title":'Expired link',"content":"The confirmation link is not valid."})


def account_activation_sent(request):
    return render(request,'base_page.html',{"title":'Confirmation email sent',"content":'A email with confirmation link has been sent.'})

def logout(request):
    auth_logout(request)
    return redirect('login')

def password_reset_request(request):
    if request.method == "POST":
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            print('form is valid with email')
            data = password_reset_form.cleaned_data['email']
            associated_users = User.objects.filter(email=data)
            if associated_users.exists():
                print('user exists')

                for user in associated_users:


                    subject = "CoTrack Password Reset"
                    message = render_to_string('password_reset_email.html', {
                        'user': user,
                        'domain': 'www.cotrack.website', #current_site.domain,
                        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                        'token': default_token_generator.make_token(user),
                        'protocol': 'https'
                        })
                    try:
                        data = {
                          'Messages': {
                              "From": {
                                "Email": "reetkase@tlu.ee",
                                "Name": "CoTrackV2 Team "
                              },
                              "To": {
                                  "Email": user.email,
                                },
                              "Subject": "CoTrackV2 Password Reset",
                              "TextPart": message,
                            }
                        }
                        result = mailjet.send.create(data=data)
                    except:
                        return HttpResponse('Error')
                    messages.info(request,'We have emailed you instructions for setting your password, if an account exists with the email you entered. You should receive them shortly. If you do not receive an email, please make sure you have entered the address you registered with, and check your spam folder.')
                    return redirect('login')
    else:
        password_reset_form = PasswordResetForm()
        return render(request,'sign_pwd_reset.html',{'form':password_reset_form})
