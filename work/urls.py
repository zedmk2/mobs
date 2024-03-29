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
    path('week_summary/<begin>/<end>/',views.WeekSummary.as_view(),name='week_summary'),

    path('week_schedule/<begin>/<end>/',views.week_schedule,name='week_schedule'),

    path('update/<pk>/',views.UpdateShift.as_view(),name='update'),
    path('shift/<pk>/',views.ViewShift.as_view(),name='single_shift'),
    path('pdfshift/<pk>/',views.PdfShift.as_view(),name='pdf_shift'),

    url(r'^batch_shift/',views.batch_shift,name='batchshift'),

    url(r'^allshifts/$',views.RecentListShifts.as_view(),name='full'),
    url(r'^last30days_shifts/$',views.Last30ListShifts.as_view(),name='all'),
    path('next30shifts/',views.RecentListShifts.as_view(),name='next'),
    path('shiftsbetween/<begin>/<end>/',views.DateListShifts.as_view(),name='date_shift_list'),
    path('jobsbetween/<begin>/<end>/',views.DateListJobs.as_view(),name='date_job_list'),
    path('calendar/<int:year>/<int:month>/',views.Calendar.as_view(),name='calendar'),
    path('calendar/',views.Calendar.as_view(),name='calendar'),

    path('job/<pk>/',views.UpdateJob.as_view(),name='update_job'),

    path('routes/',views.RouteList.as_view(),name='route_list'),
    path('other_routes/',views.OtherRouteList.as_view(),name='other_route_list'),
    path('landscaping_routes/',views.LandscapingRouteList.as_view(),name='landscaping_route_list'),
    path('route_pricing/',views.RoutePricing.as_view(),name='route_pricing'),

    path('payroll_list/',views.payroll_list,name='payroll_list'),
    path('payroll/<begin>/<end>/',views.payroll,name='payroll'),
    path('payroll_full/<begin>/<end>/',views.payroll_full,name='payroll_full'),

    path('job_costing/<full>/<begin>/<end>/',views.job_costing,name='job_costing'),
    path('job_list/<full>/<begin>/<end>/',views.job_list,name='job_list'),

    path('property_checklist/',views.PropertySchedule.as_view(),name='property_checklist'),
    path('property_checklist/<date>/',views.PropertySchedule.as_view(),name='property_checklist_date'),
    path('annual_schedule/',views.AnnualSchedule.as_view(),name='annual_schedule'),
    path('service_history/',views.ServiceHistory.as_view(),name='service_history'),
    path('property_list/',views.PropertyList.as_view(),name='properties_list'),
    path('property/<pk>/',views.UpdateProperty.as_view(),name='update_property'),

    path('property_checks/<int:priority>/',views.InspectionList.as_view(),name='inspections'),
    path('inspection/<pk>/',views.UpdateInspection.as_view(),name='inspection_update'),
    path('new_inspection/',views.CreateInspection.as_view(),name='new_inspection'),
    path('new_inspection/<pk>/',views.CreateInspection.as_view(),name='new_inspection_pk'),

    path('qb/properties/<begin>/<end>/',views.QB_PropertyView.as_view(),name='property-list'),
    path('qb/shifts/<begin>/<end>/',views.QB_ShiftView.as_view(),name='property-list'),
    path('temp/',views.Temp1.as_view(),name='temp'),

    url(r'^api/', include(router.urls)),

]
