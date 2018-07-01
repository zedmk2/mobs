#! python3
#adds routes to MOBS based on inputs below

from work.models import *
from django.utils import timezone
from datetime import timedelta
import csv
import calendar

employees = Employee.objects.exclude(end_date__lte=timezone.now())
employees = list(employees)

dates = []

for i in range(2):
    dates.append(timezone.now().date() + timedelta(i))

print("You want to update the following dates: "+str(dates))

###Find employees working on each date###
# for i in range(4):
#     query = Shift.objects.get_or_create(date=datetime.date(), driver=employees[i])

###Populate jobs into each shift
date_shifts = Shift.objects.filter(date=dates[0])
job_location_temp = Property.objects.get(pk=1)

route_list = Route.objects.all()
# temp_route = Route.objects.get(pk=1)
# print(temp_route.job_route.all()[0].route_location)

for d in dates:
    print(d)
    for route in route_list:
        if d.weekday()==int(route.weekday):
            shift, bool = Shift.objects.get_or_create(date=d,driver=route.driver)
            for prop in route.job_route.all():
                print(prop)
                shift.jobs_in_shift.get_or_create(job_location=prop.route_location,order=prop.order)
                # print("Created shift for %s %s" % (d,j.driver))

# for j in job_list:
#     print(j)
#     for l in j.job_route.all():
#         pass

# for s in date_shifts:
#     print(s)
#
#     job = s.jobs_in_shift.get_or_create(job_location=job_location_temp)
#     # job = s.jobs_in_shift.get_or_create(job_location=Property.objects.get(name='Pikesville Towne Center'))
#     print(job)
#     print(s.jobs_in_shift.all())

print('!! Run complete !!')
