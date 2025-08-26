from django import forms

class NameRequestForm(forms.Form):
    keywords = forms.CharField(
        label="Keywords",
        help_text="Comma-separated: e.g. coffee, cozy, neighborhood",
        max_length=200,
        widget=forms.TextInput(attrs={"placeholder": "coffee, cozy, neighborhood"})
    )
    industry = forms.CharField(
        label="Industry",
        required=False,
        max_length=120,
        widget=forms.TextInput(attrs={"placeholder": "cafe / SaaS / consulting ..."})
    )
    style = forms.CharField(
        label="Style",
        required=False,
        max_length=80,
        widget=forms.TextInput(attrs={"placeholder": "modern, playful, premium ..."})
    )
    count = forms.IntegerField(
        label="How many names?",
        min_value=3, max_value=12, initial=6
    )