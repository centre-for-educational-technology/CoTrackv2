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
    CHOICES = [('En','English'),('Et','Estonian')]
    name = forms.CharField(label=_('Session name'),widget=forms.TextInput(attrs={'class':'form-control'}))
    groups = forms.IntegerField(label=_('Number of groups'),widget=forms.NumberInput(attrs={'class':'form-control'}))
    language=forms.CharField(widget=forms.Select(choices=CHOICES,attrs={'class':'form-control'}))
    duration_days = forms.IntegerField(label=_('Days'),widget=forms.NumberInput(attrs={'class':'form-control','placeholder':'Days'}))
    duration_hours = forms.IntegerField(label=_('Hours'),widget=forms.NumberInput(attrs={'class':'form-control','placeholder':'Hours'}))
    duration_minutes = forms.IntegerField(label=_('Minutes'),widget=forms.NumberInput(attrs={'class':'form-control','placeholder':'Minutes'}))
    new = forms.IntegerField(widget=forms.HiddenInput(),required=False,initial=-1) # store -1 if session is new otherwise contains session id

class CreateForm2(forms.Form):
    learning_problem = forms.CharField(label=_('Learning activity'),widget=CKEditorUploadingWidget(attrs={'class':'form-control'}),required=False)

class CreateForm3(forms.Form):
    useEtherpad = forms.BooleanField(required=False,widget=DjangoToggleSwitchWidget(klass="django-toggle-switch-dark-primary"))
    useAVchat = forms.BooleanField(required=False,widget=DjangoToggleSwitchWidget(klass="django-toggle-switch-dark-primary"))
    random_group = forms.BooleanField(required=False,widget=DjangoToggleSwitchWidget(klass="django-toggle-switch-dark-primary"))


    record_audio = forms.BooleanField(required=False,widget=DjangoToggleSwitchWidget(klass="django-toggle-switch-dark-primary"))
    record_audio_video = forms.BooleanField(required=False,widget=DjangoToggleSwitchWidget(klass="django-toggle-switch-dark-primary"))

class CreateForm4(forms.Form):
    CHOICES=[(True,_('Enable')),(False,_('Disable'))]
    allow_access = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect(attrs={'class': "custom-radio-list"}),initial=True)

class consentForm(forms.Form):
    permission = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class': "form-check-input"}),initial=False,required=True)

class AnonyForm(forms.ModelForm):
    class Meta:
        model = AnonyData
        fields = ( 'education','nationality','age','gender')
