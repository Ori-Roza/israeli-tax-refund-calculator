from typing import Optional

import requests
from bs4 import BeautifulSoup

from tax_authority_api.const import MAIN_URL, YEAR_PAGE, TAX_CODES_FOR_SPOUSE, FamilyStatus
from tax_authority_api.schemes import TaxResult, PersonalDetails, Report106Codes, SpouseReport106Codes
from tax_authority_api.utils import parse_tax_results


class TaxSimulator:
    def __init__(self, year_suffix):
        self.main_url = MAIN_URL
        self.year_page = YEAR_PAGE.format(year_suffix=year_suffix)
        self.year_suffix = year_suffix
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Referer': self.main_url,
        })

    def prepare_form(self, personal_details: PersonalDetails, report_106_codes: Report106Codes):
        # Initialize session and get form
        self.session.get(self.main_url)
        res = self.session.get(self.year_page)
        soup = BeautifulSoup(res.text, 'html.parser')
        form_data = {
            tag['name']: tag.get('value', '')
            for tag in soup.select('input[name]')
        }
        # Fill in personal details
        form_data.update({
            'ctl00$ctl00$ContentUsersPage$ChildContent1$ledambzr': personal_details.dob['month'],
            'ctl00$ctl00$ContentUsersPage$ChildContent1$ledabzr': personal_details.dob['year'],
            'ctl00$ctl00$ContentUsersPage$ChildContent1$mish': personal_details.family_status,
            'ctl00$ctl00$ContentUsersPage$ChildContent1$sex': personal_details.gender,
            'ctl00$ctl00$ContentUsersPage$ChildContent1$okHidden': 'ok',
            'ctl00$ctl00$ContentUsersPage$ChildContent1$chk020': 'on',
            f'ctl00$ctl00$ContentUsersPage$ChildContent1$CNTCurrYear': f"20{self.year_suffix}",
            f'ctl00$ctl00$ContentUsersPage$ChildContent1$CookieNameFake': f"{self.year_suffix}_Fake",
            f'ctl00$ctl00$ContentUsersPage$ChildContent1$CookieName': f"{self.year_suffix}_doch",
        })
        # Handle spouse details if applicable
        if personal_details.family_status == FamilyStatus.MARRIED and personal_details.spouse:
            form_data.update({
                'ctl00$ctl00$ContentUsersPage$ChildContent1$chk021': 'on',
                'ctl00$ctl00$ContentUsersPage$ChildContent1$ledambz': personal_details.spouse['dob']['month'],
                'ctl00$ctl00$ContentUsersPage$ChildContent1$ledabz': personal_details.spouse['dob']['year'],
                'ctl00$ctl00$ContentUsersPage$ChildContent1$sexbz': f"{personal_details.spouse['gender']}bz"
            })
        # Add salary data
        for code, value in report_106_codes.codes.items():
            field_name = f'ctl00$ctl00$ContentUsersPage$ChildContent1$txt{code}'
            form_data[field_name] = value
        return form_data

    def submit(self, form_data: dict) -> str:
        response = self.session.post(self.year_page, data=form_data)
        if response.status_code != 200:
            raise Exception(f"Failed to submit form: {response.status_code}")
        return response.text

    def calculate_refund(self,
                         personal_details: PersonalDetails,
                         report_106_codes: Report106Codes,
                         spouse_report_106_codes: Optional[SpouseReport106Codes]) -> TaxResult | None:
        if personal_details.family_status == FamilyStatus.SINGLE:
            report_106_codes.codes = {code: value for code, value in report_106_codes.codes.items() if
                                   code not in TAX_CODES_FOR_SPOUSE}
        elif personal_details.family_status == FamilyStatus.MARRIED:
            spouse_report_106_codes.codes = {code: value for code, value in spouse_report_106_codes.codes.items() if
                                   code in TAX_CODES_FOR_SPOUSE}
            # merging spouse codes if applicable
            if personal_details.family_status == FamilyStatus.MARRIED:
                report_106_codes.codes.update(spouse_report_106_codes.codes)

        data = self.prepare_form(personal_details, report_106_codes)
        response = self.submit(data)
        return parse_tax_results(response)
