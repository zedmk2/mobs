from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.conf import settings
from django.utils.timezone import now
from django.utils.functional import cached_property

import datetime
# Create your models here.

from django.contrib.auth import get_user_model
User = get_user_model

from django import template
register = template.Library()

class Employee(models.Model):
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30,blank=True)
    name = models.CharField(max_length=30, unique=True)
    em_uid = models.IntegerField("Employee ID",unique=True)
    start_date = models.DateField(blank=True,null=True)
    end_date = models.DateField(blank=True,null=True)
    driver = models.BooleanField(default=False)
    helper = models.BooleanField(default=False)
    porter = models.BooleanField(default=False)
    hauler = models.BooleanField(default=False)

    class Meta:
        ordering = ["name",'-start_date']

    def __str__(self):
        return self.name

class Truck(models.Model):
    created_at = models.DateTimeField(auto_now=True)
    last_edited = models.DateTimeField(auto_now=True,blank=True,null=True)
    name = models.IntegerField()
    start_date = models.DateTimeField(blank=True,null=True)
    end_date = models.DateTimeField(blank=True,null=True)

    def __str__(self):
        return "%s" % (self.name)

class Client(models.Model):

    name = models.CharField(max_length=200, unique=True)
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=200)
    state  = models.CharField(max_length=200)
    zipcode = models.IntegerField()

    start_date = models.DateField(blank=True,null=True)
    end_date = models.DateField(blank=True,null=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

class Property(models.Model):
    name = models.CharField(max_length=200, unique=True)
    display_name = models.CharField(max_length=200)
    invoice_name = models.CharField(max_length=200,blank=True,null=True)

    property_contact = models.CharField(max_length=50, blank=True,null=True)
    bulk_contact = models.CharField(max_length=50, blank=True,null=True)
    billing_contact = models.CharField(max_length=50, blank=True,null=True)

    address = models.CharField(max_length=200, blank=True,null=True)
    city = models.CharField(max_length=200, blank=True,null=True)
    state  = models.CharField(max_length=200, blank=True,null=True)
    zipcode = models.IntegerField(blank=True,null=True)
    county = models.CharField(max_length=30,blank=True,null=True)

    client_name = models.ForeignKey(Client, on_delete=models.PROTECT,null=True)
    bi_address = models.CharField(max_length=200, blank=True,null=True)
    bi_city = models.CharField(max_length=200,blank=True,null=True)
    bi_state  = models.CharField(max_length=200,blank=True,null=True)
    bi_zipcode = models.IntegerField(blank=True,null=True)
    #Invoice data below (from QB)
    inv_type = models.CharField(max_length=2,default='SL')
    addr1 = models.CharField(max_length=200,blank=True,null=True)
    addr2 = models.CharField(max_length=200,blank=True,null=True)
    addr3 = models.CharField(max_length=200,blank=True,null=True)
    addr4 = models.CharField(max_length=200,blank=True,null=True)
    addr5 = models.CharField(max_length=200,blank=True,null=True)
    terms = models.CharField(max_length=30,blank=True,null=True)
    saddr1 = models.CharField(max_length=200,blank=True,null=True)
    saddr2 = models.CharField(max_length=200,blank=True,null=True)
    saddr3 = models.CharField(max_length=200,blank=True,null=True)
    saddr4 = models.CharField(max_length=200,blank=True,null=True)
    saddr5 = models.CharField(max_length=200,blank=True,null=True)
    tosend = models.CharField(max_length=2,default='N')
    memo = models.CharField(max_length=200,blank=True,null=True)
    adlspl = models.CharField(max_length=500,blank=True,null=True)

    start_date = models.DateField(blank=True,null=True)
    end_date = models.DateField(blank=True,null=True)

    sw_price = models.FloatField(blank=True,null=True)
    sw_mo_price = models.FloatField(blank=True,null=True)
    bu_price = models.FloatField(blank=True,null=True)
    po_price = models.FloatField(blank=True,null=True)

    times_per_week = models.IntegerField(blank=True,null=True)
    times_per_month = models.IntegerField(blank=True,null=True)
    times_per_year = models.IntegerField(blank=True,null=True)

    job_costing_report_include = models.BooleanField(default=True)

    check_priority = models.IntegerField()
    check_interval = models.IntegerField()

    class Meta:
        verbose_name_plural = "properties"
        ordering = ["display_name"]

    def __str__(self):
        return self.display_name

class Inspection(models.Model):
    created = models.DateTimeField(editable=False)
    updated = models.DateTimeField(editable=False)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,null=True,blank=True,related_name='created_by')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,null=True,blank=True,related_name='updated_by')
    prop = models.ForeignKey(Property, on_delete=models.PROTECT,null=True, related_name='inspection')
    date = models.DateField()
    rating = models.IntegerField(blank=True,null=True)
    description = models.TextField(blank=True,null=True)

    def save(self):
        if not self.id:
            self.created = datetime.datetime.now()
        self.updated = datetime.datetime.now()
        super(Inspection, self).save()

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return self.description

    def get_absolute_url(self):
        return reverse('shifts:inspection_update',kwargs={'pk':self.id} )

class Shift(models.Model):
    # user = models.ForeignKey(User,related_name='user_shifts')
    created_at = models.DateTimeField(auto_now_add=True)
    last_edited = models.DateTimeField(auto_now=True,blank=True,null=True)
    driver = models.ForeignKey(Employee,on_delete=models.PROTECT,related_name='sh_driver')
    helper = models.ForeignKey(Employee,on_delete=models.PROTECT,related_name='sh_helper',blank=True,null=True,)
    helper_2 = models.ForeignKey(Employee,on_delete=models.PROTECT,related_name='sh_helper_2',blank=True,null=True,)
    truck = models.IntegerField(blank=True,null=True)
    truck_new = models.ForeignKey(Truck,on_delete=models.PROTECT,related_name='truck',blank=True,null=True)

    date = models.DateField()

    dr_start_time = models.TimeField(blank=True,null=True, verbose_name="driver start time",)
    dr_end_time = models.TimeField(blank=True,null=True, verbose_name="driver end time",)
    he_start_time = models.TimeField(blank=True,null=True, verbose_name="helper start time",)
    he_end_time = models.TimeField(blank=True,null=True, verbose_name="helper end time",)
    he_2_start_time = models.TimeField(blank=True,null=True, verbose_name="second helper start time",)
    he_2_end_time = models.TimeField(blank=True,null=True, verbose_name="second helper end time",)

    def shift_length(self):
        "Calculates shift duration based on driver clock times"
        try:
            self.start = datetime.datetime(self.date.year,self.date.month,self.date.day,self.dr_start_time.hour,self.dr_start_time.minute,self.dr_start_time.second)
            if self.dr_end_time < self.dr_start_time:
                self.end = datetime.datetime(self.date.year,self.date.month,(self.date.day),self.dr_end_time.hour,self.dr_end_time.minute,self.dr_end_time.second)
                self.end = self.end + datetime.timedelta(days=1)
            else:
                self.end = datetime.datetime(self.date.year,self.date.month,self.date.day,self.dr_end_time.hour,self.dr_end_time.minute,self.dr_end_time.second)
            self.duration = self.end - self.start
            return (round(self.duration.seconds / 3600,2))
        except:
            return 0

    def help_length(self):
        "Calculates shift duration based on helper clock times; returns 0 if no helper time"
        try:
            self.start = datetime.datetime(self.date.year,self.date.month,self.date.day,self.he_start_time.hour,self.he_start_time.minute,self.he_start_time.second)
            if self.he_end_time < self.he_start_time:
                self.end = datetime.datetime(self.date.year,self.date.month,(self.date.day),self.he_end_time.hour,self.he_end_time.minute,self.he_end_time.second)
                self.end = self.end + datetime.timedelta(days=1)
            else:
                self.end = datetime.datetime(self.date.year,self.date.month,self.date.day,self.he_end_time.hour,self.he_end_time.minute,self.he_end_time.second)
            self.duration = self.end - self.start
            return (round(self.duration.seconds / 3600,2))
        except:
            return 0

    def help_2_length(self):
        "Calculates shift duration based on helper clock times; returns 0 if no helper time"
        try:
            self.start = datetime.datetime(self.date.year,self.date.month,self.date.day,self.he_2_start_time.hour,self.he_2_start_time.minute,self.he_2_start_time.second)
            if self.he_2_end_time < self.he_2_start_time:
                self.end = datetime.datetime(self.date.year,self.date.month,(self.date.day),self.he_2_end_time.hour,self.he_2_end_time.minute,self.he_2_end_time.second)
                self.end = self.end + datetime.timedelta(days=1)
            else:
                self.end = datetime.datetime(self.date.year,self.date.month,self.date.day,self.he_2_end_time.hour,self.he_2_end_time.minute,self.he_2_end_time.second)
            self.duration = self.end - self.start
            return (round(self.duration.seconds / 3600,2))
        except:
            return 0

    def __str__(self):
        return "%s %s" % (self.date, self.driver)
        # def save(self,*args,**kwargs):

    #     self.message_html= misaka.html(self.user)

    def get_absolute_url(self):
        return reverse('shifts:single',kwargs={'pk':self.pk})

    class Meta:
        unique_together = (("driver","date"),
                            )
        ordering = ['-date','driver']

class Work_Date:
    def __init__(self,date):
        self.date = date

class Job(models.Model):
    job_location = models.ForeignKey(Property,on_delete=models.PROTECT, related_name='location', null=True)
    job_shift = models.ForeignKey(Shift,on_delete=models.PROTECT,related_name='jobs_in_shift', null=True)
    start_time = models.TimeField(blank=True,null=True)
    end_time = models.TimeField(blank=True,null=True)
    sweep = models.NullBooleanField(blank=True,null=True)
    blow = models.NullBooleanField(blank=True,null=True)
    pick = models.NullBooleanField(blank=True,null=True)

    @property
    def date(self):
        return self.job_shift.date

    @property
    def job_length(self):
        "Calculates job duration based on clock times"
        self.start = datetime.datetime(self.date.year,self.date.month,self.date.day,self.start_time.hour,self.start_time.minute,self.start_time.second)
        if self.end_time < self.start_time:
            self.end = datetime.datetime(self.date.year,self.date.month,(self.date.day),self.end_time.hour,self.end_time.minute,self.end_time.second)
            self.end = self.end + datetime.timedelta(days=1)
        else:
            self.end = datetime.datetime(self.date.year,self.date.month,self.date.day,self.end_time.hour,self.end_time.minute,self.end_time.second)
        self.duration = self.end - self.start
        return (round(self.duration.seconds / 3600,2))

    def __str__(self):
        return "%s %s" % (self.job_location, self.job_shift)

    def get_absolute_url(self):
        return reverse('shifts:singlejob',kwargs={'pk':self.pk})

    class Meta:
        ordering = ["-job_shift"]
