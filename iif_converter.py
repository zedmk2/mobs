#! python3
#iif_converter.py - takes jason property/job data and creates QB IIF text
#delimted file for quickbooks invoice creation

from work.models import *
import csv
import json
import ast

null= 0
jcosting = open('input_from_web.json')
jcost = jcosting.read()
jc = json.loads(jcost)
temp = []

for prop in jc:
    if prop['location'] != []:
        temp.append(prop)

jc = temp

upload = open('template.iif',encoding = "ISO-8859-1")
uploadReader = csv.reader(upload,delimiter='\t')
uploadData = list(uploadReader)

##Time variables
eom = '4/30/2018'
som = '5/1/2018'
net30date = '5/31/2018'
job_date_first = '4/1'
job_date_last = '4/30'
full_month_string = 'April 2018'


##placeholder variables
inv_type = 'SL'
date=eom
customer=''
amount = ''
docnum = ''
addr1 = ''
addr2 = ''
addr3 = ''
addr4 = ''
addr5 = ''
duedate = ''
terms= ''
saddr1 = ''
saddr2 = ''
saddr3 = ''
saddr4 = ''
tosend = 'N'
spl_amount = ''
memo = ''
qty = ''
price = ''
service_date = ''

trans = ['TRNS', '', 'INVOICE', date, 'Accounts Receivable',
        prop['client_name'], amount, docnum, '', 'N', 'Y', 'N', prop['addr1'],
        prop['addr2'], prop['addr3'], prop['addr4'], prop['addr5'], duedate, prop['terms'], date,
        prop['saddr1'], prop['saddr2'], prop['saddr3'], prop['saddr4'], prop['tosend']]
spl = ['SPL', '', 'INVOICE', date, 'Sales:Sweeping',
        '', neg_amount,'', prop['memo'], 'N', qty, prop['sw_price'], 'Sweeping',
        '', 'N', 'N', 'NOTHING', service_date, '', '',
        '', '', '', '', '']
endTrans = ['ENDTRNS', '', '', '', '', '', '', '', '', '', '', '',
            '', '', '', '', '', '', '', '', '', '', '', '', '']


iif_file = open('output_for_qb.csv','w',newline='')
iif_writer = csv.writer(iif_file,delimiter='\t')
#Creates 3 header rows for transactions and lines
for i in range(3):
    iif_writer.writerow(uploadData[i])

docnum = 1
for prop in jc:
    #Need a trigger for eom or beginning of month
    date = eom
    service_date = date
    if prop['inv_date'] == 'Start of Month':
        date = som
    duedate = date
    if prop['terms'] == 'Net 30':
        duedate = net30date
    qty = ''
    if prop['qty'] == 'Count':
        qty = len(prop['location']) * -1

    if prop['inv_date'] == 'Start of Month':
        price = prop['sw_mo_price']
    elif "Monthly install" in str(prop['memo']):
        price = prop['sw_mo_price']
    else:
        price = prop['sw_price']

    ml_spl = prop['adlspl']

    try:
        amount = price * abs(qty)
    except:
        amount = price

    try:
        neg_amount = amount * -1
    except:
        neg_amount = 0

    if prop['update_memo'] == 'Y':
        job_date_list = []
        for job in prop['location']:
            cdate = job['job_shift']['date'].split('-')
            ndate = (cdate[1].lstrip('0'))+'/'+(cdate[2].lstrip('0'))
            job_date_list.append(ndate)
        job_date_string = ', '.join(job_date_list)

        if '{full_month_string}' in prop['memo']:
            prop['memo'] = (prop['memo'].format(full_month_string=full_month_string))
        if '{job_date_first}' in prop['memo']:
            prop['memo'] = (prop['memo'].format(job_date_first=job_date_first,job_date_last=job_date_last))
        prop['memo'] = (prop['memo'].format(job_date_string))
        print(prop['memo'])

    trans = ['TRNS', '', 'INVOICE', date, 'Accounts Receivable',
            prop['client_name'], amount, docnum, '', 'N', 'Y', 'N', prop['addr1'],
            prop['addr2'], prop['addr3'], prop['addr4'], prop['addr5'], duedate, prop['terms'], date,
            prop['saddr1'], prop['saddr2'], prop['saddr3'], prop['saddr4'], prop['tosend']]
    iif_writer.writerow(trans)
    if prop['inv_type'] == 'SL':
        spl = ['SPL', '', 'INVOICE', date, 'Sales:Sweeping',
            '', neg_amount,'', prop['memo'], 'N', qty, prop['sw_price'], 'Sweeping',
            '', 'N', 'N', 'NOTHING', service_date, '', '',
            '', '', '', '', '']
        iif_writer.writerow(spl)
    if prop['inv_type'] == 'ML':
        for quick_spl in ml_spl:
            tempvar = quick_spl
            print(tempvar)
    iif_writer.writerow(endTrans)
    docnum = docnum +1

#Loop over each property, creating trans and lines for each based on setup

iif_file.close()
print('!!break!!')
