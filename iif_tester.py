#! python3
#iif_converter.py - takes jason property/job data and creates QB IIF text
#delimted file for quickbooks invoice creation

from work.models import *
import csv
import json
import ast

upload = open('original_sweep_only.csv',encoding = "ISO-8859-1")
uploadReader = csv.reader(upload,delimiter='\t')
ud = list(uploadReader)

dupload = open('output_for_qb.csv',encoding = "ISO-8859-1")
duploadReader = csv.reader(dupload,delimiter='\t')
dd = list(duploadReader)

print(ud[3])
print(dd[3])
i=0
j=0

dd[3][7] = ud[3][7]

for orig in ud:
    for new in dd:
        if new[20] == orig[20] and orig[0] != 'ENDTRNS' and orig[20] != '':
            new[7]=orig[7]
            i=0
            for a in orig:
                i +=1
            if not new==orig:

                print(orig)
                print(new)
                print('nope')


for pre in ud:
    if pre[0] == 'TRNsS':
        for post in dd:
            pre[7]=post[7]
            print(pre[4])
            if pre == post[0]:
                print(pre)
                print(post)
