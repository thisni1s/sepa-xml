# create  sepaXmlCreator
import createSepaXml
import csv
import sys
from schwifty import IBAN
from schwifty import BIC
from datetime import datetime


ACCOUNT_NAME = ''
ACCOUNT_IBAN = ''
ACCOUNT_BIC = ''
CREDITOR_ID = ''
IS_FIRST = False
FIXED_DATE = '2023-01-20'
SINGLE_AMOUNT = 10.0
SIBLING_AMOUNT = 10.0
PURPOSE = ''
OUTPUT_FILE_NAME = 'sepa.xml'



def calc_amount(str):
    if str=='1':
        return SIBLING_AMOUNT
    else:
        return SINGLE_AMOUNT

def calc_date(date: str):
    datearr = date.split('.')
    if len(datearr[2]) == 2:
        year = 2000 + int(datearr[2])
    else:
        year = int(datearr[2])
    time = datetime(year, int(datearr[1]), int(datearr[0]))
    return time.strftime('%Y-%m-%d')

def get_RCUR():
    if IS_FIRST:
        return 'FRST'
    else:
        return 'RCUR'
    

creator = createSepaXml.sepa_xml_creator()

creator.accountName = ACCOUNT_NAME
creator.accountIban = ACCOUNT_IBAN
creator.accountBic = ACCOUNT_BIC
creator.creditorId = CREDITOR_ID
creator.isFirst = IS_FIRST
creator.fixedDate = FIXED_DATE

with open(sys.argv[1]) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    next(csv_reader)
    next(csv_reader)
    count = 0
    for row in csv_reader:
        if (row[16] == "1" and row[13] == get_RCUR() and len(row[6]) != 0): # First and ausgefüllt and email not empty
            count += 1
            buchung = createSepaXml.sepa_buchung()
            buchung.kontoinhaber = row[8]
            buchung.iban = row[9]
            buchung.bic = row[10]
            buchung.amount = calc_amount(row[14])
            buchung.mandatId = createSepaXml.sepa_buchung.normalize_string(row[15])
            buchung.mandatDate = calc_date(row[11])
            buchung.mandatChange = False
            buchung.verwendungszweck = createSepaXml.sepa_buchung.normalize_string(PURPOSE+' '+row[1]+' '+row[2])

            #check the banking details
            try:
                iban = IBAN(buchung.iban) # should raise an error if its wrong somehow
                if iban.bic.formatted.replace(' ', '') != buchung.bic:
                    if len(buchung.bic) == 0:
                        buchung.bic = iban.bic.formatted.replace(' ', '')
                        creator.buchungssaetze.append(buchung)
                    else:
                        print("BIC for " + buchung.kontoinhaber + " is invalid, skipping")
                else:
                    creator.buchungssaetze.append(buchung)


            except:
                print("IBAN for " + buchung.kontoinhaber + " is invalid, skipping")  
        

print(count)  

#creator.print_sepa_entries()
xml_string = creator.generate_xml()
with open(OUTPUT_FILE_NAME, "w") as f:
    f.write(xml_string) 