import os
import time, calendar
from collections import defaultdict
from django.shortcuts import render, render_to_response, HttpResponseRedirect
from django.contrib.auth import get_user_model
User = get_user_model()

from django.contrib.auth.mixins import (LoginRequiredMixin,
                                        PermissionRequiredMixin)
from django.contrib.auth.decorators import login_required
# Create your views here.
from django.conf import settings
from django.db.models import Prefetch
from django.urls import reverse, reverse_lazy
from django.templatetags.static import static
from django.contrib.staticfiles.storage import staticfiles_storage
from django.utils import timezone
from django.http import Http404, FileResponse, HttpResponse
from django.views import generic
from work.models import Shift, Job, Property, Employee, Inspection, Route
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.db import IntegrityError, transaction
from django.db.models import Count, Sum, Avg
from easy_pdf.views import PDFTemplateView, PDFTemplateResponseMixin
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Frame, PageTemplate, Paragraph, Image
from reportlab.lib.styles import ParagraphStyle

import datetime
from io import BytesIO

from braces.views import SelectRelatedMixin

from django import forms
from django.forms import formsets, inlineformset_factory

from . import models
from . import forms

from rest_framework import viewsets, mixins, generics
from work.serializers import PropertySerializer, JobSerializer, ShiftSerializer

#########CREATE NEW SHIFT AND JOBS #####################

class CreateShift(LoginRequiredMixin, generic.CreateView):
    model = Shift

    form_class = forms.CreateShiftForm
    success_url = reverse_lazy('shifts:all')

    def get(self,request,*args,**kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        job_form = forms.JobsInlineFormset(instance=self.object)
        return self.render_to_response(
            self.get_context_data(shift_form=form,
                                  formset=job_form))

    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        job_form = forms.JobsInlineFormset(self.request.POST, instance=self.object)
        if form.is_valid() and job_form.is_valid():
            return self.form_valid(form, job_form)
        else:
            return self.form_invalid(form, job_form)

    def form_valid(self, form, job_form):
        self.object = form.save()
        job_form.instance = self.object
        job_form.save()
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, job_form):
        return self.render_to_response(
            self.get_context_data(shift_form=form,
                                  formset=job_form))

#########UPDATE A PARTICULAR SHIFT AND JOB #####################

class DateSummary(generic.ListView):
    model = Shift
    template_name = 'work/date_summary.html'

    def get_queryset(self, **kwargs):
        sel_date = self.kwargs['date_summary']
        return Shift.objects.filter(date=sel_date).prefetch_related('jobs_in_shift').prefetch_related('driver').prefetch_related('helper').prefetch_related('jobs_in_shift__job_location')

class ViewShift(LoginRequiredMixin,generic.DetailView):
    model = Shift

class PdfShift(generic.DetailView):
    model = Shift

    def get(self,request,*args,**kwargs):
        self.object = self.get_object()
        shift = self.object
        response = pdf_build(shift)
        return response

    def get_queryset(self):
        """
        Return the `QuerySet` that will be used to look up the object.
        This method is called by the default implementation of get_object() and
        may not be called if get_object() is overridden.
        """
        if self.queryset is None:
            if self.model:
                return self.model._default_manager.all().prefetch_related('driver').prefetch_related('helper').prefetch_related('jobs_in_shift').prefetch_related('jobs_in_shift__job_location')
            else:
                raise ImproperlyConfigured(
                    "%(cls)s is missing a QuerySet. Define "
                    "%(cls)s.model, %(cls)s.queryset, or override "
                    "%(cls)s.get_queryset()." % {
                        'cls': self.__class__.__name__
                    }
                )
        return self.queryset.all()

class UpdateShift(LoginRequiredMixin,generic.UpdateView):
    model = Shift
    form_class = forms.CreateShiftForm
    success_url = reverse_lazy('shifts:all')
    template_name_suffix = '_form'

    def get(self,request,*args,**kwargs):
        self.object = self.get_object()
        queryset = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        job_form = forms.JobsInlineFormset(instance=self.object)
        return self.render_to_response(
            self.get_context_data(shift_form=form,
                                  formset=job_form,
                                  obj=queryset))

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        job_form = forms.JobsInlineFormset(self.request.POST, instance=self.object)
        if form.is_valid() and job_form.is_valid():
            return self.form_valid(form, job_form)
        else:
            return self.form_invalid(form, job_form)

    def form_valid(self, form, job_form):
        self.object = form.save()
        job_form.instance = self.object
        job_form.save()
        pdf_build(self.object)
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, job_form):
        return self.render_to_response(
            self.get_context_data(shift_form=form,
                                  formset=job_form))

##########VIEW TO CREATE MULTIPLE SHIFTS AT ONCE (PAYROLL)################

@login_required
def batch_shift(request):
    ShiftFormSet = formsets.formset_factory(forms.CreateShiftForm,extra=4, max_num=18)

    if request.method == 'POST':
        shift_form = ShiftFormSet(request.POST)
        if shift_form.is_valid():
            for form_here in shift_form:
                if form_here.is_valid():
                    form_here.save()
            return HttpResponseRedirect('/work/next30shifts/')
    else:
        shift_form = ShiftFormSet()

    context = {'shift_form_fact':shift_form,}

    return render(request,'work/batch_shift_form.html',context)

###############################
### VIEW VIEWS #########

class ListShifts(LoginRequiredMixin,generic.ListView):
    queryset = Shift.objects.prefetch_related('driver').prefetch_related('helper').prefetch_related('jobs_in_shift')

    date_form = forms.DateForm()

    def post(self,request,*args,**kwargs):
        if request.method == 'POST':
            date_form = forms.DateForm(request.POST)
            if date_form.is_valid():
                return HttpResponseRedirect(reverse('shifts:date_shift_list', kwargs={'begin':date_form.cleaned_data['begin'], 'end':date_form.cleaned_data['end']}))
            else:
                return render(request,'work/shift_list.html',{'date_form':date_form})

    def get_context_data(self, **kwargs):
        date_form = forms.DateForm()
        context = super().get_context_data(**kwargs)
        context['date_form'] = date_form
        return context

class Last30ListShifts(ListShifts):
    def get_queryset(self):
        begin = datetime.date.today() - datetime.timedelta(days=30)
        end = datetime.date.today()
        return Shift.objects.filter(date__gte=begin).filter(date__lte=end).prefetch_related('driver').prefetch_related('helper').prefetch_related('jobs_in_shift')

class RecentListShifts(ListShifts):
    def get_queryset(self):
        begin = datetime.date.today() - datetime.timedelta(days=60)
        end = datetime.date.today() + datetime.timedelta(days=30)
        return Shift.objects.filter(date__gte=begin).filter(date__lte=end).prefetch_related('driver').prefetch_related('helper').prefetch_related('jobs_in_shift')

class CalendarLast30ListShifts(ListShifts):
    def get_queryset(self):
        begin = datetime.date.today() - datetime.timedelta(days=60)
        end = datetime.date.today() + datetime.timedelta(days=30)
        return Shift.objects.filter(date__gte=begin).filter(date__lte=end).prefetch_related('driver').prefetch_related('helper').prefetch_related('jobs_in_shift')

        def get_context_data(self, *, object_list=None, **kwargs):
            """Get the context for this view."""
            queryset = object_list if object_list is not None else self.object_list
            page_size = self.get_paginate_by(queryset)
            context_object_name = self.get_context_object_name(queryset)
            if page_size:
                paginator, page, queryset, is_paginated = self.paginate_queryset(queryset, page_size)
                context = {
                    'paginator': paginator,
                    'page_obj': page,
                    'is_paginated': is_paginated,
                    'object_lit': queryset,
                    'poop':'poop',
                }
            else:
                context = {
                    'paginator': None,
                    'page_obj': None,
                    'is_paginated': False,
                    'object_lit': queryset,
                    'poop':'poop',
                }
            if context_object_name is not None:
                context[context_object_name] = queryset
            context.update(kwargs)
            return super().get_context_data(**context)

    template_name = 'work/calendar.html'

class DateListShifts(LoginRequiredMixin,generic.ListView):
    template_name = 'work/shift_list.html'
    context_object_name = 'shift_list'

    date_form = forms.DateForm()

    def get_queryset(self):
        return Shift.objects.filter(date__gte=self.kwargs['begin']).filter(date__lte=self.kwargs['end']).prefetch_related('driver').prefetch_related('helper').prefetch_related('jobs_in_shift')

    def post(self,request,*args,**kwargs):
        if request.method == 'POST':
            date_form = forms.DateForm(request.POST)
            if date_form.is_valid():
                return HttpResponseRedirect(reverse('shifts:date_shift_list', kwargs={'begin':date_form.cleaned_data['begin'], 'end':date_form.cleaned_data['end']}))

    def get_context_data(self, **kwargs):
        date_form = forms.DateForm()
        context = super().get_context_data(**kwargs)
        context['date_form'] = date_form
        context['class'] = 'jQUIAccordion2'
        return context

class ListProperties(LoginRequiredMixin,generic.ListView):
    template_name = 'work/property_list.html'
    context_object_name = 'property_list'
    model = Property

class RouteList(generic.ListView):
    model = Route
    date_form = forms.DateForm()

    def get_queryset(self):
        return Route.objects.filter(type='weekly').prefetch_related('driver').prefetch_related('job_route').prefetch_related('job_route__route_location')

    def get_context_data(self, **kwargs):
        date_form = forms.DateForm()
        context = super().get_context_data(**kwargs)
        context['date_form'] = date_form
        return context

    def post(self, request, *args, **kwargs):
        form = forms.DateForm(request.POST)
        if form.is_valid():
            route_list = Route.objects.filter(type='weekly')
            dates = []
            d1 = form.cleaned_data['begin']
            d2 = form.cleaned_data['end']
            # this will give you a list containing all of the dates
            dd = [d1 + datetime.timedelta(days=x) for x in range((d2-d1).days + 1)]
            # print("You want to update the following dates: "+str(dates))
            for d in dd:
                # print(d)
                for route in route_list:
                    if d.weekday()==int(route.weekday):
                        shift, bool = Shift.objects.get_or_create(date=d,driver=route.driver,day_num=route.route_num)
                        if bool:
                            for prop in route.job_route.all():
                                # print(prop)
                                if prop.freq == 'even':
                                    if d.isocalendar()[1] %2 == 0:
                                        shift.jobs_in_shift.get_or_create(job_location=prop.route_location,order=prop.order)
                                elif prop.freq == 'odd':
                                    if d.isocalendar()[1] %2 == 1:
                                        shift.jobs_in_shift.get_or_create(job_location=prop.route_location,order=prop.order)
                                else:
                                    shift.jobs_in_shift.get_or_create(job_location=prop.route_location,order=prop.order)
                            print("Created shift for %s %s" % (d,route.driver))
                            pdf_build(shift)
                        else:
                            print("Retrieved shift for %s %s" % (d,route.driver))
            return HttpResponseRedirect('/work/next30shifts/')
        else:
            return HttpResponseRedirect('/work/next30shifts/')

class OtherRouteList(generic.ListView):
    model = Route
    date_form = forms.QDateForm()
    route_form = forms.RouteSelectForm()
    template_name = "work/route_list_2.html"

    def get_queryset(self):
        return Route.objects.filter(type='commercial').prefetch_related('driver').prefetch_related('job_route').prefetch_related('job_route__route_location')

    def get_context_data(self, **kwargs):
        date_form = forms.QDateForm()
        route_form = forms.RouteSelectForm()
        context = super().get_context_data(**kwargs)
        context['date_form'] = date_form
        context['route_form'] = route_form
        return context

    def post(self, request, *args, **kwargs):
        form = forms.QDateForm(request.POST)
        route_form = forms.RouteSelectForm(request.POST)
        if form.is_valid() and route_form.is_valid():
            route_list = Route.objects.filter(type='weekly')
            route = route_form.cleaned_data['route_select']
            date = form.cleaned_data['begin']
            shift, bool = Shift.objects.get_or_create(date=date,driver=route.driver,day_num=route.route_num)
            if bool:
                for prop in route.job_route.all():
                    # print(prop)
                    shift.jobs_in_shift.get_or_create(job_location=prop.route_location,order=prop.order)
                print("Created shift for %s %s" % (date,route.driver))
                pdf_build(shift)
            else:
                print("Retrieved shift for %s %s" % (date,route.driver))
            return HttpResponseRedirect(reverse('shifts:update', args=[shift.pk]))
        else:
            return HttpResponseRedirect('/work/other_routes/')

##############VIEWS FOR PAYROLL REPORTS
@login_required
def payroll_list(request):
    today = datetime.datetime.now()

    ##0 = Monday, 1 = Tuesday, etc...
    weekday = 0

    def next_weekday(d, weekday):
        days_ahead = weekday - d.weekday()
        if days_ahead <  0: # Target day already happened this week
            days_ahead += 7
        return d + datetime.timedelta(days_ahead)

    next_tue = next_weekday(today,weekday).date()
    prev_day = next_tue - datetime.timedelta(days=6)
    week_list = []
    for i in range(7):
        next_tue = next_tue - datetime.timedelta(days=(7))
        prev_day = prev_day - datetime.timedelta(days=(7))
        week_list.append((next_tue,prev_day))

    date_form = forms.DateForm()
    if request.method == 'POST':
        date_form = forms.DateForm(request.POST)
        if date_form.is_valid():
            return HttpResponseRedirect(reverse('shifts:payroll', args=[date_form.cleaned_data['begin'], date_form.cleaned_data['end']]))

    context = {'today':today,'next_tue':next_tue,'prev_day':prev_day,'week_list':week_list, 'date_form':date_form}
    return render(request,'work/payroll_list.html',context)


@login_required
def payroll_full(request,begin,end):
    begin = begin
    end = end
    begin_str = str(begin)
    end_str = str(end)
    shift = Shift.objects.filter(date__gte=begin).filter(date__lte=end).prefetch_related('jobs_in_shift').select_related('driver').prefetch_related('helper').prefetch_related('jobs_in_shift__job_shift').prefetch_related('jobs_in_shift__job_location')
    shift_list = []
    hr_total_pairs = []
    hr_totals = defaultdict(int)
    for i in shift:
        if i.helper == None:
            shift_list.append({'date':str(i.date),'driver':i.driver.name,'length':i.shift_length()})
        elif i.helper_2 == None:
            shift_list.append({'date':str(i.date),'driver':i.driver.name,'length':i.shift_length(),'helper':i.helper.name,'he_length':i.help_length()})
        else:
            shift_list.append({'date':str(i.date),'driver':i.driver.name,'length':i.shift_length(),'helper':i.helper.name,'helper_2':i.helper_2.name,'he_length':i.help_length(),'he_2_length':i.help_2_length()})

    employee = Employee.objects.filter(em_uid__gte=100).filter(em_uid__lte=300).exclude(end_date__lte=end).prefetch_related('sh_driver').prefetch_related('sh_helper').prefetch_related('sh_helper_2')

    emp_mix =[]
    i=0
    for emp in employee:
        emp_mix.append({'employee':"",'jobs':"",'total':""})
        emp2 = emp
        emp_mix[i]['employee'] = emp.name
        emp_mix[i]['jobs'] = emp.sh_driver.filter(date__gte=begin).filter(date__lte=end).annotate(Count('date')) | emp.sh_helper.filter(date__gte=begin).filter(date__lte=end).annotate(Count('date')) | emp.sh_helper_2.filter(date__gte=begin).filter(date__lte=end).annotate(Count('date'))
        dr_sh = emp.sh_driver.filter(date__gte=begin).filter(date__lte=end).annotate(Count('date'))
        he_sh = emp.sh_helper.filter(date__gte=begin).filter(date__lte=end).annotate(Count('date'))
        he_2_sh = emp.sh_helper_2.filter(date__gte=begin).filter(date__lte=end).annotate(Count('date'))
        iter1 = dr_sh | he_sh | he_2_sh
        iter2 = list(iter1)
        if iter2 == []:
            emp_mix[i]['total']=0
        else:
            l=0
            for k in range(len(iter2)):
                if emp.name == iter2[k].driver.name:
                    l += iter2[k].shift_length()
                elif emp.name == iter2[k].helper.name:
                    l += iter2[k].help_length()
                elif emp.name == iter2[k].helper_2.name:
                    l += iter2[k].help_2_length()
            emp_mix[i]['total'] = round(l,2)
        i=i+1

    context = {'temp':{},'emp_mix':emp_mix,'shift_list':shift_list,'shift':shift,'begin':begin_str,'end':end_str}
    return render(request,'work/payroll_full.html',context)

@login_required
def payroll(request,begin,end):
    begin = begin
    end = end
    begin_str = str(begin)
    end_str = str(end)
    total_hours = 0

    d1 = datetime.datetime.strptime(begin_str,'%Y-%m-%d').date()
    d2 = datetime.datetime.strptime(end_str,'%Y-%m-%d').date()

    # this will give you a list containing all of the dates
    dd = [d1 + datetime.timedelta(days=x) for x in range((d2-d1).days + 1)]

    employee = Employee.objects.filter(em_uid__gte=100).filter(em_uid__lte=300).exclude(end_date__lte=end).prefetch_related('sh_driver').prefetch_related('sh_helper').prefetch_related('sh_helper_2')

    emp_mix =[]
    i=0
    for emp in employee:
        emp_mix.append({'employee':"",'jobs':"",'shifts':"",'total':""})
        emp2 = emp
        emp_mix[i]['employee'] = emp.name
        dr_sh = emp.sh_driver.filter(date__gte=begin).filter(date__lte=end).annotate(Count('date'))
        he_sh = emp.sh_helper.filter(date__gte=begin).filter(date__lte=end).annotate(Count('date'))
        he_2_sh = emp.sh_helper_2.filter(date__gte=begin).filter(date__lte=end).annotate(Count('date'))
        iter1 = dr_sh | he_sh | he_2_sh

        emp_mix[i]['jobs'] = iter1
        iter2 = list(iter1)
        iter4 = []
        if iter2 == []:
            emp_mix[i]['total']=0
        else:
            l=0
            for k in range(len(iter2)):
                if emp.name == iter2[k].driver.name:
                    l += iter2[k].shift_length()
                elif emp.name == iter2[k].helper.name:
                    l += iter2[k].help_length()
                elif emp.name == iter2[k].helper_2.name:
                    l += iter2[k].help_2_length()
            emp_mix[i]['total'] = round(l,2)

        for k in range(len(dd)):
            iter4.append(0)
            for j in range(len(iter2)):
                if dd[k] == iter2[j].date:
                    if emp.name == iter2[j].driver.name:
                        iter4[k]= iter2[j].shift_length()
                    elif emp.name == iter2[j].helper.name:
                        iter4[k]= iter2[j].help_length()
                    elif emp.name == iter2[j].helper_2.name:
                        iter4[k]= iter2[j].help_2_length()

        emp_mix[i]['shifts'] = iter4
        i=i+1
    for i in range(len(emp_mix)):
        total_hours += emp_mix[i]['total']
    total_hours = round(total_hours,2)

    context = {'emp_mix':emp_mix,'dates':dd,'total_hours':total_hours,'begin':begin_str,'end':end_str}
    return render(request,'work/payroll.html',context)


################VIEW FOR JOB COSTING

@login_required
def job_costing(request, begin, end,full):
    shift_set = Shift.objects.filter(date__gte=begin).filter(date__lte=end).select_related('driver').select_related('helper').select_related('helper_2')
    job_set = Job.objects.filter(job_shift__date__gte=begin).filter(job_shift__date__lte=end).prefetch_related(Prefetch('job_shift',queryset=shift_set))
    property_set = Property.objects.filter(job_costing_report_include=True).order_by('client_name', 'display_name').prefetch_related(Prefetch('location',queryset=job_set,to_attr='jobs')).prefetch_related(Prefetch('location__job_location__client_name'))
    if full == 'all':
        property_set = Property.objects.order_by('client_name', 'display_name').prefetch_related(Prefetch('location',queryset=job_set,to_attr='jobs')).prefetch_related(Prefetch('location__job_location__client_name'))
    # will want to replace **TK** price with calculation for hourly cost
    price = 53
    for p in property_set:
        p.job_num = 0
        p.job_total = 0
        p.job_avg = 0
        p.cost_total = 0
        p.sw_total_price = 0
        p.a_dph_sum = 0
        for j in p.jobs:
            p.job_num += 1
            p.job_total += j.job_length
            j.job_cost = j.job_length * price
            p.cost_total += j.job_cost
        try:
            p.job_avg = p.job_total / p.job_num
        except:
            p.job_avg = 0
        if not p.sw_price and p.sw_mo_price:
            try:
                p.sw_price = p.sw_mo_price / p.job_num
            except ZeroDivisionError:
                p.sw_price = 0
        if p.sw_price:
                p.sw_total_price = p.sw_price * p.job_num
        for j in p.jobs:
            j.e_dph = ""
            try:
                j.a_dph = p.sw_price/j.job_length
                p.a_dph_sum += j.a_dph
            except:
                j.a_dph = 0
        try:
            p.a_dph_avg = p.a_dph_sum / p.job_num
        except:
            p.a_dph_avg = 0

    month = datetime.datetime.strptime(begin,'%Y-%m-%d').strftime('%B %Y')

    context = {'prop':property_set,'job':job_set,'month':month,'begin':begin,'end':end, 'full':full}

    return render(request,'work/job_costing.html',context)

def job_list(request, begin, end,full):
    shift_set = Shift.objects.filter(date__gte=begin).filter(date__lte=end).select_related('driver').select_related('helper').select_related('helper_2')
    job_set = Job.objects.filter(job_shift__date__gte=begin).filter(job_shift__date__lte=end).prefetch_related(Prefetch('job_shift',queryset=shift_set))
    property_set = Property.objects.filter(job_costing_report_include=True).order_by('client_name', 'display_name').prefetch_related(Prefetch('location',queryset=job_set,to_attr='jobs')).prefetch_related(Prefetch('location__job_location__client_name'))
    if full == 'all':
        property_set = Property.objects.order_by('client_name', 'display_name').prefetch_related(Prefetch('location',queryset=job_set,to_attr='jobs')).prefetch_related(Prefetch('location__job_location__client_name'))
    # will want to replace **TK** price with calculation for hourly cost
    price = 53
    for p in property_set:
        p.job_num = 0
        p.job_total = 0
        p.job_avg = 0
        p.cost_total = 0
        p.sw_total_price = 0
        p.a_dph_sum = 0
        for j in p.jobs:
            p.job_num += 1
            p.job_total += j.job_length
            j.job_cost = j.job_length * price
            p.cost_total += j.job_cost
        try:
            p.job_avg = p.job_total / p.job_num
        except:
            p.job_avg = 0
        if not p.sw_price and p.sw_mo_price:
            try:
                p.sw_price = p.sw_mo_price / p.job_num
            except ZeroDivisionError:
                p.sw_price = 0
        if p.sw_price:
                p.sw_total_price = p.sw_price * p.job_num
        for j in p.jobs:
            j.e_dph = ""
            try:
                j.a_dph = p.sw_price/j.job_length
                p.a_dph_sum += j.a_dph
            except:
                j.a_dph = 0
        try:
            p.a_dph_avg = p.a_dph_sum / p.job_num
        except:
            p.a_dph_avg = 0

    month = datetime.datetime.strptime(begin,'%Y-%m-%d').strftime('%B %Y')

    context = {'prop':property_set,'job':job_set,'month':month,'begin':begin,'end':end}

    return render(request,'work/job_list.html',context)

#I dont know why the Prefetch thing works
class QB_PropertyView(generics.ListCreateAPIView):
    def get_queryset(self,**kwargs):
        begin = self.kwargs['begin']
        end = self.kwargs['end']
        shift_set = Shift.objects.filter(date__gte=begin).filter(date__lte=end).select_related('driver').select_related('helper').select_related('helper_2')
        job_set = Job.objects.filter(job_shift__date__gte=begin).filter(job_shift__date__lte=end).prefetch_related(Prefetch('job_shift',queryset=shift_set))
        queryset = Property.objects.filter(job_costing_report_include=True).order_by('client_name', 'display_name').prefetch_related(Prefetch('location',queryset=job_set,)).prefetch_related(Prefetch('location__job_location__client_name'))

        return queryset

    serializer_class = PropertySerializer

class QB_ShiftView(generics.ListCreateAPIView):
    def get_queryset(self,**kwargs):
        begin = self.kwargs['begin']
        end = self.kwargs['end']
        queryset = Job.objects.filter(job_shift__date__gte=begin).filter(job_shift__date__lte=end).prefetch_related('job_shift','job_location')
        return queryset

    serializer_class = JobSerializer

################ SCHEDULE VIEWS ##############

class WeekSchedule(generic.ListView):
    def get_queryset(self):
        # self.driver = get_object_or_404(Employee, name=self.kwargs['driver'])
        qs = Shift.objects.order_by("date").filter(date__gte=self.kwargs['begin']).filter(date__lte=self.kwargs['end']).prefetch_related('driver').prefetch_related('helper')
        return qs

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        allow_empty = self.get_allow_empty()
        if not allow_empty:
            # When pagination is enabled and object_list is a queryset,
            # it's better to do a cheap query than to load the unpaginated
            # queryset in memory.
            if self.get_paginate_by(self.object_list) is not None and hasattr(self.object_list, 'exists'):
                is_empty = not self.object_list.exists()
            else:
                is_empty = len(self.object_list) == 0
            if is_empty:
                raise Http404(_("Empty list and '%(class_name)s.allow_empty' is False.") % {
                    'class_name': self.__class__.__name__,
                })
        context = self.get_context_data()

        employees = Employee.objects.filter(driver=True) | Employee.objects.filter(helper=True)
        employee_list = [employee.name for employee in employees]

        queryset = [q for q in self.object_list]

        temp = [q.date for q in self.object_list]
        temp2 = [self.kwargs['begin'],self.kwargs['end']]
        d1 = datetime.datetime.strptime(self.kwargs['begin'],'%Y-%m-%d')
        d2 = datetime.datetime.strptime(self.kwargs['end'],'%Y-%m-%d')
        # this will give you a list containing all of the dates
        dd = [(d1 + datetime.timedelta(days=x)).date() for x in range((d2-d1).days + 1)]

        date_range = {key: [] for key in sorted(dd)}

        for key,value in date_range.items():
            for i in queryset:
                if key == i.date:
                    date_range[key].append(i)

        form_date = [{'driver':q.driver,'helper':q.helper,'date':q.date} for q in queryset]
        ScheduleFormSet = formsets.formset_factory(forms.ScheduleForm,extra=4,max_num=5)
        formset = ScheduleFormSet(initial=form_date)


        extra_context = {'form_date':form_date,'temp':dd,'date_range':date_range,'queryset':queryset,'employees':employee_list,'kwargs':kwargs,'formset':formset}
        full_context = {**context, **extra_context}
        return self.render_to_response(full_context)

    template_name = "work/schedule.html"

def days_in_month(today):
        first_of_month = today.replace(day=1)
        end_of_month_number =  calendar.monthrange(today.year, today.month)[1]
        end_of_month = today.replace(day=end_of_month_number)
        list_days = [first_of_month + datetime.timedelta(days=x) for x in range((end_of_month - first_of_month).days + 1)]
        days_dict = {"M":0,"T":0,"W":0,"R":0,"F":0,"S":0,"U":0}
        dict = defaultdict(int)
        for day in list_days:
            dict[day.weekday()] += 1
        days_dict["M"] = dict[0]
        days_dict["T"] = dict[1]
        days_dict["W"] = dict[2]
        days_dict["R"] = dict[3]
        days_dict["F"] = dict[4]
        days_dict["S"] = dict[5]
        days_dict["U"] = dict[6]

        return days_dict

class PropertySchedule(generic.ListView):
    def get_queryset(self):
        qs = Property.objects.filter(check_priority=1)
        return qs

    def get(self, request, *args, **kwargs):
        prop_list = qs = Property.objects.filter(check_priority=1)
        self.object_list = self.get_queryset()
        context = self.get_context_data()

        today = datetime.date.today()
        first_of_month = today.replace(day=1)
        end_of_month_number =  calendar.monthrange(today.year, today.month)[1]
        end_of_month = today.replace(day=end_of_month_number)

        days_dict = days_in_month(today)

        prev_shifts = Shift.objects.order_by("date").filter(date__gte=first_of_month).filter(date__lt=today).prefetch_related('jobs_in_shift').prefetch_related('jobs_in_shift__job_location').prefetch_related('driver').prefetch_related('helper')
        remaining_shifts = Shift.objects.order_by("date").filter(date__gte=today).filter(date__lte=end_of_month).prefetch_related('jobs_in_shift').prefetch_related('jobs_in_shift__job_location').prefetch_related('driver').prefetch_related('helper')
        record = {}
        record_2 = {}

        for s in prev_shifts:
            s1 = 0
            for j in s.jobs_in_shift.all():
                if j.job_location.name in record:
                    record[j.job_location.name] += 1
                else:
                    record[j.job_location.name] = 1

        for s in remaining_shifts:
            s1 = 0
            for j in s.jobs_in_shift.all():
                if j.job_location.name in record_2:
                    record_2[j.job_location.name] += 1
                else:
                    record_2[j.job_location.name] = 1

        for p in prop_list:
                p.month_target= 0
                if int(p.times_per_month or 0) > 0:
                    p.month_target = p.times_per_month
                elif int(p.times_per_week or 0) == 7:
                    p.month_target = end_of_month_number
                elif int(p.times_per_week or 0) >0 and type(p.days_of_week)!='NoneType':
                    for letter in str(p.days_of_week or ''):
                        p.month_target += days_dict[letter]
                else:
                    p.month_target = "NA"
                p.completed = record.get(p.name)
                p.remaining = record_2.get(p.name)
                p.difference_class = 'yellow'
                if p.month_target != "NA":
                    p.difference = int(p.month_target or 0) - int(p.completed or 0) - int(p.remaining or 0)
                    if p.difference > 0:
                        p.difference_class = 'blue'
                    elif p.difference < 0 :
                        p.difference_class = 'red'
                    else:
                        p.difference_class = 'grey'

        extra_context = {'prev_shifts':prev_shifts,'remaining_shifts':remaining_shifts,'record':record,'prop_list':prop_list}
        full_context = {**context, **extra_context}
        return self.render_to_response(full_context)

    template_name = "work/property_schedule.html"

################################################
###PROPERTY LIST
#############################################

class PropertyList(LoginRequiredMixin,generic.ListView):
    def get_queryset(self):
        queryset = Property.objects.prefetch_related('location').prefetch_related('location__job_shift').prefetch_related('location__job_shift__driver')
        for prop in queryset:
            prop.recent_jobs = []
            for loc in prop.location.all():
                prop.recent_jobs.append(loc)
            prop.recent_jobs = prop.recent_jobs[-3:]
        return queryset
    template_name = "work/property_list.html"

class UpdateProperty(LoginRequiredMixin,generic.UpdateView):
    model = Property
    form_class = forms.InspectionForm
    template_name_suffix = '_form'


################################################
###PROPERTY CHECKS
#############################################

class InspectionList(LoginRequiredMixin,generic.ListView):
    def get_queryset(self):
        priority = self.kwargs['priority']
        queryset = Property.objects.filter(check_priority__lte=priority).prefetch_related('inspection').order_by('county','name')
        for prop in queryset:
            for inspection in prop.inspection.all():
                inspection.days_since = (datetime.date.today() - inspection.date).days
            try:
                if prop.inspection.all()[0].days_since > (prop.check_interval*2):
                    prop.color = 'fas fa-exclamation-triangle'
                elif prop.inspection.all()[0].days_since > prop.check_interval:
                    prop.color = 'fas fa-clock'
                else:
                    prop.color = 'fas fa-check'
            except:
                prop.color = 'fas fa-question'
        return queryset
    template_name = "work/inspection_list.html"

class UpdateInspection(LoginRequiredMixin,generic.UpdateView):
    model = Inspection
    form_class = forms.InspectionForm
    def get_initial(self):
        initial = super(UpdateInspection,self).get_initial()
        initial['updated_by'] = self.request.user
        return initial

class CreateInspection(LoginRequiredMixin,generic.CreateView):
    model = Inspection
    form_class = forms.InspectionForm
    extra_context = {'today':datetime.datetime.today()}
    def get_initial(self):
        initial = super(CreateInspection,self).get_initial()
        initial['prop'] = self.kwargs['pk']
        initial['date'] = datetime.date.today()
        initial['created_by'] = self.request.user
        initial['updated_by'] = self.request.user
        return initial

    success_url = reverse_lazy('shifts:inspections',kwargs={'priority':1})

    ################################################
    ###JOBS CHECKS
    #############################################

class UpdateJob(LoginRequiredMixin,generic.UpdateView):
    model = Job
    form_class = forms.InspectionForm
    template_name_suffix = '_form'

#########################################################
#PDF Build#
#########################################################
def pdf_build(shift):
    string=str(shift)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename='+string
    buffer = BytesIO()
    width, height = letter
    # Start writing the PDF here
    p = SimpleDocTemplate(buffer, leftMargin=0.5*inch,rightMargin=0.5*inch,bottomMargin=0.5*inch,topMargin=0.5*inch,pagesize=landscape(letter))
    logo=os.path.join(settings.BASE_DIR,'static','mobs','ms.jpg')
    I = Image(logo,width=2.2*inch,height=1.2*inch)
    # container for the 'Flowable' objects
    elements = []
    # Header table
    data_h = [[I,shift.date.strftime('%A')+': '+shift.date.strftime('%b %d, %Y'),'',shift.driver,'Weather'],
                ['','Driver','Time in','Time out','Viento (Windy)',''],
                ['','Helper','Time in','Time out','Lloviendo (Rain)',''],
                ['','Lunch (Almuerzo)','Time in','Time out','Nieve (Snow)',''],
                ['','Truck #','Mileage in','Mileage out',''],]
    t_h = Table(data_h,rowHeights=[0.3*inch,0.3*inch,0.3*inch,0.3*inch,0.3*inch],colWidths=[3*inch,2*inch,2*inch,2*inch,1*inch,0.4*inch])
    t_h.setStyle(TableStyle([('GRID',(1,1),(3,4),1,colors.black),
                            ('GRID',(5,1),(5,3),1,colors.black),
                            ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
                           ('FONT',(0,1),(-1,-1),'Helvetica',8),
                           ('FONT',(0,0),(-1,0),'Helvetica-Bold',8),
                           ('SPAN',(0,0),(0,-1),
                           )]))
    #Property table
    data= [['Property', '#', 'Time', '','Sweep','', 'Blow','','','Pick','','','Trash','','Bulk','Dumpster'],
           ['','', 'In', 'Out', 'Front', 'Back', 'Front', 'Back', 'S/W', 'Front', 'Back', 'S/W', 'Empty', '# Bags','','%'],
                ]
    for job in shift.jobs_in_shift.all():
        style = ParagraphStyle('jobs',fontName='Helvetica',fontSize=8,borderPadding=(3,5,3,5))
        if job.job_location.color:
            style.backColor = str(job.job_location.color)
        text = str(job.job_location.display_name)
        # +'<br/>'+str(job.job_location.address)
        P = Paragraph(text,style)
        data.append([P, '', '', '', '', '', '', '', '', '', '', '', '', ''])
        if job.job_location.instructions:
            data.append([str(job.job_location.instructions), '', '', '', '', '', '', '', '', '', '', '', '', ''])
    #Table settings
    t=Table(data,colWidths=[3.0*inch,0.4*inch,0.85*inch,0.85*inch,0.5*inch,0.5*inch,0.4*inch,0.4*inch,0.4*inch,0.4*inch,0.4*inch,0.4*inch,0.5*inch,0.5*inch,0.45*inch,0.55*inch],spaceBefore=0.15*inch)
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.lemonchiffon),
                            ('ALIGN', (1, 0), (-1, 1), "CENTER"),
                            ('TOPPADDING',(0,2),(-1,-1),4),
                            ('BOTTOMPADDING',(0,2),(-1,-1),4),
                           ('GRID',(0,0),(-1,-1),1,colors.black),
                           ('FONT',(0,0),(-1,0),'Helvetica-Bold',8),
                           ('FONT',(0,1),(-1,-1),'Helvetica',8),
                           ('SPAN',(2,0),(3,0)),
                           ('SPAN',(4,0),(5,0)),
                           ('SPAN',(6,0),(8,0)),
                           ('SPAN',(9,0),(11,0)),
                           ('SPAN',(12,0),(13,0)),]))
    #Walmart
    data_2 = [  ['Walmart, Philadelphia Rd, Aberdeen','','',],
                ['Dial (516) 500-7776. Enter 1 for Eng or 9 for Espanol. Enter 316878#. Enter 00580672#. Enter # again. Hang up','Yes','No',],
                ['Dial (516) 500-7776. Enter 1 for Eng or 9 for Espanol. Enter 316878#. Enter 00580672#. Enter 4. Enter #. Enter 2. Enter #. Hang up.','Yes','No']]
    data_3 = [  ['Walmart, Baltimore National','','',],
                ['Dial (516) 500-7776. Enter 1 for Eng or 9 for Espanol. Enter 316878#. Enter 05326779#. Enter # again. Hang up.','Yes','No',],
                ['Dial (516) 500-7776. Enter 1 for Eng or 9 for Espanol. Enter 316878#. Enter 05326779#. Enter 4. Enter #. Enter 2. Enter #. Hang up.','Yes','No']]
    w_1 = Table(data_2,colWidths=[9.5*inch, 0.5*inch,0.5*inch],spaceBefore=0.15*inch)
    w_2 = Table(data_3,colWidths=[9.5*inch, 0.5*inch,0.5*inch],spaceBefore=0.15*inch)
    w_1.setStyle(TableStyle([('BACKGROUND',(1,1),(3,3),colors.lawngreen),
                           ('GRID',(0,1),(-1,-1),1,colors.black),
                           ('FONT',(0,0),(-1,-1),'Helvetica',8),
                           ('ALIGN',(-2,0),(-1,-1),'CENTER'),]))
    w_2.setStyle(TableStyle([('BACKGROUND',(1,1),(3,3),colors.lawngreen),
                           ('GRID',(0,1),(-1,-1),1,colors.black),
                           ('FONT',(0,0),(-1,-1),'Helvetica',8),
                           ('ALIGN',(-2,0),(-1,-1),'CENTER'),]))
    elements.append(t_h)
    elements.append(t)
    for job in shift.jobs_in_shift.all():
        if job.job_location.pk == 25:
            elements.append(w_1)
        if job.job_location.pk == 63:
            elements.append(w_2)
    # write the document to disk
    p.build(elements)
    # End writing
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    file_name = os.path.join(settings.MEDIA_ROOT,'routes',string+'.pdf')
    print('Generating file: '+file_name)
    with open(file_name, 'wb') as f:
        f.write(pdf)
    return response
