from xml.dom import minidom
from datetime import datetime
import os

class sepa_buchung:
    end2end = ''
    iban = ''
    bic = ''
    kontoinhaber = ''
    verwendungszweck = ''
    amount = ''
    mandatId = ''
    mandatDate = ''
    mandatChange = ''

    def normalize_string(input):
        replace_dict = {
            'Á':'A', 'À':'A', 'Â':'A', 'Ã':'A', 'Å':'A', 'Ä':'Ae', 'Æ':'AE', 'Ç':'C', 'É':'E', 'È':'E', 'Ê':'E', 'Ë':'E',
            'Í':'I', 'Ì':'I', 'Î':'I', 'Ï':'I', 'Ð':'Eth', 'Ñ':'N', 'Ó':'O', 'Ò':'O', 'Ô':'O', 'Õ':'O', 'Ö':'O', 'Ø':'O', 
            'Ú':'U', 'Ù':'U', 'Û':'U', 'Ü':'Ue', 'Ý':'Y', 'á':'a', 'à':'a', 'â':'a', 'ã':'a', 'å':'a', 'ä':'ae', 'æ':'ae',
            'ç':'c', 'é':'e', 'è':'e', 'ê':'e', 'ë':'e', 'í':'i', 'ì':'i', 'î':'i', 'ï':'i', 'ð':'eth', 'ñ':'n', 'ó':'o',
            'ò':'o', 'ô':'o', 'õ':'o', 'ö':'oe', 'ø':'o', 'ú':'u', 'ù':'u', 'û':'u', 'ü':'ue', 'ý':'y', 'ß':'ss', 'þ':'thorn',
            'ÿ':'y', '&':'u.', '@':'at', '#':'h', '$':'s', '%':'perc', '^':'-','*':'-'
        }

        for x in input:
            if x in replace_dict:
                input = input.replace(x, replace_dict[x])

        return input

    def __str__(self):
        # doesnt print end2end because its never set anyways
        return 'SEPA-ENTRY: '+self.kontoinhaber+' '+self.bic+' '+self.iban+' '+str(self.amount)+' '+self.mandatId+' '+self.mandatDate+' '+self.verwendungszweck


class sepa_xml_creator:
    dom = minidom.Document()
    buchungssaetze = []
    accountName = ''
    accountIban = ''
    accountBic = ''
    offset = 0
    fixedDate = ''
    currency = 'EUR'
    isFirst = True
    creditorId = ''

    def set_account_values(self, name, iban, bic):
        self.accountName = name
        self.accountIban = iban
        self.accountBic = bic

    def calc_umsatzsumme(self):
        betrag = 0

        for b in self.buchungssaetze:
            betrag += float(b.amount)

        return betrag

    def gen_el(self, nm, text):
        tmp = self.dom.createElement(nm)
        tmp.appendChild(self.dom.createTextNode(str(text)))
        return tmp

    def print_sepa_entries(self):
        for entry in self.buchungssaetze:
            print(entry)




    def generate_xml(self):        
        document = self.dom.createElement('Document')
        document.setAttribute('xmlns', 'urn:iso:std:iso:20022:tech:xsd:pain.008.001.02')
        document.setAttribute('xsi:schemaLocation', 'urn:iso:std:iso:20022:tech:xsd:pain.008.001.02 pain.008.001.02.xsd')
        document.setAttribute('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')        
        self.dom.appendChild(document)
        content = self.dom.createElement('CstmrDrctDbtInitn')
        document.appendChild(content)
        header = self.dom.createElement('GrpHdr')
        content.appendChild(header)

        creation_time = datetime.now()

        #Msg-ID
        header.appendChild(self.gen_el('MsgId', str(self.accountBic + '00' + creation_time.strftime('%Y%m%d%H%M%S'))))
        header.appendChild(self.gen_el('CreDtTm', (creation_time.strftime('%Y-%m-%d') + 'T' + creation_time.strftime('%H:%M:%S') + '.000Z')))
        header.appendChild(self.gen_el('NbOfTxs', len(self.buchungssaetze)))
        initiator = self.dom.createElement('InitgPty')
        initiator.appendChild(self.gen_el('Nm', self.accountName))
        header.appendChild(initiator)

        #Payment Info
        payment_info = self.dom.createElement('PmtInf')
        content.appendChild(payment_info)
        payment_info.appendChild(self.gen_el('PmtInfId', 'PMT-ID0-' + creation_time.strftime('%Y%m%d%H%M%S')))
        payment_info.appendChild(self.gen_el('PmtMtd', 'DD'))
        payment_info.appendChild(self.gen_el('BtchBookg', 'true'))
        payment_info.appendChild(self.gen_el('NbOfTxs', len(self.buchungssaetze)))
        payment_info.appendChild(self.gen_el('CtrlSum', str(round(self.calc_umsatzsumme(),2))))
        tmp = self.dom.createElement('PmtTpInf')
        tmp2 = self.dom.createElement('SvcLvl')
        tmp2.appendChild(self.gen_el('Cd', 'SEPA'))
        tmp.appendChild(tmp2)
        tmp3 = self.dom.createElement('LclInstrm')
        tmp3.appendChild(self.gen_el('Cd', 'CORE'))
        tmp.appendChild(tmp3)
        if self.isFirst:
            tmp.appendChild(self.gen_el('SeqTp', 'FRST'))
        else:
            tmp.appendChild(self.gen_el('SeqTp', 'RCUR'))

        payment_info.appendChild(tmp)

        #Ausführungsdatum
        #Muss gesetzt werdem im format Y-m-d
        payment_info.appendChild(self.gen_el('ReqdColltnDt', self.fixedDate))

        #eigene Acc Daten
        cdtr = self.dom.createElement('Cdtr')
        cdtr.appendChild(self.gen_el('Nm', self.accountName))
        payment_info.appendChild(cdtr)

        cdtrAcct = self.dom.createElement('CdtrAcct')
        tmp = self.dom.createElement('Id')
        tmp.appendChild(self.gen_el('IBAN', self.accountIban))
        cdtrAcct.appendChild(tmp)        
        payment_info.appendChild(cdtrAcct)

        tmp = self.dom.createElement('CdtrAgt')
        tmp2 = self.dom.createElement('FinInstnId')
        tmp2.appendChild(self.gen_el('BIC', self.accountBic))
        tmp.appendChild(tmp2)
        payment_info.appendChild(tmp)
        payment_info.appendChild(self.gen_el('ChrgBr', 'SLEV'))

        tmp = self.dom.createElement('CdtrSchmeId')
        tmp2 = self.dom.createElement('Id')
        tmp3 = self.dom.createElement('PrvtId')
        tmp4 = self.dom.createElement('Othr')
        tmp4.appendChild(self.gen_el('Id', self.creditorId))
        tmp5 = self.dom.createElement('SchmeNm')
        tmp5.appendChild(self.gen_el('Prtry', 'SEPA'))

        tmp4.appendChild(tmp5)
        tmp3.appendChild(tmp4)
        tmp2.appendChild(tmp3)
        tmp.appendChild(tmp2)
        payment_info.appendChild(tmp)

        #Buchungssaetze hinzufügen
        for b in self.buchungssaetze:
            buchung = self.dom.createElement('DrctDbtTxInf')
            tmp = self.dom.createElement('PmtId')
            tmp.appendChild(self.gen_el('EndToEndId', 'NOTPROVIDED'))
            buchung.appendChild(tmp)

            #Betrag
            tmp = self.gen_el('InstdAmt', str(round(float(b.amount),2)))
            tmp.setAttribute('Ccy', self.currency)
            buchung.appendChild(tmp)

            #Mandatsinfos
            tmp = self.dom.createElement('DrctDbtTx')
            tmp2 = self.dom.createElement('MndtRltdInf')
            tmp2.appendChild(self.gen_el('MndtId', b.mandatId))
            tmp2.appendChild(self.gen_el('DtOfSgntr', b.mandatDate))
            tmp2.appendChild(self.gen_el('AmdmntInd', 'false'))
            tmp.appendChild(tmp2)
            buchung.appendChild(tmp)

            #Institut
            tmp = self.dom.createElement('DbtrAgt')
            tmp2 = self.dom.createElement('FinInstnId')
            tmp2.appendChild(self.gen_el('BIC', b.bic))
            tmp.appendChild(tmp2)
            buchung.appendChild(tmp)

            #Inhaber
            tmp = self.dom.createElement('Dbtr')
            tmp.appendChild(self.gen_el('Nm', b.kontoinhaber))
            buchung.appendChild(tmp)

            #IBAN
            tmp = self.dom.createElement('DbtrAcct')
            tmp2 = self.dom.createElement('Id')
            tmp2.appendChild(self.gen_el('IBAN', b.iban))
            tmp.appendChild(tmp2)
            buchung.appendChild(tmp)
            tmp = self.dom.createElement('UltmtDbtr')
            tmp.appendChild(self.gen_el('Nm', b.kontoinhaber))
            buchung.appendChild(tmp)

            #Verwendungszweck
            if len(b.verwendungszweck) > 0:
                tmp = self.dom.createElement('RmtInf')
                tmp.appendChild(self.gen_el('Ustrd', b.verwendungszweck))
                buchung.appendChild(tmp)

            payment_info.appendChild(buchung)

        return self.dom.toprettyxml(indent ="\t") 



        