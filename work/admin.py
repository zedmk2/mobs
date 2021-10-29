from django.contrib import admin
from . import models
from django.contrib import admin
from django.contrib.admin.models import LogEntry

# Register your models here.

class JobAdmin(admin.ModelAdmin):
    search_fields = ['job_location__display_name']
    list_display = ['job_shift','job_location','start_time','end_time','date']

class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['name','first_name','last_name','em_uid','start_date','end_date','driver','helper','porter']
    list_editable = ['em_uid','start_date','end_date',]

class PropertyAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ['id','name','display_name','color','instructions','check_priority','sw_price','sw_mo_price','times_per_week','days_of_week','times_per_month','times_per_year','adlspl','length','county']
    list_editable = ['color','check_priority','adlspl','length','county']
    list_filter = ['job_costing_report_include',]

class RouteJobAdmin(admin.ModelAdmin):
    search_fields = ['route_location']
    list_display = ['route_location','job_route','order','freq']
    list_editable = ['job_route','order','freq']

class ClientAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ['id','name','billing_name']
    list_editable = ['name','billing_name',]

class JobInlineAdmin(admin.TabularInline):
    model = models.Job
    ordering = ("-job_location",)
    extra = 8

class RouteJobInline(admin.TabularInline):
    model = models.RouteJob
    extra = 10

class RouteAdmin(admin.ModelAdmin):
    inlines = [RouteJobInline,]
    list_display = ["weekday", "route_num", "driver"]
    list_editable = [ "route_num", "driver"]

class ShiftAdmin(admin.ModelAdmin):
    list_display = ["id","driver",  "date", "created_at"]
    list_editable = [ "driver", "date"]

class Shift_Inline_Admin(admin.ModelAdmin):
    list_display = ["id","driver",  "date", "created_at"]
    list_editable = [ "driver", "date"]
    inlines = [
    JobInlineAdmin,
    ]
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "job":
            kwargs["queryset"] = School.objects.order_by('job_location')
        return super(Shift_Inline_Admin, self).formfield_for_foreignkey(db_field, request, **kwargs)


class LogEntryAdmin(admin.ModelAdmin):
    readonly_fields = ('content_type',
        'user',
        'action_time',
        'object_id',
        'object_repr',
        'action_flag',
        'change_message'
    )
    list_display = [ "action_time", "user",'content_type','object_repr','change_message']

admin.site.register(LogEntry, LogEntryAdmin)
admin.site.register(models.Job, JobAdmin)
admin.site.register(models.Client, ClientAdmin)
admin.site.register(models.Property, PropertyAdmin)
admin.site.register(models.Inspection)
admin.site.register(models.Employee, EmployeeAdmin)
admin.site.register(models.Shift,Shift_Inline_Admin)
admin.site.register(models.Route, RouteAdmin)
admin.site.register(models.RouteJob, RouteJobAdmin)
