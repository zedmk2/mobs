from work import models
from . import views
from django import forms
from django.core import validators
from django.forms import formsets
from django.forms.models import inlineformset_factory
from datetime import time

class InspectionForm(forms.ModelForm):
    class Meta:
        model = models.Inspection
        fields = ['created_by','updated_by','prop','date','rating','description',]

class UpdateInspectionForm(forms.ModelForm):

    class Meta:
        model = models.Inspection
        fields = ['updated_by','prop','date','rating','description',]

class ScheduleForm(forms.ModelForm):

    class Meta:
        model = models.Shift
        fields = ['driver','helper','date','truck']

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

class CreateShiftForm(forms.ModelForm):

    date = forms.DateField(required=True,widget=forms.DateInput(attrs={'class': 'shiftDate','placeholder':'mm/dd/yyyy'}))
    dr_start_time = forms.TimeField(widget=forms.TextInput(attrs={'class': 'special','type':'time'}))
    dr_end_time = forms.TimeField(widget=forms.TextInput(attrs={'class': 'special','type':'time'}))
    he_start_time = forms.TimeField(widget=forms.TextInput(attrs={'class': 'special','type':'time'}), required=False)
    he_end_time = forms.TimeField(widget=forms.TextInput(attrs={'class': 'special','type':'time'}),required=False)
    he_2_start_time = forms.TimeField(widget=forms.TextInput(attrs={'class': 'special','type':'time'}),required=False)
    he_2_end_time = forms.TimeField(widget=forms.TextInput(attrs={'class': 'special','type':'time'}),required=False)
    driver = forms.ModelChoiceField(queryset = models.Employee.objects.filter(driver=True))
    helper = forms.ModelChoiceField(queryset = models.Employee.objects.filter(helper=True),required=False)
    helper_2 = forms.ModelChoiceField(queryset = models.Employee.objects.filter(helper=True),required=False)
    #Update to ModelChoice/Queryset when equipment model added
    trucks = [(415,'415'),(501,'501'),(502,'502'),(503,'503'),(504,'504'),(203,'203'),(101,'101')]
    truck = forms.ChoiceField(choices = trucks)

    class Meta:
        model = models.Shift
        fields = ['driver','helper','helper_2','truck',
                    'dr_start_time','dr_end_time','he_start_time','he_end_time','he_2_start_time','he_2_end_time','date']

    def __init__(self, is_update=False, **kwargs):
        self.is_update = is_update
        return super(CreateShiftForm, self).__init__(**kwargs)

    def clean_pk(self):
        pk = self.cleaned_data['pk']
        try:
            product = Shift.objects.get(pk=pk)
        except:
            pass
        else:
            if not self.is_update:
                raise forms.ValidationError("Already exists")
            else:

                return pk

class CreateJobForm(forms.ModelForm):

    start_time = forms.TimeField(widget=forms.TextInput(attrs={'class': 'special','type':'time'}))
    end_time = forms.TimeField(widget=forms.TextInput(attrs={'class': 'special','type':'time'}))

    class Meta:
        model = models.Job
        fields = ['job_shift','job_location',
                    'start_time','end_time',]

JobsInlineFormset = inlineformset_factory(models.Shift, models.Job, extra=10, max_num=18, can_delete=True, form=CreateJobForm, fields=('job_location','job_shift','start_time','end_time','pick','blow','sweep'))
