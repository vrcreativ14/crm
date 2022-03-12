GOVERNMENT_FEE = 4200
EXPIRED_QUOTE_EXTENSION_DAYS = 15
VAT_PERCENTAGE = 0.05
STAGE_NEW = "new"
STAGE_QUOTE = "quote"
STAGE_SETTLEMENT = "settlement"
STAGE_VALUATION = "valuation"
STAGE_FINAL_OFFER = "offer"
STAGE_ClosedWON = "won"
STAGE_ClosedLOST = "lost"
STAGE_PREAPPROVAL = "preApproval"
STAGE_LOAN_DISBURSAL = "loanDisbursal"
STAGE_PROPERTY_TRANSFER = "propertyTransfer"

DEAL_STAGES = (
    ("new", "New Deal"),
    (STAGE_QUOTE, "Quote Sent"),
    (STAGE_PREAPPROVAL, "Pre Approval"),
    (STAGE_VALUATION, "Valuation"),
    (STAGE_FINAL_OFFER, "Final Offer"),
    (STAGE_SETTLEMENT, "Settlement"),
    (STAGE_LOAN_DISBURSAL, "Loan Disbursal"),
    (STAGE_PROPERTY_TRANSFER, "Property Transfer"),
    (STAGE_ClosedWON, "Closed Won"),
    (STAGE_ClosedLOST, "Closed Lost"),
)

DEAL_TYPE_NEW = "new"
DEAL_TYPE_DUPLICATE = "duplicate"
DEAL_TYPE_RENEWAL = "renewal"
DEAL_TYPE_DEVELOPER = "developer"
DEAL_TYPE_BUY_OUT = "buy out"
DEAL_TYPE_REFINANCE = "refinance"
DEAL_TYPE_RESALE = "resale"

DEAL_TYPES = (
    (DEAL_TYPE_NEW, "New"),
    (DEAL_TYPE_DUPLICATE, "Duplicate"),
    (DEAL_TYPE_RENEWAL, "Renewal"),
    (DEAL_TYPE_DEVELOPER, "Developer"),
    (DEAL_TYPE_BUY_OUT, "Buy Out"),
    (DEAL_TYPE_REFINANCE, "Re-finance"),
    (DEAL_TYPE_RESALE, "Resale")
)

STATUS_ACTIVE = "active"
STATUS_DELETED = "deleted"
STATUS_CLIENT = "waiting for client"
STATUS_US = "waiting for us"
STATUS_BANK = "waiting for bank"

DEAL_STATUSES = (
    (STATUS_ACTIVE, "Active"),
    (STATUS_DELETED, "Deleted"),
    (STATUS_CLIENT, "Waiting for client"),
    (STATUS_US, "Waiting for us"),
    (STATUS_BANK, "Waiting for bank")
)

STATUS_DELETED_TRUE = "yes"

EXPATS_YES = "yes"
EXPATS_NO = "no"

DEAL_EXPATS = (
    (EXPATS_YES, "Yes"),
    (EXPATS_NO, "No")
)

STATUS_PAID = "paid"
STATUS_UNPAID = "unpaid"

PAYMENT_STATUSES = (
    (STATUS_PAID, "Paid"),
    (STATUS_UNPAID, "Unpaid"),
)

INSURANCE_TYPE_COMPREHENSIVE = "comprehensive"
INSURANCE_TYPE_TPL = "tpl"

INSURANCE_TYPES = (
    (INSURANCE_TYPE_COMPREHENSIVE, "Comprehensive"),
    (INSURANCE_TYPE_TPL, "Third Party Liability (TPL)"),
)

M0 = "0M"
M1 = "1M"
M3 = "3M"
M6 = "6M"
EIBOR_DURATIONS = (
    (M0, "0M"),
    (M1, "1M"),
    (M3, "3M"),
    (M6, "6M"),
)

SELECT_BANK = "Select Bank"
CONFIRM_BANK = "Confirm Bank"

WAIT_PREAPPROVAL_DOC = "Waiting for Pre Approval Documments"
SENT_TO_BANK_FOR_PREAPPROVAL = 'Sent to Bank for Approval'

WAITING_FOR_VALUATION_DOCUMENTS ="Waiting for Valuation Documents"
SENT_TO_BANK_FOR_APPROVAL = "Sent to Bank for Approval"

FOL_REQUESTED_FROM_BANK ="FOL Requested From Bank"
FOL_SIGNED = "FOL signed"

SUB_SETTLEMENT = "Settlement"
SUB_PROPERTY_TRANSFER = "Property Transfer"
SUB_PAYMENT = "Payment"

SUB_STAGES =(
    (SELECT_BANK,"select bank"),
    (CONFIRM_BANK,"confirm bank"),

    (WAIT_PREAPPROVAL_DOC,"wait preapproval doc"),
    (SENT_TO_BANK_FOR_PREAPPROVAL,"sent to bank for preapproval"),

    (WAITING_FOR_VALUATION_DOCUMENTS, 'waiting for valuation documents'),
    (SENT_TO_BANK_FOR_APPROVAL, 'sent to bank for approval'),

    (FOL_REQUESTED_FROM_BANK, 'fol request from bank'),
    (FOL_SIGNED, 'fol signed'),

    (SUB_SETTLEMENT, 'settlement'),
    (SUB_PROPERTY_TRANSFER, 'property transfer'),
    (SUB_PAYMENT, 'payment'),
)


PASSPORT = 'passport'
BANK_APPLICATION_FORM = 'bank application form'
VISA = 'visa'
SALARY_CERTIFICATE = 'salary certificate'
EMIRATES_ID_FRONT = 'emirates id front'
BANK_STATEMENT ='bank statement'
EMIRATES_ID_BACK ='emirates id back'
PAYSLIPS = 'payslips'

MEMORANDUM_OF_UNDERSTANDING ='memorandum of understanding'
PROPERTY_TITLE_DEED ='property title deed'
SELLER_EMIRATES_ID_BACK ='sellers emirates id back'
SELLERS_EMIRATES_ID_FRONT ='sellers emirates id front'
SELLERS_PASSPORT ='sellers passport'
SELLER_VISA = 'sellers visa'

DOCUMENT_NAMES = (

    (BANK_APPLICATION_FORM,'bank application form'),
    (SALARY_CERTIFICATE,'salary certificate'),
    (BANK_STATEMENT,'bank statement'),
    (PAYSLIPS,'payslips'),
    (PASSPORT,'passport'),
    (VISA,'visa'),
    (EMIRATES_ID_FRONT,'emirates id front'),
    (EMIRATES_ID_BACK,'emirates id back'),

    (MEMORANDUM_OF_UNDERSTANDING,'memorandum of understanding'),
    (PROPERTY_TITLE_DEED,'property title deed'),
    (SELLERS_PASSPORT,'sellers passport'),
    (SELLER_VISA,'sellers visa'),
    (SELLER_EMIRATES_ID_BACK,'sellers emirates id back'),
    (SELLERS_EMIRATES_ID_FRONT,'sellers emirates id front'),
)

FIXED_BANK_TYPE = 'fixed'
VARIABLE_BANK_TYPE = 'variable'
BANK_TYPE = (
    (FIXED_BANK_TYPE,'Fixed'),
    (VARIABLE_BANK_TYPE,'Variable'),
)