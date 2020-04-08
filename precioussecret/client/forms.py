from django import forms


class AddSecretForm(forms.Form):
    url = forms.URLField(required=False)
    file = forms.FileField(required=False)

class AccessSecretForm(forms.Form):
    access_code = forms.CharField(required=True)
