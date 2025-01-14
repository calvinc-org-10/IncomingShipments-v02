from typing import List, Dict, Any, Callable, Tuple

import decimal
from datetime import datetime, date

from django.db import models
from django.db.models import Q, F, Value
from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex


# standard sizes for decimal fields
HunThouMoney2Dec = {'max_digits':  8, 'decimal_places': 2}
HunThouMoney4Dec = {'max_digits': 10, 'decimal_places': 4}
HunMillMoney2Dec = {'max_digits': 11, 'decimal_places': 2}
HunMillMoney4Dec = {'max_digits': 13, 'decimal_places': 4}

# TODO: move to utils
def moneystr(value):
    return f"${value:,.2f}"
def str_to_dec(value):
    return decimal.Decimal(value.replace("$", "").replace(",", ""))

def datestrYMD(value):
    return value.strftime('%Y-%m-%d')
def strYMD_to_date(value):
    return datetime.strptime(value, '%Y-%m-%d').date()

# for converting Django models to Qt models
class QDjangoTableModel(QAbstractTableModel):
    def __init__(self, tbl:models.Model, flds:List, foreign_keys:List = [], special_processing_flds:Dict[str,Tuple[Callable, Callable]] = {}, filter:Dict[str,Any] = {}, parent = None):
        super().__init__(parent)
        self.headers = flds
        self.queryset = list(tbl.objects.filter(**filter).only(*flds))
        self.foreign_keys = foreign_keys
        self.special_processing = special_processing_flds

    
    def rowCount(self, parent = QModelIndex()):
        return len(self.queryset)
    
    def columnCount(self, parent = QModelIndex()):
        return len(self.headers)
    
    def data(self, index, role = Qt.DisplayRole):
        if not index.isValid():
            return None
        if role == Qt.ItemDataRole.DisplayRole:
            rec = self.queryset[index.row()]
            fldName = self.headers[index.column()]
            value = getattr(rec, fldName, '')
            if fldName in self.foreign_keys:
                value = str(value) if value else ''
            elif fldName in self.special_processing:
                formatter, _ = self.special_processing[fldName]
                if callable(formatter):
                    return formatter(value)
            # endif special field values

            return value
        # endif role
        return None

    def setData(self, index, value, role=Qt.EditRole):
        if not index.isValid():
            return False
        if role == Qt.EditRole:
            rec = self.queryset[index.row()]
            fldName = self.headers[index.column()]

            # Apply special processing for editing if defined
            if fldName in self.special_processing:
                _, editor = self.special_processing[fldName]
                if callable(editor):
                    value = editor(value)

            # Set the field value
            setattr(rec, fldName, value)
            rec.save()
            return True
        return False

 
    def headerData(self, section, orientation, role = Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return self.headers[section]
            elif orientation == Qt.Orientation.Vertical:
                return str(section+1)
            #endif orientation
        # endif role
        return None


# I'm quite happy with automaintained pk fields, so I don't specify any (in most cases)

class Companies(models.Model):
    CompanyName = models.CharField(max_length=250, blank=False)
    SmOffVendorID = models.CharField(max_length=25)
    notes = models.CharField(max_length=250, blank=True)

    def __str__(self) -> str:
        return f'{self.CompanyName}'
        # return super().__str__()

# TODO: Buyers table - used with Organizations and PO
# PO  M->1  Buyers
# Organizations  M<->M  Buyers

class Organizations(models.Model):
    orgname = models.CharField(max_length=250, blank=False)
    CostCenterName = models.CharField(max_length=25)
    ApplyingBusinesUnit = models.CharField(max_length=25)
    # TODO: Link to Buyer list
    notes = models.CharField(max_length=250, blank=True)

    def __str__(self) -> str:
        return f'{self.orgname}'
        # return super().__str__()

class FreightTypes(models.Model):
    FreightType = models.CharField(max_length=25)
    notes = models.CharField(max_length=250, blank=True)

    def __str__(self) -> str:
        return f'{self.FreightType}'
        # return super().__str__()

class Origins(models.Model):
    OriginAbbr3 = models.CharField(max_length=10)
    OriginAbbr2 = models.CharField(max_length=10)
    OriginName = models.CharField(max_length=5)
    notes = models.CharField(max_length=250, blank=True)

    def __str__(self) -> str:
        return f'{self.OriginAbbr3} ({self.OriginName})'
        # return super().__str__()

###########################################################
###########################################################

class StdLineItems(models.Model):
    StdLineItem = models.IntegerField(unique=True)
    notes = models.CharField(max_length=250, blank=True)

class ServiceNames(models.Model):
    ServiceName = models.CharField(max_length=100)
    StdLineItem = models.ForeignKey(StdLineItems, models.CASCADE)
    notes = models.CharField(max_length=250, blank=True)

class Quotes(models.Model):
    company = models.ForeignKey(Companies, models.CASCADE)
    FreightType = models.ForeignKey(FreightTypes, models.CASCADE)
    QuoteNumber = models.CharField(max_length=25)
    Origin = models.ForeignKey(Origins, models.CASCADE)
    notes = models.CharField(max_length=250, blank=True)

    class Meta:
        # ordering = ['orgname']
        constraints = [
                models.UniqueConstraint(fields=['company', 'FreightType', 'QuoteNumber', 'Origin'], name="Quotes_unq_co_FrTy_QNum_Orgin"),
            ]

    def __str__(self) -> str:
        return f'{self.company}.{self.FreightType}.{self.QuoteNumber}.{self.Origin}'
        # return super().__str__()

class QuotedLineItem(models.Model):
    Quote = models.ForeignKey(Quotes, models.CASCADE)
    LineItem = models.ForeignKey(StdLineItems, models.CASCADE)
    unit = models.CharField(max_length=25, blank=True)
    rate = models.DecimalField(**HunThouMoney4Dec)
    minChg = models.DecimalField(**HunThouMoney4Dec, null=True, blank=True)
    maxChg = models.DecimalField(**HunThouMoney4Dec, null=True, blank=True)
    notes = models.CharField(max_length=250, blank=True)

    class Meta:
        constraints = [
                models.UniqueConstraint(fields=['Quote', 'LineItem'], name="QuotedLineItem_unq_Quote_LineItem"),
            ]

    def __str__(self) -> str:
        return f'{self.Quote}.{self.LineItem}'
        # return super().__str__()

###########################################################
###########################################################

class PO(models.Model):
    PONumber = models.CharField(max_length=25, unique=True)
    org = models.ForeignKey(Organizations, models.CASCADE, null=True, blank=True)
    fiiPO = models.ForeignKey("PO", models.SET_NULL, null=True, blank=True)
    Buyer = models.CharField(max_length=30, blank=True, db_default='')
    notes = models.CharField(max_length=250, blank=True)

    class Meta:
        ordering = ['PONumber']

    def __str__(self) -> str:
        return f'{self.PONumber} ({self.org})'
        # return super().__str__()

###########################################################
###########################################################

class ShippingForms(models.Model):
    id_SmOffFormNum = models.IntegerField(unique=True)
    RequestedDelivDate = models.DateField(null=True, blank=True)
    urgent = models.BooleanField(blank=True, default=False)
    PO = models.ForeignKey(PO, models.SET_NULL, null=True, blank=True)
    incoterm = models.CharField(max_length=30, blank=True)
    CostCenter = models.ForeignKey(Organizations, models.CASCADE, null=True, blank=True)
    notes = models.CharField(max_length=250, blank=True)

    class Meta:
        ordering = ['id_SmOffFormNum']

    def __str__(self) -> str:
        return f'{self.id_SmOffFormNum} ({self.CostCenter})'
        # return super().__str__()
class QModelShippingForms(QDjangoTableModel):    
    def __init__(self, filter={}, parent=None):
        tbl = ShippingForms
        flds = [
            'id', 
            'id_SmOffFormNum', 
            'RequestedDelivDate', 
            'urgent', 
            'PO', 
            'incoterm', 
            'CostCenter',
            'notes',
            ]
        foreign_keys = ['PO', 'CostCenter']
        special_proc_flds = {}
        super().__init__(tbl, flds, foreign_keys, special_proc_flds, filter, parent)

class Containers(models.Model):
    ContainerNumber = models.CharField(max_length=30)
    HBL = models.ForeignKey('HBL', models.CASCADE, null=True, blank=True)
    LFD = models.DateField(null=True, blank=True)
    DelivAppt = models.DateField(null=True, blank=True)
    notes = models.CharField(max_length=250, blank=True)

    class Meta:
        constraints = [
                models.UniqueConstraint(fields=['HBL', 'ContainerNumber'], name="Containers_unq_HBL_ContNbr"),
            ]

    def __str__(self) -> str:
        return f'{self.ContainerNumber}'
        # return super().__str__()
class QModelContainers(QDjangoTableModel):
    def __init__(self, filter={}, parent=None):
        tbl = Containers
        flds = [
            'id', 
            'ContainerNumber',
            'HBL',
            'LFD',
            'DelivAppt',
            'notes',
            ]
        foreign_keys = ['HBL', ]
        special_proc_flds = {}
        super().__init__(tbl, flds, foreign_keys, special_proc_flds, filter, parent)

###########################################################
###########################################################

class HBL(models.Model):
    Company = models.ForeignKey(Companies, models.RESTRICT, null=True, blank=True)
    HBLNumber = models.CharField(max_length=30)
    FreightType = models.ForeignKey(FreightTypes, models.RESTRICT, blank=True, null=True)
    Origin = models.ForeignKey(Origins, models.RESTRICT, null=True, blank=True)
    incoterm = models.CharField(max_length=30, blank=True)
    ETA = models.DateField(null=True, blank=True)
    LFD = models.DateField(null=True, blank=True)
    ChargeableWeight = models.FloatField(null=True, blank=True)
    Pieces = models.IntegerField(null=True, blank=True)
    Volume = models.FloatField(null=True, blank=True)
    ShippingForms = models.ManyToManyField(ShippingForms, blank=True)
    POList = models.ManyToManyField(PO, blank=True)
    Quote = models.ForeignKey(Quotes, models.SET_NULL, null=True, blank=True)
    notes = models.CharField(max_length=250, blank=True)
    
    class Meta:
        ordering = ['HBLNumber']
        constraints = [
                models.UniqueConstraint(fields=['Company', 'HBLNumber'], name="HBL_unq_Company_HBLNbr"),
            ]

    def __str__(self) -> str:
        return f'{self.HBLNumber}'
        # return super().__str__()
class QModelHBL(QDjangoTableModel):
    def __init__(self, filter={}, parent=None):
        tbl = HBL
        flds = [
            'id', 
            'Company',
            'HBLNumber',
            'FreightType',
            'Origin',
            'incoterm',
            'ETA',
            'LFD',
            'ChargeableWeight',
            'Pieces',
            'Volume',
            'Quote',
            'notes',
            ]
        foreign_keys = ['Company', 'FreightType', 'Origin', 'Quote', 'HBLNumber', ] # HBLNumber incl as a trick to force to str
        special_proc_flds = {}
        super().__init__(tbl, flds, foreign_keys, special_proc_flds, filter, parent)


class Invoices(models.Model):
    class SmOffStatusCodes(models.IntegerChoices):
        NOTENT   = 000, 'NOT ENTRD'
        DRAFT    = 100, 'DRAFT'   
        PENDING  = 200, 'PENDING'
        APPROVED = 900, 'APPROVED'
    id_SmOffFormNum = models.IntegerField(null=True, blank=True, unique=True)
    SmOffStatus = models.IntegerField(choices=SmOffStatusCodes, default=SmOffStatusCodes.NOTENT)
    inv_downloaded = models.BooleanField(default=False)
    verifiedForFii = models.BooleanField(default=False)
    #Company - not needed - it comes from HBL
    Company = models.ForeignKey(Companies, models.RESTRICT, null=True, blank=True)
    InvoiceNumber = models.CharField(max_length=30, unique=True)
    InvoiceDate = models.DateField()
    InvoiceAmount = models.DecimalField(**HunMillMoney2Dec)
    HBL = models.ForeignKey(HBL, models.RESTRICT)
    AddlBillingForInv = models.ForeignKey("Invoices", models.RESTRICT, null=True, blank=True)
    notes = models.CharField(max_length=250, blank=True)

    class Meta:
        ordering = ['InvoiceNumber']

    def __str__(self) -> str:
        return f'{self.InvoiceNumber} ({self.id_SmOffFormNum})'
        # return super().__str__()
class QModelInvoices(QDjangoTableModel):
    def __init__(self, filter={}, parent=None):
        tbl = Invoices
        flds = [
            'id', 
            'id_SmOffFormNum',
            'inv_downloaded',
            'SmOffStatus',
            'Company',
            'InvoiceNumber',
            'InvoiceDate',
            'InvoiceAmount',
            'HBL',
            'AddlBillingForInv',
            'verifiedForFii',
            'notes',
            ]
        foreign_keys = ['Company', 'HBL', 'AddlBillingForInv',  ]
        special_processing_flds = {
            'InvoiceDate': (datestrYMD, strYMD_to_date),
            'InvoiceAmount': (moneystr, str_to_dec),
            'SmOffStatus': (
                lambda code: Invoices.SmOffStatusCodes.__call__(code).label if code in Invoices.SmOffStatusCodes else None,
                lambda code: code
                ),
        }
        super().__init__(tbl, flds, foreign_keys, special_processing_flds=special_processing_flds, filter=filter, parent=parent)
        


###########################################################
###########################################################

class references(models.Model):
    # do I need a distinguisher between emails and files?
    emaildatefrom_or_filelocation = models.CharField(max_length=255, blank=False, unique=True)
    FilePath = models.FilePathField("W:\\", path=None, match=None, recursive=True, allow_folders=False, max_length=150,db_default='')
    notes = models.TextField(blank=True)
    
    def __str__(self) -> str:
        return f'{self.emaildatefrom_or_filelocation}'
        # return super().__str__()
class reference_ties(models.Model):
    class refTblChoices(models.TextChoices):
        Invoices      = 'INVC',  'Invoice'
        ShippingForms = 'SHPFM', 'Shipping Form'
        HBL           = 'HBL', 'HBL'          
        Containers    = 'CNTNR', 'Container'
    email = models.ForeignKey(references,models.CASCADE)
    table_ref = models.CharField(max_length=5, choices=refTblChoices, blank=True)
    record_ref = models.IntegerField(null=True, blank=True)

    class Meta:
        constraints = [
                models.UniqueConstraint(fields=['email', 'table_ref', 'record_ref'], name="references_unq_ref_tref_recref"),
            ]
def all_references() -> models.QuerySet:
    # filters will most likely be complex, with muliple Q ors and ands.
    # let the caller have all the records and then fiter
    return reference_ties.objects.select_related('email')\
        .annotate(
            notes=F('email__notes'), 
            FilePath=F('email__FilePath'), 
            record_name=Value('')
            )
class QModelrefs(QDjangoTableModel):
    special_processing = {}
    def __init__(self, tbl, parent=None):
        # note: tbl will come in pre-joined and pre-filtered
        QAbstractTableModel.__init__(self)    # we need to skip over the QDjangoTableModel init; it's not designed for this weird join
        flds = [
            'id', 
            'email',
            'table_ref',
            'record_ref',
            'record_name',
            'FilePath',
            'notes',
            ]
        foreign_keys = ['email', 'table_ref', ]

        # later, convert the record_ref to the keyvalue
        
        self.headers = flds
        for rec in tbl:
            if rec.table_ref == reference_ties.refTblChoices.Containers:
                rec.record_name = str(Containers.objects.get(pk=rec.record_ref))
            if rec.table_ref == reference_ties.refTblChoices.HBL:
                rec.record_name = str(HBL.objects.get(pk=rec.record_ref))
            if rec.table_ref == reference_ties.refTblChoices.Invoices:
                rec.record_name = str(Invoices.objects.get(pk=rec.record_ref))
            if rec.table_ref == reference_ties.refTblChoices.ShippingForms:
                rec.record_name = str(ShippingForms.objects.get(pk=rec.record_ref))

        # from django.apps import apps

        # tName = "Invoices"
        # ModelClass = apps.get_model('billing', tName)

        # try:
        #     rrec = ModelClass.objects.first()
        #     print(rrec)
        # except ModelClass.DoesNotExist:
        #     print(f"No records found in model {tName}.")

        Qannotated = list(tbl)
        self.queryset = Qannotated
        self.foreign_keys = foreign_keys

##########################################################
##########################################################


##########################################################
##########################################################