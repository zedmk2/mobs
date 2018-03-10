from django.contrib import admin
from . import models

# Register your models here.

class JobAdmin(admin.ModelAdmin):
    search_fields = ['job_location']

class PropertyAdmin(admin.ModelAdmin):
    search_fields = ['name']
    fields = ['name','address','city','state','zipcode',]

    list_display = ['name','address','city','state','zipcode',]
    list_editable = ['address','city','state','zipcode',]


class ClientAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ['name','zipcode']

class JobInlineAdmin(admin.TabularInline):
    model = models.Job
    ordering = ("-job_location",)
    extra = 8

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
