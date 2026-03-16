from django import forms

class ImageUploadForm(forms.Form):
    image = forms.ImageField(required=True)
    colors = forms.IntegerField(min_value=3, max_value=12, initial=6, required=False)