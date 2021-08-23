LEAD_TYPES_USED_CAR = "used"
LEAD_TYPES_OWN_CAR = "own"
LEAD_TYPES_NEW_CAR = "new"

LEAD_TYPES = [
    (LEAD_TYPES_OWN_CAR, "To renew your car's insurance policy"),
    (LEAD_TYPES_USED_CAR, "To insure a used car you're buying"),
    (LEAD_TYPES_NEW_CAR, "To insure a brand new car you're buying"),
]

TOP_TIER_INSURER_OTHER = "other"
INSURER_AXA = "axa"
INSURER_DAT = "dat"
INSURER_DI = "di"
INSURER_EIC = "eic"
INSURER_IH = "ih"
INSURER_OIC = "oic"
INSURER_QIC = "qic"
INSURER_RSA = "rsa"
INSURER_UI = "ui"
INSURER_TOKIO = "tokio-marine"
INSURER_NOOR_TAKAFUL = "noor-takaful"

TOP_TIER_INSURERS = [
    (INSURER_AXA, "AXA Gulf"),
    (INSURER_DAT, "Dar Al Takaful"),
    (INSURER_DI, "Dubai Insurance"),
    (INSURER_EIC, "Emirates Insurance Co"),
    (INSURER_IH, "Insurance House"),
    (INSURER_NOOR_TAKAFUL, "Noor Takaful"),
    (INSURER_OIC, "Oman Insurance Co"),
    (INSURER_QIC, "Qatar Insurance Co"),
    (INSURER_RSA, "Royal & Sun Alliance (RSA)"),
    (INSURER_TOKIO, "Tokio Marine"),
    (INSURER_UI, "Union Insurance"),
    (TOP_TIER_INSURER_OTHER, "OTHER"),
]

INSURANCE_TYPE_COMPREHENSIVE = 'comprehensive'
INSURANCE_TYPE_TPL = 'tpl'

INSURANCE_TYPES = [
    (INSURANCE_TYPE_COMPREHENSIVE, "Comprehensive"),
    (INSURANCE_TYPE_TPL, "Third Party Liability (TPL)"),
]

EMIRATES_LIST = [
    ("DU", "Dubai"),
    ("AD", "Abu Dhabi"),
    ("SJ", "Sharjah"),
    ("AJ", "Ajman"),
    ("RK", "Ras Al Khaimah"),
    ("FJ", "Fujairah"),
    ("UQ", "Umm Al Quwain"),
]

LICENSE_AGE_LIST = [
    ("less than 6 months", "Less than 6 months"),
    ("less than 1 year", "Less than 1 year"),
    ("less than 2 years", "Less than 2 years"),
    ("more than 2 years", "More than 2 years"),
]

NO_CLAIMS_CANT_REMEMBER = "unknown"
NO_CLAIMS_THIS_YEAR = "this year"
NO_CLAIMS = [
    (NO_CLAIMS_CANT_REMEMBER, "I can't remember or don't know"),
    ("never", "I've never made a claim"),
    (NO_CLAIMS_THIS_YEAR, "I made a claim in the last 12 months"),
    ("last year", "I last made a claim over 1 year ago"),
    ("2 years ago", "Over 2 years ago"),
    ("3 years ago", "Over 3 years ago"),
    ("4 years ago", "Over 4 years ago"),
    ("5 years or more", "Over 5 years ago"),
]
