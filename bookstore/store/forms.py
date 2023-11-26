from django.contrib.auth.forms import UserCreationForm

from . models import User,Profile
from django import forms

class CustomUserForm(UserCreationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control my-2','placeholder':'Enter username'}))
    email = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control my-2','placeholder':'Enter email','name': 'email'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control my-2','placeholder':'Enter password'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control my-2','placeholder':'Confirm Password'}))
    
    
    class Meta:
        model = User
        fields = ['username','email','password1','password2']
        

    def clean_username(self):
            username = self.cleaned_data['username']
            
            if not len(username)>4:
                raise forms.ValidationError("Username is short")
            return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already in use. Please use a different email.")
        return email
    
# class Userform(User):
#     class Meta:
#         model = User
#         fields = ('first_name','last_name')
        
# class Profileform(Profile):
#     class Meta:
#         model = Profile
#         fields = ('phone','address','city','state','country','pincode')
        
        