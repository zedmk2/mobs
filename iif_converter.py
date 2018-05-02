#! python3
#iif_converter.py - takes jason property/job data and creates QB IIF text
#delimted file for quickbooks invoice creation

from work.models import *
import csv
import json
import ast
import datetime

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

eolm = '4/1/2018'
mo_start = datetime.datetime.strptime(eolm,'%m/%d/%Y').date()
single_day = datetime.timedelta(days=1)
mon = 0
tue = 0
wed = 0
thu = 0
fri = 0
sat = 0
sun = 0

mo_num = mo_start.month
while mo_num == mo_start.month:
    if mo_start.weekday() == 0:
        mon += 1
    elif mo_start.weekday() ==1:
        tue +=1
    elif mo_start.weekday() ==2:
        wed +=1
    elif mo_start.weekday() ==3:
        thu +=1
    elif mo_start.weekday() ==4:
        fri +=1
    elif mo_start.weekday() ==5:
        sat +=1
    elif mo_start.weekday() ==6:
        sun +=1
    mo_start += single_day

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
print('dumps')
print(json.dumps([spl,spl]))
print('dumps')
endTrans = ['ENDTRNS', '', '', '', '', '', '', '', '', '', '', '',
            '', '', '', '', '', '', '', '', '', '', '', '', '']


iif_file = open('output_for_qb.csv','w',newline='')
iif_writer = csv.writer(iif_file,delimiter='\t')
#Creates 3 header rows for transactions and lines
for i in range(3):
    iif_writer.writerow(uploadData[i])

docnum = 1
for prop in jc:
    if prop['inv_type'] != 'NI':
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

        if prop['inv_type'] == 'SL' or prop['inv_type']=='MI':
            trans = ['TRNS', '', 'INVOICE', date, 'Accounts Receivable',
                    prop['client_name'], amount, docnum, '', 'N', 'Y', 'N', prop['addr1'],
                    prop['addr2'], prop['addr3'], prop['addr4'], prop['addr5'], duedate, prop['terms'], date,
                    prop['saddr1'], prop['saddr2'], prop['saddr3'], prop['saddr4'], prop['tosend']]
            iif_writer.writerow(trans)

            spl = ['SPL', '', 'INVOICE', date, 'Sales:Sweeping',
                '', neg_amount,'', prop['memo'], 'N', qty, prop['sw_price'], 'Sweeping',
                '', 'N', 'N', 'NOTHING', service_date, '', '',
                '', '', '', '', '']
            iif_writer.writerow(spl)
            if prop['saddr1'] == '4700 Belle Grove Road':
                iif_writer.writerow(endTrans)
                trans[20] == '4701 Belle Grove Road'
                iif_writer.writerow(trans)
                iif_writer.writerow(spl)

        if prop['inv_type'] == 'ML':
            if prop['client_name'] == 'U.S. REALTY & INVESTMENT CO.':
                memo = prop['memo']
                qty = -1*(sun+mon+wed+fri+sat)
                neg_amount = qty * prop['sw_price']
                spl = ['SPL', '', 'INVOICE', date, 'Sales:Sweeping',
                    '', neg_amount,'', memo, 'N', qty, prop['sw_price'], 'Sweeping',
                    '', 'N', 'N', 'NOTHING', service_date, '', '',
                    '', '', '', '', '']

                sw_price_2 = 30.9
                memo_2 = 'Parking lot sweeping - 2x per week (Shoppers area only)'
                qty_2 = -1*(tue+thu)
                neg_amount_2 = qty_2 * sw_price_2
                spl_2 = ['SPL', '', 'INVOICE', date, 'Sales:Sweeping',
                    '', neg_amount_2,'', memo_2, 'N', qty_2, sw_price_2, 'Sweeping',
                    '', 'N', 'N', 'NOTHING', service_date, '', '',
                    '', '', '', '', '']
                amount = -1*(neg_amount+neg_amount_2)
                trans = ['TRNS', '', 'INVOICE', date, 'Accounts Receivable',
                        prop['client_name'], amount, docnum, '', 'N', 'Y', 'N', prop['addr1'],
                        prop['addr2'], prop['addr3'], prop['addr4'], prop['addr5'], duedate, prop['terms'], date,
                        prop['saddr1'], prop['saddr2'], prop['saddr3'], prop['saddr4'], prop['tosend']]
                iif_writer.writerow(trans)
                iif_writer.writerow(spl)
                iif_writer.writerow(spl_2)
            i=1
            adl_lines = json.loads(prop['adlspl'])

        if prop['inv_type'] == 'MI':
            #Want to have more robust multi invoicing
            pass

        iif_writer.writerow(endTrans)
        docnum = docnum +1


#Loop over each property, creating trans and lines for each based on setup

iif_file.close()
print('!!break!!')
