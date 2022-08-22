from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from formtools.wizard.views import SessionWizardView
from django.forms.fields import Field
from datetime import date
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe
from .models import Session, Audiofl, VAD, Speech, Help,RoleRequest, AnonyData
from django.forms import ModelForm
from django_toggle_switch_widget.widgets import DjangoToggleSwitchWidget
from ckeditor.widgets import CKEditorWidget
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django.utils.translation import gettext as _

setattr(Field, 'is_checkbox', lambda self: isinstance(self.widget, forms.CheckboxInput ))


class AudioflForm(forms.ModelForm):
    strDate = forms.CharField(max_length=50,required=False,widget=forms.HiddenInput())
    class Meta:
        model = Audiofl
        fields = ('description', 'fl', 'session','user','group','sequence')
        widgets = {'description':forms.HiddenInput(),'fl': forms.HiddenInput(),'session':forms.HiddenInput(),'user':forms.HiddenInput(),'group':forms.HiddenInput(),'sequence':forms.HiddenInput()}
class RequestForm(forms.ModelForm):
    class Meta:
        model = RoleRequest
        fields = ('school', 'class_size','subject')
        widgets = {'school':forms.TextInput(attrs={'placeholder':'Enter your school/instituion  name.'}),'class_size':forms.NumberInput(attrs={'placeholder':'Enter approximate size of your class where you want to use CoTrack.'}),'subject':forms.TextInput(attrs={'placeholder':'Enter subject of the class session where you plan to use CoTrack.'})}


class VADForm(forms.ModelForm):
    strDate = forms.CharField(max_length=20,required=False,widget=forms.HiddenInput())
    milli = forms.IntegerField(max_value=1000,required=False,widget=forms.HiddenInput())

    class Meta:
        model = VAD
        fields = ( 'session','user','group','activity')
        widgets = {'strDate':forms.HiddenInput(),'milli':forms.HiddenInput(),'session':forms.HiddenInput(),'user':forms.HiddenInput(),'group':forms.HiddenInput(),'activity':forms.HiddenInput()}

class SpeechForm(forms.ModelForm):
    strDate = forms.CharField(max_length=20,required=False,widget=forms.HiddenInput())

    class Meta:
        model = Speech
        fields = ( 'session','user','group','TextField')
        widgets = {'strDate':forms.HiddenInput(),'milli':forms.HiddenInput(),'session':forms.HiddenInput(),'user':forms.HiddenInput(),'group':forms.HiddenInput(),'TextField':forms.HiddenInput()}

class HelpForm(forms.ModelForm):
    class Meta:
        model = Speech
        fields = ( 'session','user','group')
        widgets = {'session':forms.HiddenInput(),'user':forms.HiddenInput(),'group':forms.HiddenInput()}




class SessionForm(ModelForm):
    id = forms.IntegerField(required=False)
    id.widget = forms.HiddenInput()
    class Meta:
        model = Session
        fields = ['name','groups','learning_problem']
        """
        widgets = {
            'problem': CKEditorWidget(),
        }
        """

class CreateForm1(forms.Form):
    CHOICES = [('En',_('English')),('Et',_('Estonian'))]
    name = forms.CharField(label=_('Session name'),widget=forms.TextInput(attrs={'class':'form-control'}))
    groups = forms.IntegerField(label=_('Number of groups'),widget=forms.NumberInput(attrs={'class':'form-control'}))
    language=forms.CharField(label=_('Language'),widget=forms.Select(choices=CHOICES,attrs={'class':'form-control'}))
    duration_days = forms.IntegerField(label=_('Days'),widget=forms.NumberInput(attrs={'class':'form-control','placeholder':_('Days')}))
    duration_hours = forms.IntegerField(label=_('Hours'),widget=forms.NumberInput(attrs={'class':'form-control','placeholder':_('Hours')}))
    duration_minutes = forms.IntegerField(label=_('Minutes'),widget=forms.NumberInput(attrs={'class':'form-control','placeholder':_('Minutes')}))
    new = forms.IntegerField(widget=forms.HiddenInput(),required=False,initial=-1) # store -1 if session is new otherwise contains session id

class CreateForm2(forms.Form):
    learning_problem = forms.CharField(label=_('Learning activity'),widget=CKEditorUploadingWidget(attrs={'class':'form-control'}),required=False)

class CreateForm3(forms.Form):
    useEtherpad = forms.BooleanField(required=False,widget=DjangoToggleSwitchWidget(klass="django-toggle-switch-dark-primary"))
    useAVchat = forms.BooleanField(required=False,widget=DjangoToggleSwitchWidget(klass="django-toggle-switch-dark-primary"))
    random_group = forms.BooleanField(required=False,widget=DjangoToggleSwitchWidget(klass="django-toggle-switch-dark-primary"))


    record_audio = forms.BooleanField(required=False,widget=DjangoToggleSwitchWidget(klass="django-toggle-switch-dark-primary"))
    record_audio_video = forms.BooleanField(required=False,widget=DjangoToggleSwitchWidget(klass="django-toggle-switch-dark-primary"))

    conf_vad = forms.BooleanField(required=False,widget=DjangoToggleSwitchWidget(klass="django-toggle-switch-dark-primary"))
    conf_speech = forms.BooleanField(required=False,widget=DjangoToggleSwitchWidget(klass="django-toggle-switch-dark-primary"))
    conf_engage = forms.BooleanField(required=False,widget=DjangoToggleSwitchWidget(klass="django-toggle-switch-dark-primary"))
    conf_sus = forms.BooleanField(required=False,widget=DjangoToggleSwitchWidget(klass="django-toggle-switch-dark-primary"))
    conf_consent = forms.BooleanField(required=False,widget=DjangoToggleSwitchWidget(klass="django-toggle-switch-dark-primary"))
    conf_demo = forms.BooleanField(required=False,widget=DjangoToggleSwitchWidget(klass="django-toggle-switch-dark-primary"))

    default_consent_form = """<h6 >Dear Participant </h6><br/>
      With your permission, we would like to record audio and video during collaborative activity session so that we can analyze it in detail later on.
      The recording will be saved in  files- in WEBM format on server.
      <br/><br/>
      It should be noticed that:<br/>
      All kinds of data will be stored securely on Google drive (under a password-protected TLU account), and backed up in a password-protected server at TLU, accessible only to the research team.
      This data will be stored not longer than 5 years. <br/>
      The data may be re-used by members of the <a href='http://ceiter.tlu.ee/' target='_blank'>CEITER research team</a>, or in later projects by students of the School of Educational Technologies and School of Educational Sciences.
      <br/><br/>No personal information about you will be shared or made public, and any information you provide will be anonymized before publication. <br/>
      At any point, you can request to withdraw your data from the study, or from this storage. <br/>
      <br/><br/>
      <b>GDPR art. 13</b> requirements: <br/>
      Data Protection Officer (at Tallinn University): andmekaitsespetsialist@tlu.ee<br/>
      <br/>
      <b>Please read carefully the following points and ask for clarifications in case of doubts:</b><br/><br/>

      <ul>
        <li>  The collaboration activity is designed to gather information for research purposes and further development of data collection and visualization technologies to understand collaborative learning activities across spaces.</li>
        <li>  I may withdraw and discontinue my participation at any time.</li>
        <li> My audio and video will be recorded.</li>
        <li> The researcher will not identify me by name in any report using information obtained from this dataset, and my confidentiality as a participant in this study will remain secure. </li>
        <li> Anonymized extracts from the dataset may be used in research publications.  </li>
        <li> I have the right to ask access, rectification, or erasure of my data (as long as it is possible to pinpoint my identity from that data)</li>
      </ul>"""
    consent_content = forms.CharField(label=_('Consent form'),widget=CKEditorUploadingWidget(attrs={'class':'form-control'}),required=False,initial=default_consent_form)


class CreateForm4(forms.Form):
    CHOICES=[(True,_('Enable')),(False,_('Disable'))]
    allow_access = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect(attrs={'class': "custom-radio-list"}),initial=True)

class consentForm(forms.Form):
    permission = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class': "form-check-input"}),initial=False,required=True)

class AnonyForm(forms.ModelForm):
    class Meta:
        model = AnonyData
        fields = ( 'education','nationality','age','gender')
