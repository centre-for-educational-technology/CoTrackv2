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
import operator
COUNTRIES = {
    "AF": _("Afghanistan"),
    "AX": _("Åland Islands"),
    "AL": _("Albania"),
    "DZ": _("Algeria"),
    "AS": _("American Samoa"),
    "AD": _("Andorra"),
    "AO": _("Angola"),
    "AI": _("Anguilla"),
    "AQ": _("Antarctica"),
    "AG": _("Antigua and Barbuda"),
    "AR": _("Argentina"),
    "AM": _("Armenia"),
    "AW": _("Aruba"),
    "AU": _("Australia"),
    "AT": _("Austria"),
    "AZ": _("Azerbaijan"),
    "BS": _("Bahamas"),
    "BH": _("Bahrain"),
    "BD": _("Bangladesh"),
    "BB": _("Barbados"),
    "BY": _("Belarus"),
    "BE": _("Belgium"),
    "BZ": _("Belize"),
    "BJ": _("Benin"),
    "BM": _("Bermuda"),
    "BT": _("Bhutan"),
    "BO": _("Bolivia (Plurinational State of)"),
    "BQ": _("Bonaire, Sint Eustatius and Saba"),
    "BA": _("Bosnia and Herzegovina"),
    "BW": _("Botswana"),
    "BV": _("Bouvet Island"),
    "BR": _("Brazil"),
    "IO": _("British Indian Ocean Territory"),
    "BN": _("Brunei Darussalam"),
    "BG": _("Bulgaria"),
    "BF": _("Burkina Faso"),
    "BI": _("Burundi"),
    "CV": _("Cabo Verde"),
    "KH": _("Cambodia"),
    "CM": _("Cameroon"),
    "CA": _("Canada"),
    "KY": _("Cayman Islands"),
    "CF": _("Central African Republic"),
    "TD": _("Chad"),
    "CL": _("Chile"),
    "CN": _("China"),
    "CX": _("Christmas Island"),
    "CC": _("Cocos (Keeling) Islands"),
    "CO": _("Colombia"),
    "KM": _("Comoros"),
    "CG": _("Congo"),
    "CD": _("Congo (the Democratic Republic of the)"),
    "CK": _("Cook Islands"),
    "CR": _("Costa Rica"),
    "CI": _("Côte d'Ivoire"),
    "HR": _("Croatia"),
    "CU": _("Cuba"),
    "CW": _("Curaçao"),
    "CY": _("Cyprus"),
    "CZ": _("Czechia"),
    "DK": _("Denmark"),
    "DJ": _("Djibouti"),
    "DM": _("Dominica"),
    "DO": _("Dominican Republic"),
    "EC": _("Ecuador"),
    "EG": _("Egypt"),
    "SV": _("El Salvador"),
    "GQ": _("Equatorial Guinea"),
    "ER": _("Eritrea"),
    "EE": _("Estonia"),
    "SZ": _("Eswatini"),
    "ET": _("Ethiopia"),
    "FK": _("Falkland Islands (Malvinas)"),
    "FO": _("Faroe Islands"),
    "FJ": _("Fiji"),
    "FI": _("Finland"),
    "FR": _("France"),
    "GF": _("French Guiana"),
    "PF": _("French Polynesia"),
    "TF": _("French Southern Territories"),
    "GA": _("Gabon"),
    "GM": _("Gambia"),
    "GE": _("Georgia"),
    "DE": _("Germany"),
    "GH": _("Ghana"),
    "GI": _("Gibraltar"),
    "GR": _("Greece"),
    "GL": _("Greenland"),
    "GD": _("Grenada"),
    "GP": _("Guadeloupe"),
    "GU": _("Guam"),
    "GT": _("Guatemala"),
    "GG": _("Guernsey"),
    "GN": _("Guinea"),
    "GW": _("Guinea-Bissau"),
    "GY": _("Guyana"),
    "HT": _("Haiti"),
    "HM": _("Heard Island and McDonald Islands"),
    "VA": _("Holy See"),
    "HN": _("Honduras"),
    "HK": _("Hong Kong"),
    "HU": _("Hungary"),
    "IS": _("Iceland"),
    "IN": _("India"),
    "ID": _("Indonesia"),
    "IR": _("Iran (Islamic Republic of)"),
    "IQ": _("Iraq"),
    "IE": _("Ireland"),
    "IM": _("Isle of Man"),
    "IL": _("Israel"),
    "IT": _("Italy"),
    "JM": _("Jamaica"),
    "JP": _("Japan"),
    "JE": _("Jersey"),
    "JO": _("Jordan"),
    "KZ": _("Kazakhstan"),
    "KE": _("Kenya"),
    "KI": _("Kiribati"),
    "KP": _("Korea (the Democratic People's Republic of)"),
    "KR": _("Korea (the Republic of)"),
    "KW": _("Kuwait"),
    "KG": _("Kyrgyzstan"),
    "LA": _("Lao People's Democratic Republic"),
    "LV": _("Latvia"),
    "LB": _("Lebanon"),
    "LS": _("Lesotho"),
    "LR": _("Liberia"),
    "LY": _("Libya"),
    "LI": _("Liechtenstein"),
    "LT": _("Lithuania"),
    "LU": _("Luxembourg"),
    "MO": _("Macao"),
    "MG": _("Madagascar"),
    "MW": _("Malawi"),
    "MY": _("Malaysia"),
    "MV": _("Maldives"),
    "ML": _("Mali"),
    "MT": _("Malta"),
    "MH": _("Marshall Islands"),
    "MQ": _("Martinique"),
    "MR": _("Mauritania"),
    "MU": _("Mauritius"),
    "YT": _("Mayotte"),
    "MX": _("Mexico"),
    "FM": _("Micronesia (Federated States of)"),
    "MD": _("Moldova (the Republic of)"),
    "MC": _("Monaco"),
    "MN": _("Mongolia"),
    "ME": _("Montenegro"),
    "MS": _("Montserrat"),
    "MA": _("Morocco"),
    "MZ": _("Mozambique"),
    "MM": _("Myanmar"),
    "NA": _("Namibia"),
    "NR": _("Nauru"),
    "NP": _("Nepal"),
    "NL": _("Netherlands"),
    "NC": _("New Caledonia"),
    "NZ": _("New Zealand"),
    "NI": _("Nicaragua"),
    "NE": _("Niger"),
    "NG": _("Nigeria"),
    "NU": _("Niue"),
    "NF": _("Norfolk Island"),
    "MK": _("North Macedonia"),
    "MP": _("Northern Mariana Islands"),
    "NO": _("Norway"),
    "OM": _("Oman"),
    "PK": _("Pakistan"),
    "PW": _("Palau"),
    "PS": _("Palestine, State of"),
    "PA": _("Panama"),
    "PG": _("Papua New Guinea"),
    "PY": _("Paraguay"),
    "PE": _("Peru"),
    "PH": _("Philippines"),
    "PN": _("Pitcairn"),
    "PL": _("Poland"),
    "PT": _("Portugal"),
    "PR": _("Puerto Rico"),
    "QA": _("Qatar"),
    "RE": _("Réunion"),
    "RO": _("Romania"),
    "RU": _("Russian Federation"),
    "RW": _("Rwanda"),
    "BL": _("Saint Barthélemy"),
    "SH": _("Saint Helena, Ascension and Tristan da Cunha"),
    "KN": _("Saint Kitts and Nevis"),
    "LC": _("Saint Lucia"),
    "MF": _("Saint Martin (French part)"),
    "PM": _("Saint Pierre and Miquelon"),
    "VC": _("Saint Vincent and the Grenadines"),
    "WS": _("Samoa"),
    "SM": _("San Marino"),
    "ST": _("Sao Tome and Principe"),
    "SA": _("Saudi Arabia"),
    "SN": _("Senegal"),
    "RS": _("Serbia"),
    "SC": _("Seychelles"),
    "SL": _("Sierra Leone"),
    "SG": _("Singapore"),
    "SX": _("Sint Maarten (Dutch part)"),
    "SK": _("Slovakia"),
    "SI": _("Slovenia"),
    "SB": _("Solomon Islands"),
    "SO": _("Somalia"),
    "ZA": _("South Africa"),
    "GS": _("South Georgia and the South Sandwich Islands"),
    "SS": _("South Sudan"),
    "ES": _("Spain"),
    "LK": _("Sri Lanka"),
    "SD": _("Sudan"),
    "SR": _("Suriname"),
    "SJ": _("Svalbard and Jan Mayen"),
    "SE": _("Sweden"),
    "CH": _("Switzerland"),
    "SY": _("Syrian Arab Republic"),
    "TW": _("Taiwan (Province of China)"),
    "TJ": _("Tajikistan"),
    "TZ": _("Tanzania, the United Republic of"),
    "TH": _("Thailand"),
    "TL": _("Timor-Leste"),
    "TG": _("Togo"),
    "TK": _("Tokelau"),
    "TO": _("Tonga"),
    "TT": _("Trinidad and Tobago"),
    "TN": _("Tunisia"),
    "TR": _("Turkey"),
    "TM": _("Turkmenistan"),
    "TC": _("Turks and Caicos Islands"),
    "TV": _("Tuvalu"),
    "UG": _("Uganda"),
    "UA": _("Ukraine"),
    "AE": _("United Arab Emirates"),
    "GB": _("United Kingdom of Great Britain and Northern Ireland"),
    "UM": _("United States Minor Outlying Islands"),
    "US": _("United States of America"),
    "UY": _("Uruguay"),
    "UZ": _("Uzbekistan"),
    "VU": _("Vanuatu"),
    "VE": _("Venezuela (Bolivarian Republic of)"),
    "VN": _("Viet Nam"),
    "VG": _("Virgin Islands (British)"),
    "VI": _("Virgin Islands (U.S.)"),
    "WF": _("Wallis and Futuna"),
    "EH": _("Western Sahara"),
    "YE": _("Yemen"),
    "ZM": _("Zambia"),
    "ZW": _("Zimbabwe"),
}

sort_countries = sorted(COUNTRIES.items(), key=operator.itemgetter(1))
countries_choices = [(k, v) for k, v in COUNTRIES.items()]
age_choices=[(1,_("17 or less")),(2,"18 - 27"),(3,"28 - 37"),(4,"38 - 47"),(5,_("48 - 57")),(6,_("58 or more"))]
gen_choices=[("M",_("Male")),("F",_("Female")),("O",_("Other"))]
edu_choices=[(1,_("Primary")),(2,_("Secondary")),(3,_("Bachelor")),(4,_("Master")),(5,_("Doctorate"))]


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


class RoleRequest(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    school =  models.TextField(blank=True)
    class_size = models.IntegerField()
    subject = models.TextField(blank=True)
    decision =  models.BooleanField(default=False)
    pending =  models.BooleanField(default=True)

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
    random_group = models.BooleanField(default=False) #whether the session is just for data collection purposes

class RandomGroup(models.Model):
    session = models.ForeignKey(Session,on_delete=models.CASCADE)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    group = models.IntegerField()


class GroupPin(models.Model):
    session = models.ForeignKey(Session,on_delete=models.CASCADE)
    pin = models.CharField(max_length=6)
    group = models.IntegerField()

# Consents
class Consent(models.Model):
    session = models.ForeignKey(Session,on_delete=models.CASCADE)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    given_at = models.DateTimeField(auto_now_add=True)

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
    ROLE_CHOICES = [('student','student'),('teacher','teacher'),('annotator','annotator')]
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

class SUS(models.Model):
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

class Help(models.Model):
    session = models.ForeignKey(Session,on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    group = models.IntegerField(blank=True)
    seen = models.BooleanField(default=False) # whether teacher has seen the alert or not

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

# Collaboration questionnaire based on jhonson & jhonson work
class EngagementQ(models.Model):
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
    session = models.ForeignKey(Session,on_delete=models.CASCADE)
    sub_date = models.DateField(default=datetime.date.today)
    group = models.IntegerField()
    submitted_user = models.ForeignKey(User,on_delete=models.CASCADE)
    age = models.IntegerField(choices=age_choices,blank=True)
    gender = models.CharField(max_length=10,choices=gen_choices,blank=True)
    education = models.IntegerField(choices=edu_choices,blank=True)
    nationality = models.CharField(max_length=2, choices = sort_countries,blank=True)

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
admin.site.register(Speech)
admin.site.register(GroupPin)
admin.site.register(Help)
admin.site.register(Consent)
admin.site.register(EngagementQ)
admin.site.register(RoleRequest)
admin.site.register(AnonyData)
admin.site.register(SUS)
