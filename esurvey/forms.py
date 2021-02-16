from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from formtools.wizard.views import SessionWizardView
from django.forms.fields import Field
from datetime import date
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe
from .models import Session, Audiofl, VAD
from django.forms import ModelForm
from djrichtextfield.models import RichTextField
from djrichtextfield.widgets import RichTextWidget
from quilljs.widgets import QuillEditorWidget

setattr(Field, 'is_checkbox', lambda self: isinstance(self.widget, forms.CheckboxInput ))


class AudioflForm(forms.ModelForm):
    class Meta:
        model = Audiofl
        fields = ('description', 'fl', 'session','user','group','sequence' )
        widgets = {'description':forms.HiddenInput(),'fl': forms.HiddenInput(),'session':forms.HiddenInput(),'user':forms.HiddenInput(),'group':forms.HiddenInput(),'sequence':forms.HiddenInput()}


class VADForm(forms.ModelForm):
    strDate = forms.CharField(max_length=20,required=False,widget=forms.HiddenInput())
    milli = forms.IntegerField(max_value=1000,required=False,widget=forms.HiddenInput())

    class Meta:
        model = VAD
        fields = ( 'session','user','group','activity')
        widgets = {'strDate':forms.HiddenInput(),'milli':forms.HiddenInput(),'session':forms.HiddenInput(),'user':forms.HiddenInput(),'group':forms.HiddenInput(),'activity':forms.HiddenInput()}



class SessionForm(ModelForm):
    class Meta:
        model = Session
        fields = ['name','groups','problem']
        widgets = {
            'problem': RichTextWidget(),
        }

class CreateForm1(forms.Form):
    project_choices = [(1,'Individual'),(2,'Comparision A and B'),(3, 'Comparision A, B and C'),(4, 'Comparision A, B, C and D'),(5, 'Comparision A, B, C, D and E')]

    type_questionnaire = forms.CharField(label="Type of Questionnaire",widget=forms.Select(choices=[('TrUX','TrustedUX')],attrs={'class':'form-control'}))
    project_name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}),max_length=100)
    project_type = forms.CharField(widget=forms.Select(choices=project_choices,attrs={'class':'form-control'}))
    test_project = forms.BooleanField(required=False,widget=forms.CheckboxInput(attrs={'class':'form-check-input'}))

class CreateForm2(forms.Form):
    industry_choices = [('Agriculture','Agriculture'),('Automobile','Automobile'),('Building system engineering','Building system engineering'),('Chemical industry','Chemical industry'),('Clothing industory','Clothing industory'),('Consulting','Consulting'),('Crafts','Crafts'),('Electronics','Electronics'),('Energy industry','Energy industry'),('Finance','Finance'),('IT','IT'),('Marketing','Marketing'),('Media','Media'),('Medical','Medical'),('Other','Other'),('Production','Production'),('Retail','Retail'),('Services','Services'),('Sports','Sports'),('Telecommunications','Telecommunications'),('Tourism','Tourism')]
    type_choices = [('Accounting sysetm','Accounting system'),('Consumer Electronics','Consumer Electronics'),('Enterprise resource planning system','Enterprise resource planning system'),('Logistic Systems','Logistic Systems'),('Medical devices','Medical devices'),('Office applications','Office applications'),('Order picking systems','Order picking systems'),('Other','Other'),('Production machinery','Production machinery'),('Smart home applications','Smart home applications'),('Telecommunications','Telecommunications'),('Web applications','Web applications'),('Website','Website')]

    start_date = forms.DateField(widget=forms.DateInput(attrs={'class':'form-control','type':'date'}))
    end_date = forms.DateField(widget=forms.DateInput(attrs={'class':'form-control','type':'date'}))
    name_of_survey = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}),max_length=100)
    product_name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}),max_length=100)
    product_type = forms.CharField(widget=forms.Select(choices=type_choices,attrs={'class':'form-control'}),max_length=100)
    product_industry = forms.CharField(widget=forms.Select(choices=industry_choices,attrs={'class':'form-control'}))

    def clean_start_date(self):
        start_date = self.cleaned_data['start_date']
        if start_date < date.today():
            raise ValidationError('You can not choose start date in past.')
        else:
            return start_date

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date:
            if start_date > end_date:
                raise ValidationError('Project end date must be after the start date.')





class CreateForm3(forms.Form):
    CHOICES = [('A','anonymous participation'),('P','invite participants')]
    type_of_participation=forms.CharField( widget=forms.Select(choices=CHOICES,attrs={'class':'form-control'}))


class CreateForm4(forms.Form):
    CHOICES = [('En','English'),('Pt','Portugese'),('Est','Estonian')]
    questionnaire_language=forms.CharField( widget=forms.Select(choices=CHOICES,attrs={'class':'form-control'}))
    title = forms.CharField(initial="Assessment of {PRODUCT_NAME}",widget=forms.TextInput(attrs={'class':'form-control'}),max_length=100)
    subtitle = forms.CharField(initial="Welcome to the assessment of {PRODUCT_NAME}",widget=forms.TextInput(attrs={'class':'form-control'}),max_length=100)
    paragraph = forms.CharField(initial="With your help, we would like to examine how users perceive the usability and aesthetics of {PRODUCT_NAME}. We hope to identify areas for optimization. This will enable us to optimize the product in such a way that it is as efficient and comprehensible as possible.",widget=forms.Textarea(attrs={'class':'form-control'}),help_text=mark_safe('You can use following variables to use in title, subtitle and paragraph: <br/>{PROJECT_NAME} - Name of project <br/> {PRODUCT_NAME} - Name of product<br/> {SURVEY_NAME} - Name of survey <br/> {TODAY} - for today date.'))

class lastForm(forms.Form):
    CHOICES=[(True,'Activate now'),(False,'Activate later')]
    project_status = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect(attrs={'class': "custom-radio-list"}),initial=True)

class AnonyForm(forms.Form):
    CHOICES=[(1,'Below 20'),(2,'20 - 30'),(3,'30 - 40'),(4,'40 - 50'),(5,'Above 50 ')]
    gen_choices=[('M','Male'),('F','Female')]
    age_group = forms.ChoiceField(choices=CHOICES)
    gender = forms.ChoiceField(choices=gen_choices)
