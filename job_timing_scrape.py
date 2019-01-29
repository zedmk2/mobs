from work.models import Shift, Job, Property, Employee, Inspection, Route
from django.db.models import Prefetch
import csv

begin = '2018-11-01'
end = '2018-12-31'


shift_set = Shift.objects.filter(date__gte=begin).filter(date__lte=end).select_related('driver').select_related('helper').select_related('helper_2')
job_set = Job.objects.filter(job_shift__date__gte=begin).filter(job_shift__date__lte=end).prefetch_related(Prefetch('job_shift',queryset=shift_set))
property_set = Property.objects.filter(job_costing_report_include=False).order_by('client_name', 'display_name').prefetch_related(Prefetch('location',queryset=job_set,to_attr='jobs')).prefetch_related(Prefetch('location__job_location__client_name'))

for p in property_set[0:10]:
    print(p)
    print(p.sw_price)
    print(p.sw_mo_price)

# outputFile = open('output.csv', 'w', newline='')
# outputWriter = csv.writer(outputFile)
# outputWriter.writerow(['location','date','timein','timeout','length'])
# for job in job_set:
#     print(job.job_location)

#     outputWriter.writerow([job.job_location,job.datenight ,job.start_time,job.end_time,job.job_length])

# outputFile.close()

outputFile2 = open('output2.csv', 'w', newline='')
outputWriter2 = csv.writer(outputFile2)
outputWriter2.writerow(['property','sw_price','mo_price'])

for p in property_set:
    outputWriter2.writerow([p,p.sw_price,p.sw_mo_price])

outputFile2.close()
