from django.views.generic import TemplateView, FormView
from django.shortcuts import render, HttpResponseRedirect, reverse
from . import forms


class ThanksPage(TemplateView):
    template_name = 'thanks.html'

class HomePage(FormView):
    template_name = 'index.html'
    form_class = forms.DateForm

    def post(self,request,*args,**kwargs):
        if request.method == 'POST':
            form = forms.DateForm(request.POST)
            if form.is_valid():
                return HttpResponseRedirect(reverse('shifts:job_costing', kwargs={'begin':form.cleaned_data['begin'], 'end':form.cleaned_data['end'], 'full':0}))
            else:
                return render(request,'work/shift_list.html',{'form':form})
