from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User



class RegisterForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True

        self.fields['first_name'].widget.attrs.update({'class': 'form-control'})
        #self.fields['first_name'].widget.attrs.update({'placeholder': 'First Name'})

        self.fields['last_name'].widget.attrs.update({'class': 'form-control'})
        #self.fields['last_name'].widget.attrs.update({'placeholder': 'Last Name'})


        self.fields['email'].widget.attrs.update({'class': 'form-control'})
        #self.fields['email'].widget.attrs.update({'placeholder': 'Email'})

        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        #self.fields['password1'].widget.attrs.update({'placeholder': 'Password'})

        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
        #self.fields['password2'].widget.attrs.update({'placeholder': 'Repeat password'})






    class Meta:
        model = User
        fields = ('first_name','last_name', 'email', 'password1', 'password2', )


    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            user = User.objects.filter(email=email)
            print(user[0])
            u = user[0]
            if u.is_active:
                raise ValidationError("Email already exists")
            else:
                print('not active')

        return email

class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class':'form-control'}),max_length=254)
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control'}))
