from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm

class RegisterForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "Username"}))
    email = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "Email"}))
    password = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "Password", "type": "password"}))
    confirm_password = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "Confirm Password", "type": "password"}))
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', "confirm_password"]
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")



class ItineraryForm(forms.Form):
    query = forms.CharField(max_length=100, label="")