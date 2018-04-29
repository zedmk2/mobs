from work.models import Shift, Job, Property, Employee, Inspection
shift_set = [{'date':'2018-04-09','driver':'Carlos','helper':'Juan'}]
s = Job.objects.all()
print(s)

def sch():
    print(s)
