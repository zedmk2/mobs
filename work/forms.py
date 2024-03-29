from work import models
from . import views
from django import forms
from django.core import validators
from django.forms import formsets
from django.forms.models import formset_factory, inlineformset_factory, modelformset_factory
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
    date = forms.DateField(required=True,widget=forms.DateInput(attrs={'class': 'shiftDate','placeholder':'mm/dd/yyyy','autocomplete':'off'}))
    class Meta:
        model = models.Shift
        fields = ['driver','helper','day_num','date']


class RouteSelectForm(forms.ModelForm):
    route_select = forms.ModelChoiceField(queryset=models.Route.objects.filter(type='commercial'))

    def label_from_instance(self, obj):
        return "{0} {1}".format(obj.route_num, obj)

    def __init__(self, *args, **kwargs):
        super(RouteSelectForm, self).__init__(*args, **kwargs)

        self.fields['route_select'].label_from_instance = self.label_from_instance

    class Meta:
        model = models.Route
        fields = ['weekday']

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

class QDateForm(forms.Form):
    begin = forms.DateField(required=True,widget=forms.DateInput(attrs={'class': 'payrollDate','type':'date','placeholder':'mm/dd/yyyy'}))

class CreateShiftForm(forms.ModelForm):

    date = forms.DateField(required=True,widget=forms.DateInput(attrs={'class': 'shiftDate','placeholder':'mm/dd/yyyy','autocomplete':'off'}))
    dr_start_time = forms.TimeField(widget=forms.TextInput(attrs={'class': 'special','type':'time'}), required=False)
    dr_end_time = forms.TimeField(widget=forms.TextInput(attrs={'class': 'special','type':'time'}), required=False)
    he_start_time = forms.TimeField(widget=forms.TextInput(attrs={'class': 'special','type':'time'}), required=False)
    he_end_time = forms.TimeField(widget=forms.TextInput(attrs={'class': 'special','type':'time'}),required=False)
    he_2_start_time = forms.TimeField(widget=forms.TextInput(attrs={'class': 'special','type':'time'}),required=False)
    he_2_end_time = forms.TimeField(widget=forms.TextInput(attrs={'class': 'special','type':'time'}),required=False)
    driver = forms.ModelChoiceField(queryset = models.Employee.objects.filter(driver=True))
    helper = forms.ModelChoiceField(queryset = models.Employee.objects.filter(helper=True),required=False)
    helper_2 = forms.ModelChoiceField(queryset = models.Employee.objects.filter(helper=True),required=False)
    day_num = forms.IntegerField()
    #Update to ModelChoice/Queryset when equipment model added
    trucks = [(415,'415'),(501,'501'),(502,'502'),(503,'503'),(504,'504'),(203,'203'),(101,'101'),(12,'12'),(13,'13'),(14,'14'),(15,'15'),(16,'16'),(17,'17'),(18,'18'),(999,'Other')]
    truck = forms.ChoiceField(choices = trucks)

    ST_CHOICES = (
    ('0', 'Sweeping'),
    ('1', 'Landscaping'),
    ('2', 'Power Washing'),
    ('9', 'Other'),)
    shift_type = forms.ChoiceField(choices = ST_CHOICES)

    class Meta:
        model = models.Shift
        fields = ['driver','helper','helper_2','truck',
                    'dr_start_time','dr_end_time','he_start_time','he_end_time','he_2_start_time','he_2_end_time','date','day_num','shift_type']

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

    start_time = forms.TimeField(required=False,widget=forms.TextInput(attrs={'class': 'special','type':'time'}))
    end_time = forms.TimeField(required=False,widget=forms.TextInput(attrs={'class': 'special','type':'time'}))
    order = forms.IntegerField(widget=forms.TextInput(attrs={'class':'jobOrderForm','autocomplete':'off'}))

    class Meta:
        model = models.Job
        fields = ['job_shift','job_location',
                    'start_time','end_time','order']

JobsInlineFormset = inlineformset_factory(models.Shift, models.Job, extra=10, max_num=18, can_delete=True, form=CreateJobForm, fields=('job_location','job_shift','start_time','end_time','order','pick','blow','sweep'))
ScheduleFormSet = formset_factory(ScheduleForm, max_num=5)
ScheduleFormSetModel = modelformset_factory(models.Shift, exclude=(), extra=0, max_num=10)
