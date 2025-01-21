from django import forms

from .models import User


class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField()
    remember_me = forms.BooleanField(required=False)

    def add_incorrect_error(self):
        self.add_error('email', 'Email or password is incorrect.')

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if email and password:
            try:
                user = User.objects.filter(email=email).get()
            except User.DoesNotExist:
                self.add_incorrect_error()
            else:
                if not user.check_password(password):
                    self.add_incorrect_error()


class SignUpForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField()
    password2 = forms.CharField()

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')
        password2 = cleaned_data.get('password2')

        if password != password2:
            self.add_error('password2', 'Passwords did not match.')
        elif User.objects.filter(email=email).exists():
            self.add_error('email', 'Email is already in use.')
