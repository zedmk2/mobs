from work import models
from . import views
from django import forms
from django.core import validators
from django.forms import formsets
from django.forms.models import inlineformset_factory
from datetime import time

class DateForm(forms.Form):
    begin = forms.DateField(required=True,widget=forms.DateInput(attrs={'class': 'payrollDate','type':'date','placeholder':'mm/dd/yyyy'}))
    end = forms.DateField(required=True,widget=forms.DateInput(attrs={'class': 'payrollDate','type':'date','placeholder':'mm/dd/yyyy'}))

    def clean(self):
        cleaned_data = super().clean()
        begin = cleaned_data.get('begin')
        end = cleaned_data.get('end')
        if  begin > end:
            raise forms.ValidationError("End date must be after start date")
        return cleaned_data
