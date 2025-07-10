from dataclasses import dataclass

BASE_URL = "https://secapp.taxes.gov.il/shsimulatormas"
MAIN_URL = f"{BASE_URL}/main.aspx"
YEAR_PAGE = f"{BASE_URL}/DochSchirim{{year_suffix}}.aspx"


@dataclass(frozen=True)
class TAX_CODES:
    CODE_150: str = "150"
    CODE_170: str = "170"
    CODE_158: str = "158"
    CODE_172: str = "172"
    CODE_196: str = "196"
    CODE_270: str = "270"
    CODE_272: str = "272"
    CODE_258: str = "258"
    CODE_069: str = "069"
    CODE_068: str = "068"
    CODE_059: str = "059"
    CODE_109: str = "109"
    CODE_309: str = "309"
    CODE_34: str = "34"
    CODE_36: str = "36"
    CODE_38: str = "38"
    CODE_245: str = "245"
    CODE_244: str = "244"
    CODE_237: str = "237"
    CODE_037: str = "037"
    CODE_249: str = "249"
    CODE_248: str = "248"
    CODE_313: str = "313"
    CODE_219: str = "219"
    CODE_218: str = "218"
    CODE_042: str = "042"
    CODE_089: str = "089"
    CODE_030: str = "030"
    CODE_086: str = "086"
    CODE_045: str = "045"
    CODE_180: str = "180"
    CODE_135: str = "135"
    CODE_082: str = "082"


# Grouped codes for logic (as list of lists)
TAX_CODES_GROUPS = [
    [TAX_CODES.CODE_158, TAX_CODES.CODE_172],
    [TAX_CODES.CODE_272, TAX_CODES.CODE_258],
    [TAX_CODES.CODE_069, TAX_CODES.CODE_068],
    [TAX_CODES.CODE_109, TAX_CODES.CODE_309],
    [TAX_CODES.CODE_34],
    [TAX_CODES.CODE_36],
    [TAX_CODES.CODE_245, TAX_CODES.CODE_244],
    [TAX_CODES.CODE_237, TAX_CODES.CODE_037],
    [TAX_CODES.CODE_249, TAX_CODES.CODE_248],
    [TAX_CODES.CODE_219, TAX_CODES.CODE_218],
    [TAX_CODES.CODE_042],
    [TAX_CODES.CODE_089, TAX_CODES.CODE_030],
    [TAX_CODES.CODE_086, TAX_CODES.CODE_045],
    [TAX_CODES.CODE_180, TAX_CODES.CODE_135],
]

TAX_CODES_FOR_SPOUSE = [TAX_CODES.CODE_170, TAX_CODES.CODE_069,
                        TAX_CODES.CODE_270, TAX_CODES.CODE_196,
                        TAX_CODES.CODE_172, TAX_CODES.CODE_313,
                        TAX_CODES.CODE_272, TAX_CODES.CODE_245,
                        TAX_CODES.CODE_249, TAX_CODES.CODE_219
                        ]

HEBREW_TO_ENGLISH = {
    "סה\"כ הכנסות": "total_income",
    "סה''כ  ניכויים": "total_deductions",
    "הכנסה חייבת": "taxable_income",
    "מס ברוטו": "gross_tax",
    "זיכוי תושב": "resident_credit",
    "זיכוי אישה": "woman_credit",
    "זיכוי 45.א": "credit_45a",
    "סה''כ  זיכויים": "total_credits",
    "מס מגיע": "final_tax_due",
    "ניכויים במקור": "withholding_tax",
    "מס לאחר ניכוי במקור": "tax_after_withholding",
}

SPECIAL_ATTRIBUTES = {
    "זיכוי תושב": "resident_credit",
    "זיכוי אישה": "woman_credit",
    "זיכוי 45.א": "credit_45a",
}

class FamilyStatus:
    SINGLE = "ravak"
    MARRIED = "nasui"

    @classmethod
    def choices(cls):
        return [cls.RAVAK, cls.NASUI]