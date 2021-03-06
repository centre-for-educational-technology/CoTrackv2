from django.db import models
from django.contrib.auth.models import User
import uuid
from django.contrib import admin
import datetime
import os
from django.db.models.signals import post_save
from django.conf import settings
import requests
from django.contrib import messages
from ckeditor_uploader.fields import RichTextUploadingField

def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return os.path.join(
      "session_%d" % instance.session.id,"group_%d" % instance.group, "user_%s" % instance.user.id, filename)

def call(function,arguments=None,request=None):
    try:
        url = settings.ETHERPAD_URL + '/api/1.2.12/' +function+'?apikey='+settings.ETHERPAD_KEY
        response = requests.post(url,arguments)
        x = response.json()
        print('Returned:x',x)
        return x
    except:

        return redirect('project_home')


class Session(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    groups = models.IntegerField()
    problem = RichTextUploadingField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=False)
    #assessment = models.IntegerField()
    survey = models.BooleanField(default=False)



class AuthorMap(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    authorid = models.CharField(max_length=20)

class SessionGroupMap(models.Model):
    session = models.ForeignKey(Session,on_delete=models.CASCADE)
    eth_groupid = models.CharField(max_length=20)

class Pad(models.Model):
    session = models.ForeignKey(Session,on_delete=models.CASCADE)
    eth_padid = models.CharField(max_length=50)
    group = models.IntegerField()
    eth_text = models.TextField(blank=True)


class Role(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    role = models.CharField(max_length=50,default='student')

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

post_save.connect(createRole,sender=User)



class Audiofl(models.Model):
    session = models.ForeignKey(Session,on_delete=models.CASCADE)
    group = models.IntegerField(blank=True)
    user = models.ForeignKey(User,on_delete=models)
    sequence = models.IntegerField(blank=True)
    description = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    fl = models.FileField(upload_to=user_directory_path, blank=True, )

class SessionPin(models.Model):
    session = models.OneToOneField(Session, on_delete=models.CASCADE)
    pin = models.CharField(max_length=6)

# Create your models here.
class Project(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    questionnaire_type  = models.CharField(default=False,max_length=100)
    project_name = models.CharField(max_length=100)
    test_project = models.BooleanField(max_length=100)
    project_type = models.IntegerField()
    project_status = models.BooleanField()
    archived = models.BooleanField(default=False)
    closed = models.BooleanField(default=False)

class Survey(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    survey_name = models.CharField(max_length=100)
    product_name = models.CharField(max_length=200)
    product_type = models.CharField(max_length=200)
    product_industry = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField()
    title = models.CharField(max_length=100)
    subtitle = models.CharField(max_length=200)
    paragraph = models.TextField(max_length=1000)


class VAD(models.Model):
    session = models.ForeignKey(Session,on_delete=models.CASCADE)
    group = models.IntegerField(blank=True)
    user = models.ForeignKey(User,on_delete=models)
    timestamp = models.DateTimeField(blank=True)
    activity = models.BigIntegerField(blank=True)



class Link(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    url = models.UUIDField(default=uuid.uuid4)
    sequence = models.IntegerField()


class Submission(models.Model):
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

class Usability(models.Model):

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


class AnonyData(models.Model):
    submission = models.OneToOneField(Submission,on_delete=models.CASCADE)
    age = models.IntegerField()
    gender = models.CharField(max_length=10)


admin.site.register(Project)
admin.site.register(Survey)
admin.site.register(Link)
admin.site.register(Submission)
admin.site.register(Audiofl)
admin.site.register(Session)
admin.site.register(Pad)
admin.site.register(SessionGroupMap)
admin.site.register(AuthorMap)
admin.site.register(Role)
admin.site.register(SessionPin)
admin.site.register(Usability)
