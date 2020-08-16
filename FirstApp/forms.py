from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from . MongoModels import *

# testing the login form
class LoginForm(forms.Form):
    # username = forms.CharField(max_length=100)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())

    def clean(self):
        # cleaned_username = self.cleaned_data.get('username')
        cleaned_email = self.cleaned_data.get('email')
        cleaned_password = self.cleaned_data.get('password')

        lecturer = Lecturer.objects.get(email=cleaned_email)

        # if a lecturer is already in the system
        if (lecturer):
            # retrieve the User object
            user = User.objects.get(email=cleaned_email)
            is_user = user.check_password(cleaned_password)

            # if the password is correct
            if (is_user):
                # lec_credentials = LecturerCredentials.objects.filter(username_id=lecturer.id)
                lec_credentials = LecturerCredentials.objects.get(username_id=lecturer.id)

                print('credentials: ', lec_credentials)

                # if lecture credentials are already created
                if (lec_credentials):
                    lec_credentials.password = user.password
                    lec_credentials.save(force_update=True)

                else:
                    LecturerCredentials(
                        username_id=lecturer.id,
                        password=user.password
                    ).save()

            else:
                raise forms.ValidationError("Username or password is incorrect")

        else:
            raise forms.ValidationError("The lecturer does not exist")

        return super(LoginForm, self).clean()


# model form for Lecturer credentials
class LecturerCredentialsForm(forms.ModelForm):

    class Meta:
        model = LecturerCredentials
        fields = '__all__'
        widgets = {
            'password': forms.PasswordInput()
        }