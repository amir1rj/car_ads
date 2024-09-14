from django import forms


class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Enter phone number or email', "class": "form-control"}), )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter password', "class": "form-control"}))
