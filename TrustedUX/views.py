from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, redirect

def index(request):
    return render(request,'index.html',{})
def changLang(request,lang_code):
    translation.activate(lang_code)
    print('Language changed')
    return redirect('home')
