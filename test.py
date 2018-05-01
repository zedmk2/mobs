#! python3
from work.models import *
import csv

q = Property.objects.filter(job_costing_report_include=True)

upload1 = open('upload.csv',encoding = "ISO-8859-1")
uploadReader = csv.reader(upload1,delimiter='\t')
uploadData = list(uploadReader)

for prop in q:
    print(prop.name)
    for index, data in enumerate(uploadData):
        if str(data[20]).upper() == str(prop.invoice_name).upper():
            print("check")
            prop.addr1 = str(data[12])
            prop.addr2 = str(data[13])
            prop.addr3 = str(data[14])
            prop.addr4 = str(data[15])
            prop.addr5 = str(data[16])
            prop.terms = str(data[18])
            prop.saddr1 = str(data[20])
            prop.saddr2 = str(data[21])
            prop.saddr3 = str(data[22])
            prop.saddr4 = str(data[23])
            prop.memo = str(uploadData[index+1][8])
            if "GREENBERG" in str(data[5]):
                prop.tosend = str(data[24])
            prop.save()

temp2 = Property.objects.filter(name="Waugh Chapel")
waugh = temp2[0]

print('!!checkup!!')
print(waugh.name)
print(waugh.memo)
