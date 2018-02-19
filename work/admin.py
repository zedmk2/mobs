from django.contrib import admin
from . import models

# Register your models here.

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

admin.site.register(models.Job)
admin.site.register(models.Client)
admin.site.register(models.Property)
admin.site.register(models.Employee)
admin.site.register(models.Shift,Shift_Inline_Admin)
