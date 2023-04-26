from django import forms

class UploadForm(forms.Form):
    TYPE = [
        ('S', 'Signal'),
        ('T', 'Telegram'),
        ('W', 'WhatsApp'),
    ]
    file = forms.FileField()
    type = forms.ChoiceField(choices=TYPE)