from django import forms


class NameRequestForm(forms.Form):
    prompt = forms.CharField(
        label="Describe what you want",
        widget=forms.Textarea(attrs={
            "id": "id_prompt",  # explicit id (optional—Django auto-adds anyway)
            "rows": 4,
            "placeholder": (
                "e.g. Sustainable laundry pickup for busy families; "
                "fresh, modern, upbeat; avoid cheesy puns; 8–12 letter names."
            ),
            "class": "w-full rounded-md border px-3 py-2",
            "autofocus": "autofocus",
            "required": "required",
        }),
    )

    industry = forms.CharField(
        label="Industry (optional)",
        required=False,
        widget=forms.TextInput(attrs={
            "class": "w-full rounded-md border px-3 py-2",
            "placeholder": "fintech, wellness, SaaS",
        }),
    )

    style = forms.CharField(
        label="Style / Tone (optional)",
        required=False,
        widget=forms.TextInput(attrs={
            "class": "w-full rounded-md border px-3 py-2",
            "placeholder": "modern, playful, premium",
        }),
    )

    count = forms.IntegerField(
        label="How many suggestions?",
        required=False,
        min_value=3,
        max_value=25,
        initial=10,
        widget=forms.NumberInput(attrs={
            "class": "w-full rounded-md border px-3 py-2",
        }),
    )

    def clean_count(self):
        v = self.cleaned_data.get("count")
        return v or 10