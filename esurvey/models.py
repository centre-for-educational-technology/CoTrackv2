from django.db import models
from django.contrib.auth.models import User
import uuid
from django.contrib import admin
import datetime
import os
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.conf import settings
import requests
from django.contrib import messages
from ckeditor_uploader.fields import RichTextUploadingField
from django.shortcuts import redirect


def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return os.path.join(
      "session_%d" % instance.session.id,"group_%d" % instance.group, "user_%s" % instance.user.id, filename)

# Function to make calls to Etherpad API
def call(function,arguments=None,request=None):
    try:
        url = settings.ETHERPAD_URL + '/api/1.2.12/' +function+'?apikey='+settings.ETHERPAD_KEY
        response = requests.post(url,arguments)
        x = response.json()
        print('Returned:x',x)
        return x
    except:
        return redirect('project_home')

# Model for storing learning activities information
class Session(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)   #owner of the session
    name = models.CharField(max_length=100)                     #session title
    groups = models.IntegerField()                              #number of groups
    learning_problem = RichTextUploadingField()
    language = models.CharField(max_length=2)                #learning problem
    created_at = models.DateTimeField(auto_now_add=True)        #created at date and time
    duration = models.DurationField()                           #duration of the activity
    access_allowed = models.BooleanField(default=True)          #whether the access is open to the students or not
    status = models.BooleanField(default=False)                 #status of session, used for archiving the session
    assessment_score = models.IntegerField()                    #to store the teacher's assessment of group's work
    useEtherpad = models.BooleanField(default=False)            #whether to use etherpad or not
    useAVchat = models.BooleanField(default=False)              #whether to use audio video chat or not
    record_audio = models.BooleanField(default=False)           #whether to record audio during activity
    record_audio_video = models.BooleanField(default=False)     #whether to record audio and video both during the activity
    data_recording_session = models.BooleanField(default=False) #whether the session is just for data collection purposes
    pin = models.CharField(max_length=6)

# Consents
class Consent(models.Model):
    session = models.ForeignKey(Session,on_delete=models.CASCADE)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    given_at = models.DateTimeField(auto_now_add=True)

                      #to access the session
# Model for storing mapping for Etherpad users
class AuthorMap(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)  #user
    authorid = models.CharField(max_length=20)                  #Author id from Etherpad

# Model for storing Etherpad session id
class SessionGroupMap(models.Model):
    session = models.ForeignKey(Session,on_delete=models.CASCADE) #session
    eth_groupid = models.CharField(max_length=20)                 #Etherpad session

# Model for storing pad id for each group
class Pad(models.Model):
    session = models.ForeignKey(Session,on_delete=models.CASCADE) #session
    eth_padid = models.CharField(max_length=50)                   #Etherpad pad id
    group = models.IntegerField()                                 #Group number
    eth_text = models.TextField(blank=True)                       #Text submitted by user

# Model to store Roles
class Role(models.Model):
    ROLE_CHOICES = [(1,'student'),(2,'teacher'),(3,'annotator')]
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    role = models.CharField(max_length=50,choices=ROLE_CHOICES,default='student')

# Function to execute when a used is created
def createRole(sender,instance,created,**kwargs):
    if created:
        r = Role(user=instance,role='student')
        objs = AuthorMap.objects.all().filter(user=instance)
        print(objs,' ',objs.count())
        if objs.count()>0:
            authorid = objs[0].authorid
        else:
            print('making etherpad api request')
            res = call('createAuthorIfNotExistsFor',{'authorMapper':instance.id,'name':instance.username})
            authorid = res['data']['authorID']
            AuthorMap.objects.create(user=instance,authorid=authorid)
        r.save()

# Binding function with User model
post_save.connect(createRole,sender=User)

# Model to store audio or video files
class Audiofl(models.Model):
    session = models.ForeignKey(Session,on_delete=models.CASCADE)
    group = models.IntegerField(blank=True)
    user = models.ForeignKey(User,on_delete=models)
    sequence = models.IntegerField(blank=True)
    description = models.TextField(blank=True)
    started_at = models.DateTimeField(blank=True)
    fl = models.FileField(upload_to=user_directory_path, blank=True, )

# Model to store voice activity detection data
class VAD(models.Model):
    session = models.ForeignKey(Session,on_delete=models.CASCADE)
    group = models.IntegerField(blank=True)
    user = models.ForeignKey(User,on_delete=models)
    timestamp = models.DateTimeField(blank=True)
    activity = models.BigIntegerField(blank=True)

# To store real-time speech to text data. Only available for chrome browser
class Speech(models.Model):
    session = models.ForeignKey(Session,on_delete=models.CASCADE)
    group = models.IntegerField(blank=True)
    user = models.ForeignKey(User,on_delete=models)
    timestamp = models.DateTimeField(blank=True)
    TextField = models.TextField(blank=True)

# Log students and teachers actions
class activityLog(models.Model):
    session = models.ForeignKey(Session,on_delete=models.CASCADE)
    actor = models.ForeignKey(User,on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now=True)
    verb = models.TextField(blank=True)
    object = models.TextField(blank=True)

# To store observation data
class observationData(models.Model):
    session = models.ForeignKey(Session,on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now=True)
    observation = models.TextField(blank=True)



# Collaboration questionnaire based on jhonson & jhonson work
class CollaborationQ(models.Model):
    session = models.ForeignKey(Session,on_delete=models.CASCADE)
    sub_date = models.DateField(default=datetime.date.today)
    group = models.IntegerField()
    submitted_user = models.ForeignKey(User,on_delete=models.CASCADE)
    q1 = models.IntegerField()
    q2 = models.IntegerField()
    q3 = models.IntegerField()
    q4 = models.IntegerField()
    q5 = models.IntegerField()
    q6 = models.IntegerField()
    q7 = models.IntegerField()
    q8 = models.IntegerField()
    q9 = models.IntegerField()
    q10 = models.IntegerField()
    q11 = models.IntegerField()
    q12 = models.IntegerField()
    q13 = models.IntegerField()
    q14 = models.IntegerField()
    q15 = models.IntegerField()
    q16 = models.IntegerField()
    q17 = models.IntegerField()
    q18 = models.IntegerField()
    q19 = models.IntegerField()
    q20 = models.IntegerField()
    q21 = models.IntegerField()
    q22 = models.IntegerField()
    q23 = models.IntegerField()
    q24 = models.IntegerField()
    q25 = models.IntegerField()
    q26 = models.IntegerField()
    q27 = models.IntegerField()
    q28 = models.IntegerField()
    q29 = models.IntegerField()
    q30 = models.IntegerField()
    q31 = models.IntegerField()
    q32 = models.IntegerField()
    q33 = models.IntegerField()
    q34 = models.IntegerField()
    q35 = models.IntegerField()
    q36 = models.IntegerField()
    q37 = models.IntegerField()

# Model to store responses to SUS questionnaire
class UsabilityQ(models.Model):
    sub_date = models.DateField(default=datetime.date.today)
    submitted_user = models.ForeignKey(User,on_delete=models.CASCADE)
    q1 = models.IntegerField()
    q2 = models.IntegerField()
    q3 = models.IntegerField()
    q4 = models.IntegerField()
    q5 = models.IntegerField()
    q6 = models.IntegerField()
    q7 = models.IntegerField()
    q8 = models.IntegerField()
    q9 = models.IntegerField()
    q10 = models.IntegerField()
    q11 = models.IntegerField()
    q12 = models.IntegerField()
    q13 = models.IntegerField()
    q14 = models.IntegerField()
    q15 = models.IntegerField()
    q16 = models.IntegerField()
    q17 = models.IntegerField()

# Model to store anonymous data
class AnonyData(models.Model):
    submission = models.OneToOneField(CollaborationQ,on_delete=models.CASCADE)
    age = models.IntegerField()
    gender = models.CharField(max_length=10)



admin.site.register(CollaborationQ)
admin.site.register(Audiofl)
admin.site.register(Session)
admin.site.register(Pad)
admin.site.register(SessionGroupMap)
admin.site.register(AuthorMap)
admin.site.register(Role)
admin.site.register(UsabilityQ)
admin.site.register(activityLog)
admin.site.register(VAD)
