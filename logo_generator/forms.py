from django import forms
from .models import LogoProject


class BriefForm(forms.ModelForm):
    """
    Minimal-first UX:
      - Only brand_name is required
      - Tagline and the rest are optional, exposed in the Advanced section
    """
    class Meta:
        model = LogoProject
        fields = [
            "brand_name",
            "tagline",
            "industry",
            "style_keywords",
            "values",
            "colors",
            "icon_ideas",
        ]
        labels = {
            "brand_name": "Brand name",
            "tagline": "Tagline (optional)",
            "industry": "Industry",
            "style_keywords": "Style keywords",
            "values": "Values",
            "colors": "Color constraints",
            "icon_ideas": "Icon ideas",
        }
        widgets = {
            "brand_name": forms.TextInput(attrs={
                "placeholder": "Acme Co.",
                "class": "block w-full rounded-lg border border-slate-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500",
            }),
            "tagline": forms.TextInput(attrs={
                "placeholder": "Optional — e.g. “Get your body back in shape”",
                "class": "block w-full rounded-lg border border-slate-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500",
            }),
            "industry": forms.TextInput(attrs={
                "placeholder": "e.g. Fitness, SaaS, Consulting",
                "class": "block w-full rounded-lg border border-slate-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500",
            }),
            "style_keywords": forms.TextInput(attrs={
                "placeholder": "e.g. modern, playful, elegant, bold",
                "class": "block w-full rounded-lg border border-slate-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500",
            }),
            "values": forms.Textarea(attrs={
                "rows": 3,
                "placeholder": "Optional — what the brand stands for (trust, innovation, sustainability)",
                "class": "block w-full rounded-lg border border-slate-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500",
            }),
            "colors": forms.TextInput(attrs={
                "placeholder": "Optional — words or HEX (e.g. “#0F172A, gold” or “green and black”)",
                "class": "block w-full rounded-lg border border-slate-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500",
            }),
            "icon_ideas": forms.TextInput(attrs={
                "placeholder": "Optional — e.g. dog, rocket, leaf",
                "class": "block w-full rounded-lg border border-slate-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Minimal requirement: only brand_name
        self.fields["brand_name"].required = True
        self.fields["tagline"].required = False
        self.fields["industry"].required = False
        self.fields["style_keywords"].required = False
        self.fields["values"].required = False
        self.fields["colors"].required = False
        self.fields["icon_ideas"].required = False