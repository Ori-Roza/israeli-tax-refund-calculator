from pydantic import BaseModel
from typing import Optional, Dict, Any


class TaxComponent(BaseModel):
    partner_value: Optional[float] = None
    spouse_value: Optional[float] = None
    total_value: Optional[float] = None


class TaxResult(BaseModel):
    total_income: Optional[TaxComponent] = None
    total_deductions: Optional[TaxComponent] = None
    taxable_income: Optional[TaxComponent] = None
    gross_tax: Optional[TaxComponent] = None
    resident_credit: Optional[TaxComponent] = None
    total_credits: Optional[TaxComponent] = None
    final_tax_due: Optional[TaxComponent] = None
    withholding_tax: Optional[TaxComponent] = None
    tax_after_withholding: Optional[TaxComponent] = None
    credit_45a: Optional[TaxComponent] = None
    woman_credit: Optional[TaxComponent] = None


class PersonalDetails(BaseModel):
    dob: Dict[str, int]  # {'month': int, 'year': int}
    family_status: Optional[Any] = None   # Should be FamilyStatus, but keeping Any for flexibility
    gender: str
    spouse: Optional[Dict[str, Any]] = None  # {'dob': {'month': int, 'year': int}, 'gender': str}



class Report106Codes(BaseModel):
    codes: Dict[str, Any]  # code: value


class SpouseReport106Codes(BaseModel):
    codes: Dict[str, Any]  # code: value
