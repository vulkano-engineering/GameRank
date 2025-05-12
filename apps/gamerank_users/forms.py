from django import forms
from django.contrib.auth import authenticate
from .models import SitePassword, UserProfile

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    site_password = forms.CharField(widget=forms.PasswordInput, label="Site Password")

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        site_password = cleaned_data.get('site_password')

        # Check site password first
        if site_password:
            if not SitePassword.objects.filter(value=site_password).exists():
                self.add_error('site_password', "Incorrect site password.")
                # No need to check user credentials if site password fails
                return cleaned_data 
        else:
            self.add_error('site_password', "Site password is required.")
            return cleaned_data

        # Then authenticate user
        if username and password:
            user = authenticate(username=username, password=password)
            if user is None:
                self.add_error('username', "Invalid username or password.")
            else:
                cleaned_data['user'] = user # Add user to cleaned_data
        elif not username:
            self.add_error('username', "Username is required.")
        elif not password:
            self.add_error('password', "Password is required.")
            
        return cleaned_data

class UserSettingsForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['alias', 'font_family', 'font_size']
        # Add widgets or choices later if needed 