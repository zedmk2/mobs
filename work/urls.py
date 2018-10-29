# WORK URLS.PY
from django.urls import include, path, re_path as url
from . import views
from rest_framework import routers

app_name = 'shifts'

router = routers.DefaultRouter()
# router.register(r'props', views.PropertyViewSet,base_name='property')
# router.register(r'shiftz', views.ShiftViewSet,base_name='shift')

urlpatterns = [
    url(r'^new/$',views.CreateShift.as_view(),name='create'),

    path('date/<date_summary>/',views.DateSummary.as_view(),name='date_summary'),
    path('update/<pk>/',views.UpdateShift.as_view(),name='update'),
    path('shift/<pk>/',views.ViewShift.as_view(),name='single_shift'),
    path('pdfshift/<pk>/',views.PdfShift.as_view(),name='pdf_shift'),

    url(r'^batch_shift/',views.batch_shift,name='batchshift'),

    url(r'^allshifts/$',views.ListShifts.as_view(),name='full'),
    url(r'^last30days_shifts/$',views.Last30ListShifts.as_view(),name='all'),
    path('next30shifts/',views.RecentListShifts.as_view(),name='next'),
    path('shiftsbetween/<begin>/<end>/',views.DateListShifts.as_view(),name='date_shift_list'),
    path('calendar/',views.CalendarLast30ListShifts.as_view()   ,name='calendar'),

    path('job/<pk>/',views.UpdateJob.as_view(),name='update_job'),

    path('routes/',views.RouteList.as_view(),name='route_list'),

    path('payroll_list/',views.payroll_list,name='payroll_list'),
    path('payroll/<begin>/<end>/',views.payroll,name='payroll'),
    path('payroll_full/<begin>/<end>/',views.payroll_full,name='payroll_full'),

    path('job_costing/<full>/<begin>/<end>/',views.job_costing,name='job_costing'),
    path('job_list/<full>/<begin>/<end>/',views.job_list,name='job_list'),

    path('week_schedule/<begin>/<end>/',views.WeekSchedule.as_view(),name='week_schedule'),
    path('property_schedule/',views.PropertySchedule.as_view(),name='property_schedule'),
    path('property_list/',views.PropertyList.as_view(),name='properties'),
    path('property/<pk>/',views.UpdateProperty.as_view(),name='update_property'),

    path('property_checks/<int:priority>/',views.InspectionList.as_view(),name='inspections'),
    path('inspection/<pk>/',views.UpdateInspection.as_view(),name='inspection_update'),
    path('new_inspection/',views.CreateInspection.as_view(),name='new_inspection'),
    path('new_inspection/<pk>/',views.CreateInspection.as_view(),name='new_inspection_pk'),

    path('qb/properties/<begin>/<end>/',views.QB_PropertyView.as_view(),name='property-list'),
    path('qb/shifts/<begin>/<end>/',views.QB_ShiftView.as_view(),name='property-list'),
    url(r'^api/', include(router.urls)),
]
