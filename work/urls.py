# WORK URLS.PY
from django.urls import  path, re_path as url
from . import views

app_name = 'shifts'

urlpatterns = [
    path('test/',views.test,name='test'),

    url(r'^new/$',views.CreateShift.as_view(),name='create'),

    path('detail/<pk>/',views.SingleShift.as_view(),name='detail'),
    path('date/<date_summary>/',views.DateSummary.as_view(),name='date_summary'),
    path('update/<pk>/',views.UpdateShift.as_view(),name='update'),

    url(r'^batch_shift/',views.batch_shift,name='batchshift'),

    url(r'^allshifts/$',views.ListShifts.as_view(),name='full'),
    url(r'^last30days_shifts/$',views.Last30ListShifts.as_view(),name='all'),
    path('shiftsbetween/<begin>/<end>/',views.DateListShifts.as_view(),name='date_shift_list'),

    path('properties/',views.ListProperties.as_view(),name='properties_list'),

    path('payroll_list/',views.payroll_list,name='payroll_list'),
    path('payroll/<begin>/<end>/',views.payroll,name='payroll'),

    path('job_costing/<begin>/<end>/',views.job_costing,name='job_costing'),

    path('week_schedule/<begin>/<end>/',views.WeekSchedule.as_view(),name='week_schedule'),

    path('property_checks/',views.InspectionList.as_view(),name='inspections'),
    path('inspection/<pk>/',views.UpdateInspection.as_view(),name='inspection_update'),
    path('new_inspection/',views.CreateInspection.as_view(),name='new_inspection'),
    path('new_inspection/<pk>/',views.CreateInspection.as_view(),name='new_inspection_pk'),

]
