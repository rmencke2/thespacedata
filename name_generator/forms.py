from django import forms

class NameRequestForm(forms.Form):
    prompt = forms.CharField(
        label="Describe what you want",
        widget=forms.Textarea(attrs={
            "id": "id_prompt",  # explicit id (optional—Django auto-adds)
            "rows": 4,
            "placeholder": "e.g. Sustainable laundry pickup for busy families; fresh, modern, upbeat; avoid cheesy puns; 8–12 letter names.",
            "class": "w-full rounded-md border px-3 py-2",
            "autofocus": "autofocus",
            "required": "required",
        }),
    )
    # (industry / style / count optional)
    # optional advanced fields if you use them
    count = forms.IntegerField(initial=10, min_value=1, max_value=50, required=False)
    style = forms.CharField(required=False)

    # Advanced (optional)
    industry = forms.CharField(
        label="Industry (optional)", required=False,
        widget=forms.TextInput(attrs={"class": "w-full rounded-md border px-3 py-2"})
    )
    style = forms.CharField(
        label="Style / Tone (optional)", required=False,
        widget=forms.TextInput(attrs={"class": "w-full rounded-md border px-3 py-2"})
    )
    count = forms.IntegerField(
        label="How many suggestions?", required=False, min_value=3, max_value=25, initial=10,
        widget=forms.NumberInput(attrs={"class": "w-full rounded-md border px-3 py-2"})
    )

    def clean_count(self):
        v = self.cleaned_data.get("count")
        return v or 10