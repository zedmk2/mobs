#! python3
#iif_converter.py - takes jason property/job data and creates QB IIF text
#delimted file for quickbooks invoice creation

from work.models import *
import csv
import json
import ast

upload = open('original.csv',encoding = "ISO-8859-1")
uploadReader = csv.reader(upload,delimiter='\t')
ud = list(uploadReader)

dupload = open('test.csv',encoding = "ISO-8859-1")
duploadReader = csv.reader(dupload,delimiter='\t')
dd = list(duploadReader)

print(ud[3])
print(dd[3])
i=0

for a in ud[3]:

    print(str(i)+'. '+ str((a == dd[3][i])))
    i +=1

print(ud[3]==dd[3])

print('~~~~~')

for pre in ud:
    if pre[0] == 'TRNsS':
        for post in dd:
            pre[7]=post[7]
            print(pre[4])
            if pre == post[0]:
                print(pre)
                print(post)
