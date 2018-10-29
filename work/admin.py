from django.contrib import admin
from . import models

# Register your models here.

class JobAdmin(admin.ModelAdmin):
    search_fields = ['job_location']
    list_display = ['job_shift','job_location','start_time','end_time','date']

class PropertyAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ['id','name','display_name','color','instructions','check_priority','sw_price','sw_mo_price','times_per_week','times_per_month','times_per_year']
    list_editable = ['name','display_name','color','instructions','check_priority','sw_price','sw_mo_price','times_per_month','times_per_week','times_per_year',]
    list_filter = ['job_costing_report_include',]

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

class Shift_Inline_Admin(admin.ModelAdmin):
    inlines = [
    JobInlineAdmin,
    ]
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "job":
            kwargs["queryset"] = School.objects.order_by('job_location')
        return super(Shift_Inline_Admin, self).formfield_for_foreignkey(db_field, request, **kwargs)

admin.site.register(models.Job, JobAdmin)
admin.site.register(models.Client, ClientAdmin)
admin.site.register(models.Property, PropertyAdmin)
admin.site.register(models.Inspection)
admin.site.register(models.Employee)
admin.site.register(models.Shift,Shift_Inline_Admin)
admin.site.register(models.Route, RouteAdmin)
admin.site.register(models.RouteJob)
