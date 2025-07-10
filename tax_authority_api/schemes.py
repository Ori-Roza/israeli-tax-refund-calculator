from pydantic import BaseModel
from typing import Optional


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


