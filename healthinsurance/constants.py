import pycountry
GOVERNMENT_FEE = 4200
EXPIRED_QUOTE_EXTENSION_DAYS = 15
VAT_PERCENTAGE = 0.05
STAGE_NEW = "new"
STAGE_QUOTE = "quote"
STAGE_BASIC = "basic"
STAGE_DOCUMENTS = "documents"
STAGE_FINAL_QUOTE = "final_quote"
STAGE_PAYMENT = "payment"
STAGE_POLICY_ISSUANCE = "policy_issuance"
STAGE_HOUSE_KEEPING = "housekeeping"
STAGE_WON = "won"
STAGE_LOST = "lost"

DEAL_STAGES = (
    (STAGE_NEW, "New Deal"),
    (STAGE_QUOTE, "Quote"),
    (STAGE_BASIC, "basic"),
    (STAGE_DOCUMENTS, "Documents"),
    (STAGE_FINAL_QUOTE, "final_quote"),
    (STAGE_PAYMENT, "payment"),
    (STAGE_POLICY_ISSUANCE, "policy_issuance"),
    (STAGE_HOUSE_KEEPING, "housekeeping"),
    (STAGE_WON, "won"),
    (STAGE_LOST, "lost"),
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
STATUS_NEW = "new"
STATUS_DELETED = "deleted"
STATUS_CLIENT = "waiting for client"
STATUS_US = "waiting for us"
STATUS_INSURER = "waiting for insurer"
STATUS_COMPLIANCE = "waiting for compliance"

DEAL_STATUSES = (
    (STATUS_ACTIVE, "Active"),
    (STATUS_NEW, "New Deal"),
    (STATUS_DELETED, "Deleted"),
    (STATUS_CLIENT, "Waiting for client"),
    (STATUS_US, "Waiting for us"),
    (STATUS_INSURER, "Waiting for insurer"),
    (STATUS_COMPLIANCE, "Waiting for compliance"),
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




SELECT_BANK = "Select Bank"
CONFIRM_BANK = "Confirm Bank"

WAIT_PREAPPROVAL_DOC = "Waiting for Pre Approval Documments"
SENT_TO_BANK_FOR_PREAPPROVAL = 'Sent to Bank for Approval'

WAITING_FOR_VALUATION_DOCUMENTS ="Waiting for Valuation Documents"
SENT_TO_BANK_FOR_APPROVAL = "Sent to Bank for Approval"

FOL_REQUESTED_FROM_BANK ="FOL Requested From Bank"
FOL_SIGNED = "FOL signed"
SUBMIT_DOCUMENTS = "submit documents"
DOCUMENTS_RECEIVED = "documents received"
DOCUMENTS_SEND_TO_INSURER = "documents sent to insurer"
WORLD_CHECK = "world check"


FINAL_QUOTE_SEND_TO_CLIENT = "final quote send to client"
FINAL_QUOTE_SEND_TO_INSURER = "final quote send to insurer"
FINAL_QUOTE_SIGNED = "final quote signed"

PAYMENT_SEND_TO_CLIENT = "payment sent to client"
PAYMENT_CONFIRMATION = "payment confirmation"
PAYMENT_SEND_TO_INSURER = "payment send to insurer"

POLICY_ISSUANCE = "policy to be issued"
POLICY_ISSUANCE_SEND_EMAIL = "send policy email"
BASIC_QUOTED = "basic quoted"
BASIC_SELECTED = "basic selected"
SIGNED = "signed"




SUB_STAGES = (
    (STAGE_QUOTE,"quote"),
    (SUBMIT_DOCUMENTS,"submit documents"),
    (DOCUMENTS_RECEIVED,"documents received"),
    (DOCUMENTS_SEND_TO_INSURER,"documents sent to insurer"),
    (WORLD_CHECK,"world check"),
    
    (FINAL_QUOTE_SEND_TO_CLIENT,"final quote send to client"),
    (FINAL_QUOTE_SIGNED,"final quote signed"),
    (FINAL_QUOTE_SEND_TO_INSURER,"final quote send to insurer"),

    (PAYMENT_SEND_TO_CLIENT, "payment sent to client"),
    (PAYMENT_CONFIRMATION, "payment confirmation"),
    (PAYMENT_SEND_TO_INSURER, "payment send to insurer"),
    (PAYMENT_SEND_TO_INSURER, "payment send to insurer"),

    (POLICY_ISSUANCE_SEND_EMAIL,"send policy email")

)


PASSPORT = 'passport'
BANK_APPLICATION_FORM = 'bank application form'
VISA = 'visa'
SALARY_CERTIFICATE = 'salary certificate'
EMIRATES_ID_FRONT = 'emirates id front'
BANK_STATEMENT ='bank statement'
EMIRATES_ID_BACK ='emirates id back'
PAYSLIPS = 'payslips'



SELLER_EMIRATES_ID_BACK ='sellers emirates id back'
SELLERS_EMIRATES_ID_FRONT ='sellers emirates id front'
SELLERS_PASSPORT ='sellers passport'
SELLER_VISA = 'sellers visa'

DOCUMENT_NAMES = (
    (BANK_STATEMENT,'bank statement'),
    (PAYSLIPS,'payslips'),
    (PASSPORT,'passport'),
    (VISA,'visa'),
    (EMIRATES_ID_FRONT,'emirates id front'),
    (EMIRATES_ID_BACK,'emirates id back'),

    
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

COMPREHENSIVE = 'comprehensive'
BASIC = 'basic'

LEVEL_OF_COVER = (
    (COMPREHENSIVE, 'comprehensive'),
    (BASIC, 'basic'),
)

SON = 'son'
MOTHER = 'mother'
FATHER = 'father'
DAUGHTER = 'daughter'
SPOUSE = 'spouse'

MEMBER_RELATIONS = (
    (FATHER,'father'),
    (MOTHER,'mother'),
    (SPOUSE,'spouse'),
    (SON,'son'),
    (DAUGHTER,'daughter'),
)


LOCAL = 'local'
REGIONAL = 'regional'
WORLDWIDE_EXCEPT_US = 'worldwide_except_us'
WORLDWIDE = 'worldwide'


GEOGRAPHICAL_COVERAGE = (
    (LOCAL, 'Local'),
    (REGIONAL, 'Regional'),
    (WORLDWIDE_EXCEPT_US, 'Worldwide Except US'),
    (WORLDWIDE, 'Worldwide'),
)

HEALTH_SCREEN = 'Health Screen'
DENTAL = 'Dental'
OTHER = 'Other'

ADDITIONAL_BENEFITS = (
    (HEALTH_SCREEN, 'Health Screen'),
    (DENTAL, 'Dental'),
    (OTHER, 'Other'),
)

BELOW1K = 'Below 1k'
BELOW4K = 'Below 4k'
FROM2TO4K = '2-4k'
FROM4TO8K = '4-8k'
ABOVE8K = 'Above 8k'
NOTSURE = 'Not Sure'

BUDGET = (
(BELOW1K,'Below 1k'),
(BELOW4K,'Below 4k'),
(FROM2TO4K,'2-4k'),
(FROM4TO8K,'4-8k'),
(ABOVE8K,'Above 8k'),
(NOTSURE,'Not Sure'),
)
ABOVE_4K = 'above_4k'
BELOW_4K = 'below_4k'

SALARY_BAND = (
    (ABOVE_4K, 'above_4k'),
    (BELOW_4K, 'below_4k'),
    ("", ''),
)

EMIRATE_DUBAI = "Dubai"
EMIRATE_ABU_DHABI = "Abu Dhabi"
EMIRATE_SHARJAH = "Sharjah"
EMIRATE_AJMAN = "Ajman"
EMIRATE_RAS_AL_KHAIMAH = "Ras Al Khaimah"
EMIRATE_FUJAIRAH = "Fujairah"
EMIRATE_UMM_AL_QUWAIN = "Umm Al Quwain"

EMIRATES_LIST = (
    (EMIRATE_DUBAI, "Dubai"),
    (EMIRATE_ABU_DHABI, "Abu Dhabi"),
    (EMIRATE_SHARJAH, "Sharjah"),
    (EMIRATE_AJMAN, "Ajman"),
    (EMIRATE_RAS_AL_KHAIMAH, "Ras Al Khaimah"),
    (EMIRATE_FUJAIRAH, "Fujairah"),
    (EMIRATE_UMM_AL_QUWAIN, "Umm Al Quwain"),
)


VARIABLE = 'Variable'
SAME_ON_ALL_COPAY = 'Same on all copay'
#NOT_APPLICABLE = 'N/A'

COPAY_MODE = (
(VARIABLE, 'Variable'),
(SAME_ON_ALL_COPAY, 'Same on all copay')
)

YES = 'yes'
NO = 'no'
PENDING = 'pending'

WORLD_CHECK_APPROVED = (
    (YES,'yes'),
    (NO,'no'),
    (PENDING,'pending'),
)



