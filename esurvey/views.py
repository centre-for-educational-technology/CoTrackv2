from django.shortcuts import render
from django.http import HttpResponse
import io
from formtools.wizard.views import SessionWizardView
from django import forms
from django.db import transaction
from django.contrib import messages
import uuid
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import redirect
from django.db.models import Count
from django.db.models import Sum
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django import forms
from django.db import transaction
from django.contrib.auth import login as auth_login
from django.contrib.auth.models import User
from django.db import transaction
from django.utils.translation import gettext as _
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from bs4 import BeautifulSoup
import datetime
import re
import time
import csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import urllib, base64

from esurvey.models import Role
from django.contrib.auth import login as auth_login
from django.contrib.auth.models import User
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

import uuid
from datetime import date, timedelta
from formtools.wizard.views import SessionWizardView
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator

from .forms import CreateForm1,CreateForm2,CreateForm3,CreateForm4, consentForm, AudioflForm, VADForm, SpeechForm, HelpForm
from .models import  Pad,Session,SessionGroupMap, AuthorMap, VAD, UsabilityQ, CollaborationQ, EngagementQ, Consent, activityLog, Speech, GroupPin, Help
from .models import Audiofl
from esurvey.models import Role
import os
from django.core.files.base import File
from django.shortcuts import render, redirect
import requests

import jwt

CREATE_FORMS = (
    ("activity_info", CreateForm1),
    ("task", CreateForm2),
    ("config", CreateForm3),
    ("overview",CreateForm4))

TEMPLATES = {"activity_info": "create_activity_info.html",
             "task": "create_task.html",
             "config": "create_config.html",
             "overview": "create_summary.html"}




################### Changeset Processing ######################
def changeset_parse (c) :
    changeset_pat = re.compile(r'^Z:([0-9a-z]+)([><])([0-9a-z]+)(.+?)\$')
    op_pat = re.compile(r'(\|([0-9a-z]+)([\+\-\=])([0-9a-z]+))|([\*\+\-\=])([0-9a-z]+)')

    def parse_op (m):
        g = m.groups()
        if g[0]:
            if g[2] == "+":
                op = "insert"
            elif g[2] == "-":
                op = "delete"
            else:
                op = "hold"
            return {
                'raw': m.group(0),
                'op': op,
                'lines': int(g[1], 36),
                'chars': int(g[3], 36)
            }
        elif g[4] == "*":
            return {
                'raw': m.group(0),
                'op': 'attr',
                'index': int(g[5], 36)
            }
        else:
            if g[4] == "+":
                op = "insert"
            elif g[4] == "-":
                op = "delete"
            else:
                op = "hold"
            return {
                'raw': m.group(0),
                'op': op,
                'chars': int(g[5], 36)
            }

    m = changeset_pat.search(c)
    bank = c[m.end():]
    g = m.groups()
    ops_raw = g[3]
    op = None

    ret = {}
    ret['raw'] = c
    ret['source_length'] = int(g[0], 36)
    ret['final_op'] = g[1]
    ret['final_diff'] = int(g[2], 36)
    ret['ops_raw'] = ops_raw
    ret['ops'] = ops = []
    ret['bank'] = bank
    ret['bank_length'] = len(bank)
    for m in op_pat.finditer(ops_raw):
        ops.append(parse_op(m))
    return ret

def perform_changeset_curline (text, c):
    textpos = 0
    curline = 0
    curline_charpos = 0
    curline_insertchars = 0
    bank = c['bank']
    bankpos = 0
    newtext = ''
    current_attributes = []

    # loop through the operations
    # rebuilding the final text
    for op in c['ops']:
        if op['op'] == "attr":
            current_attributes.append(op['index'])
        elif op['op'] == "insert":
            newtextposition = len(newtext)
            insertion_text = bank[bankpos:bankpos+op['chars']]
            newtext += insertion_text
            bankpos += op['chars']
            if 'lines' in op:
                curline += op['lines']
                curline_charpos = 0
            else:
                curline_charpos += op['chars']
                curline_insertchars = op['chars']
            # todo PROCESS attributes
            # NB on insert, the (original/old/previous) textpos does *not* increment...
        elif op['op'] == "delete":
            newtextposition = len(newtext) # is this right?
            # todo PROCESS attributes
            textpos += op['chars']

        elif op['op'] == "hold":
            newtext += text[textpos:textpos+op['chars']]
            textpos += op['chars']
            if 'lines' in op:
                curline += op['lines']
                curline_charpos = 0
            else:
                curline_charpos += op['chars']

    # append rest of old text...
    newtext += text[textpos:]
    return newtext, curline, curline_charpos, curline_insertchars
###############################################################

def recordLog(session,actor,verb,object):
    print('Logging the activity')
    activityLog.objects.create(session=session,actor=actor,verb=verb,object=object)
    return True

def isTeacher(request):
    current_user = request.user
    role_obj = Role.objects.get(user=current_user)

    if role_obj.role == 'teacher':
        print('Passed the test')
        return True
    else:
        return False

def isAdmin(request):
    current_user = request.user
    return current_user.is_staff

# Etherpad interacting function
def call(function,arguments=None,request=None):
    try:
        url = settings.ETHERPAD_URL + '/api/1.2.12/' +function+'?apikey='+settings.ETHERPAD_KEY
        response = requests.post(url,arguments)
        x = response.json()
        print('Returned:x',x)
        return x
    except:
        messages.error(request,'The etherpad server is not accessible. Please check your etherpad server and configuration.')
        return redirect('project_home')

def model_form_upload(request):
    if request.method == 'POST':
        form = AudioflForm(request.POST, request.FILES)
        print('function called')
        if form.is_valid():
            newform = form.save(commit=False)
            print('valid form')
            djfile = File(request.FILES['fl'])
            newform.fl.save(request.FILES['fl'].name, djfile)
            newform.save()
            print('data saved')
            # convert to fix the duration of audio
            file_path = newform.fl.path
            #os.system("/usr/bin/mv %s %s" % (file_path, (file_path + '.original')))
            #os.system("/usr/bin/ffmpeg -i %s -c copy -fflags +genpts %s" % ((file_path + '.original'), file_path))
            return redirect('/')
    else:
        form = AudioflForm()
    return render(request, 'model_form_upload.html', {
        'form': form
    })

def list_files(request):
    files = Audiofl.objects.all().order_by('uploaded_at')

    return render(request, 'list_files.html', {
        'files': files
    })

def is_valid_uuid(val):
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False

def error_404(request):
    return render(request,'error_404.html')



def downloadFileTimestamp(request,session_id):
    session = Session.objects.all().filter(id=session_id)
    if session.count() == 0:
        messages.error(request,'Specified session id is invalid')
        return redirect('project_home')
    else:
        session = Session.objects.get(id=session_id)
        # Preparing csv data File#####
        fname = session.name + '_file_metadata.csv'
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment;filename="' + fname +'"'
        writer = csv.writer(response)
        writer.writerow(['timestamp','user','group','sequence','filename'])
        vads = Audiofl.objects.all().filter(session=session)
        for v in vads:
            writer.writerow([v.description,v.user.email,v.group,v.sequence,v.fl.name])
    return response

def downloadVad(request,session_id):
    session = Session.objects.all().filter(id=session_id)
    if session.count() == 0:
        messages.error(request,'Specified session id is invalid')
        return redirect('project_home')
    else:
        session = Session.objects.get(id=session_id)
        # Preparing csv data File#####
        fname = session.name + '_vad.csv'
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment;filename="' + fname +'"'
        writer = csv.writer(response)
        writer.writerow(['timestamp','user','group','speaking_time(sec.)'])
        vads = VAD.objects.all().filter(session=session)
        for v in vads:
            writer.writerow([v.timestamp,v.user.email,v.group,(v.activity/1000)])
    return response

def downloadSpeech(request,session_id):
    session = Session.objects.all().filter(id=session_id)
    if session.count() == 0:
        messages.error(request,'Specified session id is invalid')
        return redirect('project_home')
    else:
        session = Session.objects.get(id=session_id)
        # Preparing csv data File#####
        fname = session.name + '_speech.csv'
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment;filename="' + fname +'"'
        writer = csv.writer(response)
        writer.writerow(['timestamp','user','group','speech'])
        objs = Speech.objects.all().filter(session=session)
        for obj in objs:
            writer.writerow([obj.timestamp,obj.user.email,obj.group,obj.TextField])
    return response

def downloadChat(request,session_id):
    session = Session.objects.all().filter(id=session_id)
    if session.count() == 0:
        messages.error(request,'Specified session id is invalid')
        return redirect('project_home')
    else:
        session = Session.objects.get(id=session_id)
        # Preparing csv data File#####
        fname = session.name + '_chat.csv'

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment;filename="' + fname +'"'

        writer = csv.writer(response)
        writer.writerow(['timestamp','authorid','message'])
        ##############################
        pad = Pad.objects.all().filter(session=session)
        for p in pad:
            padid =  p.eth_padid
            params = {'padID':padid}
            print('padid:',padid)
            authors = call('getChatHistory',params)
            print(authors)
            if  authors['data'] is None:
                continue

            for msg in authors['data']['messages']:
                print([datetime.datetime.fromtimestamp(msg["time"]/1000).strftime('%H:%M:%S %d-%m-%Y'),msg["userId"],msg["text"]])
                #print(datetime.datetime.fromtimestamp(tp/1000).strftime('%H:%M:%S %d-%m-%Y'))
                #print('   ',datetime.datetime.fromtimestamp(tp/1000).strftime('%H:%M:%S %d-%m-%Y'));
                writer.writerow([datetime.datetime.fromtimestamp(msg["time"]/1000).strftime('%H:%M:%S %d-%m-%Y'),msg["userId"],msg["text"]])
            #print(datetime.datetime.utcfromtimestamp(d["data"]/1000).strftime('%Y-%m-%d %H:%M:%S'),',',pad.group,',',cs["bank"],',',cs["source_length"],',',cs["final_diff"],',',cs["final_op"],',',rev["data"],',',ath["data"])
    return response

def downloadFileTimestamp(request,session_id):
    session = Session.objects.all().filter(id=session_id)
    if session.count() == 0:
        messages.error(request,'Specified session id is invalid')
        return redirect('project_home')
    else:
        session = Session.objects.get(id=session_id)
        # Preparing csv data File#####
        fname = session.name + '_vad.csv'
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment;filename="' + fname +'"'
        writer = csv.writer(response)
        writer.writerow(['timestamp','user','group','sequence','filename'])
        vads = Audiofl.objects.all().filter(session=session)
        for v in vads:
            writer.writerow([v.description,v.user.email,v.group,v.sequence,v.fl.name])
    return response

def downloadVad(request,session_id):
    session = Session.objects.all().filter(id=session_id)
    if session.count() == 0:
        messages.error(request,'Specified session id is invalid')
        return redirect('project_home')
    else:
        session = Session.objects.get(id=session_id)
        # Preparing csv data File#####
        fname = session.name + '_vad.csv'
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment;filename="' + fname +'"'
        writer = csv.writer(response)
        writer.writerow(['timestamp','user','group','speaking_time(sec.)'])
        vads = VAD.objects.all().filter(session=session)
        for v in vads:
            writer.writerow([v.timestamp,v.user.email,v.group,(v.activity/1000)])
    return response

def downloadMapping(request,session_id):
    session = Session.objects.all().filter(id=session_id)
    if session.count() == 0:
        messages.error(request,'Specified session id is invalid')
        return redirect('project_home')
    else:
        session = Session.objects.get(id=session_id)
        # Preparing csv data File#####
        fname = session.name + '_mapping.csv'
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment;filename="' + fname +'"'
        writer = csv.writer(response)
        writer.writerow(['username','email','authorid'])
        ##############################
        pad = Pad.objects.all().filter(session=session)
        for p in pad:
            padid =  p.eth_padid
            params = {'padID':padid}
            print('padid:',padid)
            authors = call('listAuthorsOfPad',params)
            print(authors)
            for auth in authors['data']['authorIDs']:
                aid = auth
                author = AuthorMap.objects.filter(authorid=aid)
                print(author[0].user.username,author[0].user.email,aid)
                #print(datetime.datetime.fromtimestamp(tp/1000).strftime('%H:%M:%S %d-%m-%Y'))
                #print('   ',datetime.datetime.fromtimestamp(tp/1000).strftime('%H:%M:%S %d-%m-%Y'));
                writer.writerow([author[0].user.username,author[0].user.email,aid])
            #print(datetime.datetime.utcfromtimestamp(d["data"]/1000).strftime('%Y-%m-%d %H:%M:%S'),',',pad.group,',',cs["bank"],',',cs["source_length"],',',cs["final_diff"],',',cs["final_op"],',',rev["data"],',',ath["data"])
    return response


def downloadLog(request,session_id):
    session = Session.objects.all().filter(id=session_id)
    if session.count() == 0:
        messages.error(request,'Specified session id is invalid')
        return redirect('project_home')
    else:
        session = Session.objects.get(id=session_id)
        # Preparing csv data File#####
        fname = session.name + '_logs.csv'

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment;filename="' + fname +'"'

        writer = csv.writer(response)
        writer.writerow(['timestamp','author','group','char_bank','source_length','operation','difference','text'])

        print('text included')

        ##############################


        pad = Pad.objects.all().filter(session=session)


        for p in pad:

            padid =  p.eth_padid
            params = {'padID':padid}
            rev_count = call('getRevisionsCount',params)



            for r in range(rev_count['data']['revisions']):
                if r == 327 or r == 329:
                    continue
                params = {'padID':padid,'rev':r+1}
                rev = call('getRevisionChangeset',params)
                ath = call('getRevisionAuthor',params)

                d = call('getRevisionDate',params)
                t = call('getText',params)

                print('Rev:',r,'Changeset:',rev['data'])

                cs = changeset_parse(rev['data'])
                tp = int(d['data'])
                text = t['data']['text']['text']
                char_bank = cs['bank']

                char_bank = "<br/>".join(char_bank.split("\n"))
                text = "<br/>".join(text.split("\n"))

                #print(datetime.datetime.fromtimestamp(tp/1000).strftime('%H:%M:%S %d-%m-%Y'))
                #print('   ',datetime.datetime.fromtimestamp(tp/1000).strftime('%H:%M:%S %d-%m-%Y'));
                writer.writerow([datetime.datetime.fromtimestamp(d["data"]/1000).strftime('%H:%M:%S %d-%m-%Y'),ath['data'],p.group,char_bank,cs['source_length'],cs['final_op'],cs['final_diff'],text])

            #print(datetime.datetime.utcfromtimestamp(d["data"]/1000).strftime('%Y-%m-%d %H:%M:%S'),',',pad.group,',',cs["bank"],',',cs["source_length"],',',cs["final_diff"],',',cs["final_op"],',',rev["data"],',',ath["data"])
    return response

def duplicate(request,session_id):
    print('duplicate called')
    sessions = Session.objects.all().filter(id=session_id)
    if sessions.count() ==0:
        messages.error(request,'Invalid project id')
        return redirect('project_home')
    session = sessions.first()
    if  (session.owner != request.user) and (not request.current_user.is_staff):
        messages.error(request,'You do not have edit rights for this session')
        return redirect('project_home')
    form1 = {}
    form2 = {}
    form3 = {}
    form4 = {}

    # form1 data
    form1['name'] = session.name
    form1['groups'] = session.groups
    form1['language'] = session.language
    form1['duration_days'] = session.duration.days
    form1['duration_hours'] = session.duration.seconds // 3600
    form1['duration_minutes'] =  ( session.duration.seconds // 60) % 60
    form1['new'] = -1

    # form2 data
    form2['learning_problem'] = session.learning_problem

    # form3 data
    form3['useEtherpad'] = session.useEtherpad
    form3['useAVchat'] = session.useAVchat
    form3['record_audio'] = session.record_audio
    form3['record_audio_video'] = session.record_audio_video

    #form4 data
    form4['allow_access'] = session.access_allowed
    initial = {'activity_info':form1,'task':form2,'config':form3,'overview':form4}
    print('Initial:',initial)
    return CompleteForm.as_view(CREATE_FORMS,initial_dict=initial)(request)



def edit(request,session_id):
    print('edit called')
    sessions = Session.objects.all().filter(id=session_id)
    if sessions.count() ==0:
        messages.error(request,'Invalid project id')
        return redirect('project_home')
    session = sessions.first()
    if  (session.owner != request.user) and (not request.user.is_staff):
        messages.error(request,'You do not have edit rights for this session')
        return redirect('project_home')
    form1 = {}
    form2 = {}
    form3 = {}
    form4 = {}

    # form1 data
    form1['edit_session'] = str(session.id)
    form1['s_id'] = session.id
    form1['name'] = session.name
    form1['groups'] = session.groups
    form1['language'] = session.language
    form1['duration_days'] = session.duration.days
    form1['duration_hours'] = session.duration.seconds // 3600
    form1['duration_minutes'] =  ( session.duration.seconds // 60) % 60
    form1['new'] = int(session.id)



    # form2 data
    form2['learning_problem'] = session.learning_problem

    # form3 data
    form3['useEtherpad'] = session.useEtherpad
    form3['useAVchat'] = session.useAVchat
    form3['record_audio'] = session.record_audio
    form3['record_audio_video'] = session.record_audio_video

    #form4 data
    form4['allow_access'] = session.access_allowed
    initial = {'activity_info':form1,'task':form2,'config':form3,'overview':form4}
    print('Initial:',initial)
    return CompleteForm.as_view(CREATE_FORMS,initial_dict=initial)(request)



def sessionFilter(request,filter):

    if filter not in ['all','archived']:
        messages.error(request,'Incorrect filter applied.')
        return redirect('project_home')
    else:
        projects = []
        if filter == 'archived':
            sessions = Session.objects.all().filter(owner=request.user).filter(status=False)
            if sessions.count() == 0:
                messages.warning(request,'There are no archived project')
            else:
                msg = 'Archived sessions are fetched successfully!'
                messages.success(request,msg)
            return render(request, "dashboard.html",{'sessions':sessions,'filter':True})

        else:
            messages.success(request,'All sessions are fetched successfully')
            return redirect('project_home')




def usabilityForm(request):
    if request.method == "POST":
        q1 = int(request.POST['survey-q1'])
        q2 = int(request.POST['survey-q2'])
        q3 = int(request.POST['survey-q3'])
        q4 = int(request.POST['survey-q4'])
        q5 = int(request.POST['survey-q5'])
        q6 = int(request.POST['survey-q6'])
        q7 = int(request.POST['survey-q7'])
        q8 = int(request.POST['survey-q8'])
        q9 = int(request.POST['survey-q9'])
        q10 = int(request.POST['survey-q10'])
        q11 = int(request.POST['survey-q11'])
        q12 = int(request.POST['survey-q12'])
        q13 = int(request.POST['survey-q13'])
        q14 = int(request.POST['survey-q14'])
        q15 = int(request.POST['survey-q15'])
        q16 = int(request.POST['survey-q16'])
        q17 = int(request.POST['survey-q17'])

        submission = Usability.objects.create(q1=q1,q2=q2,q3=q3,q4=q4,q5=q5,q6=q6,q7=q7,q8=q8,q9=q9,q10=q10,q11=q11,q12=q12,q13=q13,q14=q14,q15=q15,q16=q16,q17=q17,submitted_user=request.user)
        messages.success(request, 'Your responses are saved. Thank you for your submission. It will help us to improve the tool further.')
        return redirect('project_home')
        #return getAnonyForm(request)
    else:
        return render(request,"survey_form_usability.html",{'title':'Questionnaire'})



def engagementForm(request,session,group):
    if request.method == "POST":
        q1 = int(request.POST['survey-q1'])
        q2 = int(request.POST['survey-q2'])
        q3 = int(request.POST['survey-q3'])
        q4 = int(request.POST['survey-q4'])
        q5 = int(request.POST['survey-q5'])
        q6 = int(request.POST['survey-q6'])
        q7 = int(request.POST['survey-q7'])
        q8 = int(request.POST['survey-q8'])
        q9 = int(request.POST['survey-q9'])
        q10 = int(request.POST['survey-q10'])
        q11 = int(request.POST['survey-q11'])
        q12 = int(request.POST['survey-q12'])
        q13 = int(request.POST['survey-q13'])
        q14 = int(request.POST['survey-q14'])
        q15 = int(request.POST['survey-q15'])
        session_obj  = Session.objects.get(id=session)
        submission = EngagementQ.objects.create(session=session_obj,group=group,submitted_user=request.user,q1=q1,q2=q2,q3=q3,q4=q4,q5=q5,q6=q6,q7=q7,q8=q8,q9=q9,q10=q10,q11=q11,q12=q12,q13=q13,q14=q14,q15=q15)
        messages.success(request, _('Your responses are saved. Thank you for the submission.'))
        if 'joined' in request.session.keys():
            del request.session['joined']
        return redirect('student_entry')
    else:
        return render(request,"survey_form_updated_engagement.html",{'title':'Self-reporetd questionnaire on collaborative learning'})




def surveyForm(request,session,group):
    if request.method == "POST":
        q1 = int(request.POST['survey-q1'])
        q2 = int(request.POST['survey-q2'])
        q3 = int(request.POST['survey-q3'])
        q4 = int(request.POST['survey-q4'])
        q5 = int(request.POST['survey-q5'])
        q6 = int(request.POST['survey-q6'])
        q7 = int(request.POST['survey-q7'])
        q8 = int(request.POST['survey-q8'])
        q9 = int(request.POST['survey-q9'])
        q10 = int(request.POST['survey-q10'])
        q11 = int(request.POST['survey-q11'])
        q12 = int(request.POST['survey-q12'])
        q13 = int(request.POST['survey-q13'])
        q14 = int(request.POST['survey-q14'])
        q15 = int(request.POST['survey-q15'])
        q16 = int(request.POST['survey-q16'])
        q17 = int(request.POST['survey-q17'])
        q18 = int(request.POST['survey-q18'])
        q19 = int(request.POST['survey-q19'])
        q20 = int(request.POST['survey-q20'])
        q21 = int(request.POST['survey-q21'])
        q22 = int(request.POST['survey-q22'])
        q23 = int(request.POST['survey-q23'])
        q24 = int(request.POST['survey-q24'])
        q25 = int(request.POST['survey-q25'])
        q26 = int(request.POST['survey-q26'])
        q27 = int(request.POST['survey-q27'])
        q28 = int(request.POST['survey-q28'])
        q29 = int(request.POST['survey-q29'])
        q30 = int(request.POST['survey-q30'])
        q31 = int(request.POST['survey-q31'])
        q32 = int(request.POST['survey-q32'])
        q33 = int(request.POST['survey-q33'])
        q34 = int(request.POST['survey-q34'])
        q35 = int(request.POST['survey-q35'])
        q36 = int(request.POST['survey-q36'])
        q37 = int(request.POST['survey-q37'])

        session_obj  = Session.objects.get(id=session)

        submission = CollaborationQ.objects.create(session=session_obj,group=group,submitted_user=request.user,q1=q1,q2=q2,q3=q3,q4=q4,q5=q5,q6=q6,q7=q7,q8=q8,q9=q9,q10=q10,q11=q11,q12=q12,q13=q13,q14=q14,q15=q15,q16=q16,q17=q17,q18=q18,q19=q19,q20=q20,q21=q21,q22=q22,q23=q23,q24=q24,q25=q25,q26=q26,q27=q27,q28=q28,q29=q29,q30=q30,q31=q31,q32=q32,q33=q33,q34=q34,q35=q35,q36=q36,q37=q37)
        messages.success(request, 'Your responses are saved. Thank you for the submission.')
        if 'joined' in request.session.keys():
            del request.session['joined']
        return redirect('student_entry')
    else:
        return render(request,"survey_form_updated.html",{'title':'Self-reporetd questionnaire on collaborative learning'})



from urllib.parse import quote


# Create your views here.
def overview(request):

    if isTeacher(request) or isAdmin(request):
        sessions = Session.objects.all().filter(owner=request.user).filter(status=True)
        groups_pin = {}
        for session in sessions:
            groups_pin[session.id] = GroupPin.objects.all().filter(session=session)
        return render(request, "dashboard.html",{'sessions':sessions,'groups_pin':groups_pin})
    else:
        messages.warning(request,'You do not have teacher privilege to access this page.')
        return redirect('student_entry')




# Students entry form
def enterForm(request):
    if request.method == "POST":
        s_pin = request.POST['pin']
        print('Entered pin:',s_pin)
        group_pin = GroupPin.objects.all().filter(pin=s_pin)
        if group_pin.count() == 0:
            messages.error(request,'Entered pin is invalid.')
            return render(request,"session_student_entry_v2.html",{})
        else:
            session_obj = group_pin[0].session
            print('Session:',session_obj)
            user = request.user
            res = call('createAuthorIfNotExistsFor',{'authorMapper':user.id,'name':user.first_name})
            authorid = res['data']['authorID']

            group = grouppin = None

            if session_obj.useEtherpad:
                group = SessionGroupMap.objects.get(session=session_obj)
                groupid = group.eth_groupid
                NextDay_Date = datetime.datetime.today() + datetime.timedelta(days=1)
                res2 = call('createSession',{'authorID':authorid,'groupID':groupid,'validUntil':NextDay_Date.timestamp()})
                request.session['ethsid'] = res2['data']['sessionID']

            # Creating a session variable storing joined session and group
            payload = {
              "session": session_obj.id,
              "group": group_pin[0].group
            }
            token = jwt.encode(payload,settings.JW_SEC,algorithm="HS256")
            token = token.decode('utf-8')
            request.session['joined'] = token

            request.user.backend = 'django.contrib.auth.backends.ModelBackend'
            return redirect('student_consent')
    else:
        user_role = Role.objects.all().filter(user=request.user)
        if user_role.count() > 0:
            if  user_role[0].role == 'teacher' and not request.user.is_staff:
                return redirect('project_home')
        if 'joined' in request.session.keys():
            print('Jioned session exists:',request.session['joined'])

            token = jwt.decode(request.session['joined'], settings.JW_SEC, algorithms=["HS256"])

            print('Fetched token:',token)

            if Session.objects.filter(id=token['session']).count() == 0:
                messages.error(request,'The session is corrupted. Please enter your access pin again.')
                del request.session['joined']
                return render(request,"session_student_entry_v2.html",{})
            session_obj = Session.objects.get(id=token["session"])
            groups = range(session_obj.groups)
            return redirect('student_consent')
        else:
            return render(request,"session_student_entry_v2.html",{})

def consentView(request):
    form = consentForm()
    user_role = Role.objects.all().filter(user=request.user)
    if user_role[0].role == 'teacher' and not request.user.is_staff():
        return redirect('project_home')
    if 'joined' in request.session.keys():
        token = jwt.decode(request.session['joined'], settings.JW_SEC, algorithms=["HS256"])
        if Session.objects.filter(id=token['session']).count() == 0:
            messages.error(request,'The cookie is corrupted.')
            del request.session['joined']
            return render(request,"session_student_entry_v2.html",{})
        else:
            session = Session.objects.get(id=token["session"])
            pad = Pad.objects.filter(session=session).first()
            if request.method == 'POST':
                permission = request.POST['permission']
                Consent.objects.create(session = session, user = request.user)
                recordLog(session,request.user,'entered','learning_space')
                return getPad(request,session,token['group'])
                #return render(request,'student_pad.html',{'session':session,'groups':session.groups,'form':form,'lang':session.language,'etherpad_url':settings.ETHERPAD_URL,'padname':pad.eth_padid,'sessionid':request.session['ethsid'],'protocol':settings.PROTOCOL})
            else:
                if Consent.objects.filter(session=session).filter(user=request.user).count() > 0:
                    if session.useEtherpad and 'ethsid' not in request.session:
                        del request.session['joined']
                        return render(request,"session_student_entry_v2.html",{})
                    recordLog(session,request.user,'entered','learning_space')
                    return getPad(request,session,token['group'])
                    #return render(request,'student_pad.html',{'session':session,'groups':session.groups,'lang':session.language,'etherpad_url':settings.ETHERPAD_URL,'padname':pad.eth_padid})
                else:
                    return render(request,'consent.html',{'session':session,'groups':session.groups,'form':form,'lang':session.language,'user':request.user})
    else:
        message.error(request,'Please enter your access pin.')
        return redirect('session_student_entry_v2.html')

@api_view(['GET'])
@permission_classes((permissions.AllowAny,))
def getRevCount(request,padid):
    params = {'padID':padid}
    rev_count = call('getRevisionsCount',params)
    return Response({'revisions':rev_count['data']['revisions']})


@api_view(['GET'])
@permission_classes((permissions.AllowAny,))
def getTime(request):
    print('getTime called')
    if 't' in request.GET:
        t = request.query_params.get('t')
        t = int(t)

        print('Client:',t)
        cs = datetime.datetime.now()
        print('Server:',cs)
        current_time = int(cs.timestamp())*1000 # convert into millisecons
        current_time += cs.microsecond/1000 # getting millisecons
        print('Server milli:',current_time)
        delta = int(current_time) - t/1000
        print('delta:',delta)
        print('Returned:',str(delta),':',str(t))
        res = str(delta),':',str(t)
        return Response({'offset':int(delta),'time':t})


@api_view(['GET'])
@permission_classes((permissions.AllowAny,))
def getWordCloud(request,session_id,group_id):
    stopwords = set(STOPWORDS)
    session = Session.objects.get(id=session_id)
    speeches = Speech.objects.all().filter(session = session, group = group_id).values_list('TextField',flat=True)
    speeches = " ".join(speech for speech in speeches)
    print(speeches)
    if len(speeches) == 0:
        data = {'data':'empty'};
    else:
        wc = WordCloud(background_color = 'white', max_words=2000, stopwords = stopwords)

        cloud = wc.generate(speeches)
        print('Word cloud generated')
        plt.imshow(wc,interpolation ='bilinear')
        plt.axis('off')

        image = io.BytesIO()
        plt.savefig(image,format="png")
        image.seek(0)
        string = base64.b64encode(image.read())
        #image_64 =  urllib.parse.quote(string)
    data = {'data':str(string.decode())}
    print('Returning:',data)
    return Response(data)

# for building edge list with weight
def edgeExist(edge_list,edge):
    for e in edge_list:
        if e[0] == edge[0] and e[1] == edge[1]:
            return True
        if e[0] == edge[1] and e[1] == edge[0]:
            return True
    return False

def updateWeight(edge_list, edge):
    updated = list()
    for i,e in enumerate(edge_list):
        if edgeExist(updated,e):
            w = edge_list[i][2] + .001
            updated.append((e[0],e[1],w))
        else:
            updated.append(e)
    return updated

# function to get elements for cytoscape.js to draw network
def generateElements(user_sequence,speaking_data):
    total_speaking = sum(speaking_data)
    #### create edge list_files
    edge_list = list()
    # Create two variable node1 and node2 and set them to zero.
    node1=node2=0
    # Iterate over resultant users sequences
    for i in range(len(user_sequence)):
        # For the first element
        if node1==0:
            # set node1 to the first element
            node1=user_sequence[i]
        # For rest of the elements
        else:
            # Set the current element to node2
            node2=user_sequence[i]
            if node1 != node2:
                # Append the edge node1, node2 to the edge list
                if edgeExist(edge_list,(node1,node2)):
                    edge_list = updateWeight(edge_list,(node1,node2))
                else:
                    edge_list.append((node1,node2,5))
            node1=node2
    ele_nodes=[]
    total_edges = len(edge_list)
    for n in set(user_sequence):
        user_obj = User.objects.get(pk = n)
        #speak_ratio = 200*sp_time[n]/total_sp
        node_width = 20 + speaking_data[n]/total_speaking
        t = {'id':n,'name':user_obj.first_name,'size':node_width }
        ele_nodes.append(t)
    ele_edges = []
    for e in edge_list:
        t = {'source':e[0],'to':e[1],'weight':e[2]}
        ele_edges.append(t)
    elements = {'nodes':ele_nodes,'edges':ele_edges}
    return elements


@api_view(['GET'])
@permission_classes((permissions.AllowAny,))
def getHelpQueries(request,session_id):
    s = Session.objects.get(id=session_id)
    groups = s.groups
    groups_queries = []
    for group in range(groups):
        group_query = {}
        group = group + 1
        helps = Help.objects.all().filter(session=session_id,group=group,seen=False)

        group_query['group'] = group
        group_query['help'] = False
        if helps.count() > 0:
            group_query['help'] = True
        groups_queries.append(group_query)
    return Response({'queries':groups_queries})



@api_view(['GET'])
@permission_classes((permissions.AllowAny,))
def getSpeakingStats(request,session_id):
    s = Session.objects.get(id=session_id)
    groups = s.groups
    groups_speaking = []
    for group in range(groups):
        group = group + 1
        vads = VAD.objects.all().filter(session=session_id)

        group_speaking = {}
        group_speaking['group'] = group

        tmp_users = vads.filter(group = group).values('user').distinct()
        users = [user['user'] for user in tmp_users]
        user_sequence = vads.filter(group = group).values_list('user',flat=True)
        data = []
        speaking_data = {}

        for user in users:
            user_vads = vads.filter(group = group).filter(user = user).aggregate(Sum('activity'))
            speak_data = {}
            user_obj = User.objects.get(pk = user)
            speak_data['id'] = user
            speak_data['name'] = user_obj.first_name if user_obj.first_name else user_obj.username
            speak_data['speaking'] = user_vads['activity__sum']
            speaking_data[user] = user_vads['activity__sum'] * .001
            data.append(speak_data)

        group_speaking['data'] = data
        group_speaking['graph'] = generateElements(user_sequence,speaking_data)
        groups_speaking.append(group_speaking)

    return Response({'speaking_data':groups_speaking})




@api_view(['GET'])
@permission_classes((permissions.AllowAny,))
def getGroupPadStats(request,padid):
    params = {'padID':padid}
    rev_count = call('getRevisionsCount',params)
    # get user wise Info
    print(call('padUsersCount',params))
    print(call('listAuthorsOfPad',params))

    author_list = call('listAuthorsOfPad',params)['data']['authorIDs']

    addition = {}
    deletion = {}

    author_names = {}

    for author in author_list:
        print('Author',author)
        addition[author] = 0
        deletion[author] = 0

        author_names[author] = call('getAuthorName',{'authorID':author})['data']
        #author_obj = AuthorMap.objects.filter(authorid=author)


        #print('--------------',author_obj)
        #author_names[author] = author_obj[0].user.username

    for r in range(rev_count['data']['revisions']):
        params = {'padID':padid,'rev':r+1}
        rev = call('getRevisionChangeset',params)
        ath = call('getRevisionAuthor',params)

        cs = changeset_parse(rev['data'])

        if (cs['final_op'] == '>'):
            addition[ath['data']] += cs['final_diff']
        if (cs['final_op'] == '<'):
            deletion[ath['data']] += cs['final_diff']

    call_response = {}
    author_count = len(author_names.keys())

    for i,v in enumerate(author_names.keys()):
        call_response[i] = {
            'authorid': v,
            'name':author_names[v],
            'addition':addition[v],
            'deletion':deletion[v],
        }

    #######################
    return Response(call_response)

def getGroupText(request,session_id,group_id):
    session = Session.objects.get(id=session_id)
    payload = {}
    token = ''

    if (Help.objects.filter(session=session_id,group=group_id).count() > 0):
        help_objs = Help.objects.filter(session=session_id,group=group_id,seen=False)
        for help_obj in help_objs:
            help_obj.seen = True
        Help.objects.bulk_update(help_objs,['seen'])

    room_name = 'S' + str(session.id) + 'G' + str(group_id)
    context_data = {'group':group_id,'room':room_name,'session_obj':session,'session':session,'etherpad_url':settings.ETHERPAD_URL,'protocol':settings.PROTOCOL}
    if session.useAVchat:
        print('Adding token for Jitsi')
        payload = {
          "context": {
            "user": {
              "name": request.user.first_name,
              "email": request.user.email
            }
          },
          "aud": settings.JW_APP,
          "iss": settings.JW_APP,
          "sub": "www.cojitsi.website",
          "moderator": False,
          "room": room_name
        }
        token = jwt.encode(payload,settings.JW_SEC,algorithm="HS256")
        token = token.decode('utf-8')
        context_data['token'] = token

    if session.useEtherpad:
        pad = Pad.objects.all().filter(session=session).filter(group=group_id)
        eth_group = SessionGroupMap.objects.all().filter(session=session)
        padid = pad[0].eth_padid
        res = call('getText',{'padID':padid})
        read = call('getReadOnlyID',{'padID':padid})
        context_data['padname'] = read['data']['readOnlyID']
        context_data['session_id'] = session_id
        context_data['session'] = session
        print('Get readonly',read)
        valid = int(datetime.datetime.today().timestamp() + 24 * 60 * 60)
        print(valid,' ',type(valid))
        auth_id = call('createAuthorIfNotExistsFor',{'authorMapper':request.user.id})
        print('Create author',auth_id)
        accessSession = call('createSession',{'groupID':eth_group[0].eth_groupid,'authorID':auth_id['data']['authorID'],'validUntil':valid})
        print('Access session',accessSession)
        context_data['sessionid'] = accessSession['data']['sessionID']

    return render(request,'teacher_pad.html',context_data)





def downloadLog(request,session_id):
    session = Session.objects.all().filter(id=session_id)
    if session.count() == 0:
        messages.error(request,'Specified session id is invalid')
        return redirect('project_home')
    else:
        session = Session.objects.get(id=session_id)
        # Preparing csv data File#####
        fname = session.name + '.csv'

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment;filename="' + fname +'"'

        writer = csv.writer(response)
        writer.writerow(['timestamp','author','group','char_bank','source_length','operation','difference','text'])

        ##############################


        pad = Pad.objects.all().filter(session=session)


        for p in pad:

            padid =  p.eth_padid
            params = {'padID':padid}
            rev_count = call('getRevisionsCount',params)

            for r in range(rev_count['data']['revisions']):
                params = {'padID':padid,'rev':r+1}
                rev = call('getRevisionChangeset',params)
                ath = call('getRevisionAuthor',params)

                d = call('getRevisionDate',params)
                t = call('getText',params)

                cs = changeset_parse(rev['data'])
                tp = int(d['data'])
                char_bank = cs['bank']

                text = t['data']['text']['text']
                char_bank = "<br/>".join(char_bank.split("\n"))
                text = "<br/>".join(text.split("\n"))

                #print(datetime.datetime.fromtimestamp(tp/1000).strftime('%H:%M:%S %d-%m-%Y'))
                #print('   ',datetime.datetime.fromtimestamp(tp/1000).strftime('%H:%M:%S %d-%m-%Y'));
                writer.writerow([datetime.datetime.fromtimestamp(d["data"]/1000).strftime('%H:%M:%S %d-%m-%Y'),ath['data'],p.group,char_bank,cs['source_length'],cs['final_op'],cs['final_diff'],text])

            #print(datetime.datetime.utcfromtimestamp(d["data"]/1000).strftime('%Y-%m-%d %H:%M:%S'),',',pad.group,',',cs["bank"],',',cs["source_length"],',',cs["final_diff"],',',cs["final_op"],',',rev["data"],',',ath["data"])
    return response


def uploadAudio(request):
    print('Upload Audio invoked')
    if request.method == 'POST':
        form = AudioflForm(request.POST,request.FILES)
        print(form)
        if form.is_valid():
            print('Form is valid')
            strDate = form.cleaned_data.get("strDate")
            print(strDate)
            strDate = (int)(float(strDate)/1000)

            dt = datetime.datetime.fromtimestamp(strDate)
            print('Datetime:',dt)

            newform = form.save(commit=False)
            newform.started_at = dt
            djfile = File(request.FILES['data_blob'])
            newform.fl.save(request.FILES['data_blob'].name,djfile)

            strDate = (int)(float(strDate)/1000)

            dt = datetime.datetime.fromtimestamp(strDate)
            print('Datetime:',dt)
            newform.started_at = dt
            newform.save()
            return HttpResponse('Done')
        else:
            print('Form not valid')
            return HttpResponse('Form not valid')
    else:
        return HttpResponse('Not done')



def uploadVad(request):
    if request.method == 'POST':
        form = VADForm(request.POST,request.FILES)
        print(form)
        if form.is_valid():
            print('Form is valid')
            session = form.cleaned_data.get("session")
            user = form.cleaned_data.get("user")
            group = form.cleaned_data.get("group")
            strDate = form.cleaned_data.get("strDate")
            milli = form.cleaned_data.get("milli")
            activity = form.cleaned_data.get("activity")
            strDate = (int)(float(strDate)/1000)
            dt = datetime.datetime.fromtimestamp(strDate)
            print('Converted datetime:',dt)
            vad_object = VAD.objects.create(session=session,user=user,group=group,timestamp=dt,activity=activity)
            return HttpResponse('Done')
        else:
            print('Form not valid')
            return HttpResponse('Form not valid')
    else:

        return HttpResponse('Not done')

def uploadSpeech(request):
    if request.method == 'POST':
        form = SpeechForm(request.POST,request.FILES)
        print(form)
        if form.is_valid():
            print('Form is valid')
            session = form.cleaned_data.get("session")
            user = form.cleaned_data.get("user")
            group = form.cleaned_data.get("group")
            strDate = form.cleaned_data.get("strDate")
            speech = form.cleaned_data.get("TextField")

            strDate = (int)(float(strDate)/1000)
            dt = datetime.datetime.fromtimestamp(strDate)

            speech_object = Speech.objects.create(session=session,user=user,group=group,timestamp=dt,TextField=speech)

            return HttpResponse('Done')
        else:
            print('Form not valid')
            return HttpResponse('Form not valid')
    else:

        return HttpResponse('Not done')

def uploadHelp(request):
    if request.method == 'POST':
        print('Help Form recieved')
        form = HelpForm(request.POST)
        if form.is_valid():
            print(form)
            print('Form is valid')
            session = form.cleaned_data.get("session")
            user = form.cleaned_data.get("user")
            group = form.cleaned_data.get("group")
            speech_object = Help.objects.create(session=session,user=user,group=group,seen=False)
            return HttpResponse('Done')
        else:
            print('Form not valid')
            return HttpResponse('Form not valid')
    else:
        print('Not a post method')
        return HttpResponse('Not done')


def LeaveSession(request):
    if 'joined' in request.session.keys():
        del request.session['joined']

    return redirect('student_entry')

def getPad(request,session,group_id):
    eth_session = pad = padname = None

    context_data = {}
    form = AudioflForm()
    payload = {}
    token = ''
    room_name = 'S' + str(session.id) + 'G' + str(group_id)
    context_data = {'group':group_id,'room':room_name,'session_obj':session,'session':session,'form':form,'etherpad_url':settings.ETHERPAD_URL,'protocol':settings.PROTOCOL}

    if session.useAVchat:
        print('Adding token for Jitsi')
        payload = {
          "context": {
            "user": {
              "name": request.user.first_name,
              "email": request.user.email
            }
          },
          "aud": settings.JW_APP,
          "iss": settings.JW_APP,
          "sub": "www.cojitsi.website",
          "moderator": False,
          "room": room_name
        }
        token = jwt.encode(payload,settings.JW_SEC,algorithm="HS256")
        token = token.decode('utf-8')
        context_data['token'] = token

    if session.useEtherpad:
        eth_session = request.session['ethsid']
        pad = Pad.objects.get(session=session,group=group_id)
        padname = pad.eth_padid.split('$')
        context_data['padname'] = pad.eth_padid
        context_data['sessionid'] = eth_session

    return render(request,'student_pad.html',context_data)


def activateSession(request,session_id):
    session = Session.objects.all().filter(id=session_id)
    if session.count() == 0:
        messages.error(request,'Specified session id is invalid')
        return redirect('project_home')
    else:
        session = Session.objects.get(id=session_id)
        session.status = True
        session.save()
        messages.success(request,'Session is unarchived successfully.')
        return redirect('project_home')

def deactivateSession(request,session_id):
    session = Session.objects.all().filter(id=session_id)
    if session.count() == 0:
        messages.error(request,'Specified session id is invalid')
        return redirect('project_home')
    else:
        session = Session.objects.get(id=session_id)
        session.status = False
        session.save()
        messages.success(request,'Session is archived successfully.')
        return redirect('project_home')


def getSession(request,session_id):
    session = Session.objects.all().filter(id=session_id)
    if session.count() == 0:
        messages.error(request,'Specified session id is invalid')
        return redirect('project_home')
    else:
        session = Session.objects.get(id=session_id)
        context_data = {'session':session,'no_group':list(range(session.groups)),'protocol':settings.PROTOCOL}
        if session.useEtherpad:
            session_group = SessionGroupMap.objects.get(session=session)
            eth_group = session_group.eth_groupid
            context_data['eth_group'] = eth_group
            return render(request,'session_main.html',context_data)
        else:
            return render(request,'session_main_only_av_chat.html',context_data)


class CompleteForm(SessionWizardView):
    type_of_study = -1

    def updatePin(self,s,old_groups,new_groups):
        group_diff = new_groups - old_groups
        if (group_diff > 0):
            for g in range(group_diff):
                g =  g +  old_groups + 1
                while True:
                    u_pin = uuid.uuid4().hex[:6].upper()
                    objs = GroupPin.objects.filter(pin = u_pin)
                    if objs.count() == 0:
                        break
                sg = GroupPin.objects.create(session=s,pin=u_pin,group=g)
        else:
            group_diff = abs(group_diff)
            for g in range(group_diff):
                del_group = g + new_groups + 1
                GroupPin.objects.filter(session=s,group=del_group).delete()
        print('Updated pins')



    def updateEtherpad(self,s,old_groups,new_groups,old_use,new_use):
        """
        function to update the groups and pads in Etherpad.
        s : session object
        old_groups: number of groups before change
        new_groups: number of groups after change
        old_use: setting of useEtherpad before change
        new_use: setting of useEtherpad after change
        """
        group_diff = new_groups - old_groups
        if (not old_use) and (new_use):
            self.prepareEtherpad(s,new_groups)
        if (old_use) and (not new_use):
            self.deleteEtherpad(s)
        if (old_use and new_use):
            if (group_diff > 0):
                sgm = SessionGroupMap.objects.filter(session=s)
                print('group-diff',group_diff)
                for g in range(group_diff):
                    g =  g +  old_groups + 1
                    print('Creating pad for group-',g)
                    pad_name = 'session_'+str(s.id)+'_'+'group'+'_'+str(g)
                    print(' Creating pad:',pad_name,' with Groupid:',sgm[0].eth_groupid)
                    res = call('createGroupPad',{'groupID':sgm[0].eth_groupid,'padName':pad_name},request=self.request)
                    print(res)
                    if res["code"] == 0:
                        Pad.objects.create(session=s,eth_padid=res['data']['padID'],group=g)
                        #@todo: add code to handle etherpad exception is call gets failed
                    else:
                        messages.error(self.request,'Error occurred while creating pads. Check Etherpad server settings.')
                        return redirect('project_home')
            else:
                group_diff = abs(group_diff)
                for g in range(group_diff):
                    del_group = g + new_groups + 1
                    pad_name = str(sgm[0].eth_groupid) + '$' + 'session_'+str(s.id)+'_'+'group'+'_'+str(del_group)
                    res = call('deletePad',{'padID':pad_name})
                    Pad.objects.filter(group=del_group).delete()
        messages.success(self.request,'Session is successfully updated.')

    @transaction.atomic
    def deleteEtherpad(self,s):
        print('Deleting pads')
        sgm_objects = SessionGroupMap.objects.filter(session=s)
        if sgm_objects.count() > 0:
            sgm_object = sgm_objects.first()
            x = call('deleteGroup',{'groupID':sgm_object.eth_groupid},request=self.request)
            Pad.objects.filter(session=s).delete()
            SessionGroupMap.objects.filter(session=s).delete()
            print('Etherpad group in deleted')
    @transaction.atomic
    def prepareEtherpad(self,s,groups):
        x = call('createGroup',request=self.request)
        if ( x["code"] == 0):
            groupid = x["data"]["groupID"]
            print('Group created successfully:',groupid)
            sgm = SessionGroupMap.objects.create(session=s,eth_groupid=x["data"]["groupID"])
            for g in range(groups):
                g =  g + 1
                pad_name = 'session_'+str(s.id)+'_'+'group'+'_'+str(g)
                print(' Creating pad:',pad_name,' with Groupid:',groupid)
                res = call('createGroupPad',{'groupID':groupid,'padName':pad_name},request=self.request)
                print(res)
                if  res["code"] == 0:
                    Pad.objects.create(session=s,eth_padid=res['data']['padID'],group=g)
                    print('Pad created:',g)
                else:
                    messages.error(self.request,'Error occurred while creating pads. Check your Etherpad server settings.')
                    return redirect('project_home')

    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]

    def get_form(self, step=None, data=None, files=None):
        form = super().get_form(step, data, files)

        if step is None:
            step = self.steps.current
        return form

    def get_context_data(self, form, **kwargs):
        context = super(CompleteForm, self).get_context_data(form=form, **kwargs)
        data = self.get_all_cleaned_data()
        if self.steps.current == 'activity_info':
            print('Step-1')
            print(data)
        if self.steps.current == 'task':
            print('Step-2')
            print(data)

        if self.steps.current =='overview':
            data = self.get_all_cleaned_data()
            new = data['new']
            context.update({'all_data': self.get_all_cleaned_data()})
        return context

    @transaction.atomic
    def done(self, form_list, **kwargs):
        print('done called')
        all_data = self.get_all_cleaned_data()
        current_user = self.request.user
        groups=all_data['groups']

        if all_data['new'] == -1:
            print('New project')
            groups_pin = {}
            duration = timedelta(days=all_data['duration_days'],hours=all_data['duration_hours'],minutes=all_data['duration_minutes'])

            # code to add target=_blank in every anchor tag in learning problem
            learning_problem = BeautifulSoup(all_data['learning_problem'],"html.parser")
            for a in learning_problem.find_all('a'):
              a['target'] = '_blank'

            s = Session.objects.create(owner=current_user,name=all_data['name'],groups=all_data['groups'],learning_problem=str(learning_problem),language=all_data['language'],access_allowed=all_data['allow_access'],status=True,assessment_score=0,useEtherpad=all_data['useEtherpad'],useAVchat=all_data['useAVchat'],record_audio=all_data['record_audio'],record_audio_video=all_data['record_audio_video'],data_recording_session=False,duration=duration)

            for grp in range(groups):
                while True:
                    u_pin = uuid.uuid4().hex[:6].upper()
                    objs = GroupPin.objects.filter(pin = u_pin)
                    if objs.count() == 0:
                        break
                sg = GroupPin.objects.create(session=s,pin=u_pin,group=grp+1)

            if all_data['useEtherpad']:
                try:
                    self.prepareEtherpad(s,all_data['groups'])
                except e:
                    messages.error(self.request,'Error occurred while creating session. Check your Etherpad server settings.')
                return redirect('project_home')
            messages.success(self.request, 'Session is created successfully !')
        else:
            print('Edit handler called')
            session_id = int(all_data['new'])
            session = Session.objects.get(id=session_id)
            org_groups = session.groups # existing group number
            org_useEtherpad = session.useEtherpad
            updated_groups = all_data['groups']
            updated_useEtherpad = all_data['useEtherpad']

            duration = timedelta(hours=all_data['duration_hours'],minutes=all_data['duration_minutes'])
            session.owner=current_user
            session.name=all_data['name']
            session.groups=all_data['groups']
            learning_problem = BeautifulSoup(all_data['learning_problem'],"html.parser")
            print('Before:',learning_problem)
            for a in learning_problem.find_all('a'):
                if not a.has_attr('target'):
                    a['target'] = '_blank'
            print('After:',learning_problem)

            session.learning_problem=all_data['learning_problem']
            session.language=all_data['language']
            session.access_allowed=all_data['allow_access']
            session.status=True
            session.assessment_score=0
            session.useEtherpad=all_data['useEtherpad']
            session.useAVchat=all_data['useAVchat']
            session.record_audio=all_data['record_audio']
            session.record_audio_video=all_data['record_audio_video']
            session.data_recording_session=False
            session.duration=duration
            self.updateEtherpad(session,org_groups,updated_groups,org_useEtherpad,updated_useEtherpad)
            self.updatePin(session,org_groups,updated_groups)
            session.save()

        return redirect('project_home')
