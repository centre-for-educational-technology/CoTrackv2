from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, redirect
from django.urls import reverse
from django.conf import settings
from django.utils.translation import activate
from urllib.parse import unquote
from django.urls import translate_url
from django.utils.http import is_safe_url
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.translation import (
    LANGUAGE_SESSION_KEY, check_for_language, get_language,
)
def index(request):
    print('Index called')
    return render(request,'index_soft.html',{})

def about(request):
    return render(request,'index_soft_aboutus.html')

def workshop(request):
    return render(request,'index_soft_workshop.html')

def how(request):
    return render(request,'index_soft_resources.html')

def changLang(request,lang_code):
    next = request.META.get('HTTP_REFERER')
    next = next and unquote(next)  # HTTP_REFERER may be encoded.
    print('URL:',next)
    if not is_safe_url(url=next, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
        next = '/'
    if lang_code == 'et':
        next = next.replace('/en/','/et/')
    print('After replacement:',next)
    response = HttpResponseRedirect(next) if next else HttpResponse(status=204)
    if lang_code and check_for_language(lang_code):
        if next:
            next_trans = translate_url(next, lang_code)
        if next_trans != next:
            response = HttpResponseRedirect(next_trans)
        if hasattr(request, 'session'):
            request.session[LANGUAGE_SESSION_KEY] = lang_code
        response.set_cookie(
            settings.LANGUAGE_COOKIE_NAME, lang_code,
            max_age=settings.LANGUAGE_COOKIE_AGE,
            path=settings.LANGUAGE_COOKIE_PATH,
            domain=settings.LANGUAGE_COOKIE_DOMAIN,
            )
    return response
