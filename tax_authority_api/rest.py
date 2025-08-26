from typing import Optional

import requests
from bs4 import BeautifulSoup
from loguru import logger

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
        logger.info(f"TaxSimulator initialized for year 20{year_suffix}")

    def prepare_form(self, personal_details: PersonalDetails, report_106_codes: Report106Codes):
        logger.debug(f"Preparing form for tax calculation - Family status: {personal_details.family_status}")

        # Initialize session and get form
        logger.debug("Fetching main page and year-specific page")
        self.session.get(self.main_url)
        res = self.session.get(self.year_page)

        if res.status_code != 200:
            logger.error(f"Failed to fetch year page: {res.status_code}")
            raise Exception(f"Failed to fetch year page: {res.status_code}")

        logger.debug("Parsing form data from tax authority website")
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
        logger.debug(f"Added personal details to form - DOB: {personal_details.dob['month']}/{personal_details.dob['year']}")

        # Handle spouse details if applicable
        if personal_details.family_status == FamilyStatus.MARRIED and personal_details.spouse:
            logger.debug("Adding spouse details for married couple")
            form_data.update({
                'ctl00$ctl00$ContentUsersPage$ChildContent1$chk021': 'on',
                'ctl00$ctl00$ContentUsersPage$ChildContent1$ledambz': personal_details.spouse['dob']['month'],
                'ctl00$ctl00$ContentUsersPage$ChildContent1$ledabz': personal_details.spouse['dob']['year'],
                'ctl00$ctl00$ContentUsersPage$ChildContent1$sexbz': f"{personal_details.spouse['gender']}bz"
            })

        # Add salary data
        logger.debug(f"Adding {len(report_106_codes.codes)} tax codes to form")
        for code, value in report_106_codes.codes.items():
            field_name = f'ctl00$ctl00$ContentUsersPage$ChildContent1$txt{code}'
            form_data[field_name] = value
            logger.debug(f"Added tax code {code}: {value}")

        logger.info("Form preparation completed successfully")
        return form_data

    def submit(self, form_data: dict) -> str:
        logger.info(f"Submitting form to tax authority website: {self.year_page}")
        response = self.session.post(self.year_page, data=form_data)

        if response.status_code != 200:
            logger.error(f"Failed to submit form: HTTP {response.status_code}")
            raise Exception(f"Failed to submit form: {response.status_code}")

        logger.success("Form submitted successfully to tax authority")
        logger.debug(f"Response length: {len(response.text)} characters")
        return response.text

    def calculate_refund(self,
                         personal_details: PersonalDetails,
                         report_106_codes: Report106Codes,
                         spouse_report_106_codes: Optional[SpouseReport106Codes]) -> TaxResult | None:

        logger.info(f"Starting tax refund calculation for {personal_details.family_status} person")

        if personal_details.family_status == FamilyStatus.SINGLE:
            logger.debug("Processing single person - filtering out spouse-specific tax codes")
            original_count = len(report_106_codes.codes)
            report_106_codes.codes = {code: value for code, value in report_106_codes.codes.items() if
                                   code not in TAX_CODES_FOR_SPOUSE}
            filtered_count = len(report_106_codes.codes)
            logger.debug(f"Filtered tax codes: {original_count} -> {filtered_count} (removed {original_count - filtered_count} spouse codes)")

        elif personal_details.family_status == FamilyStatus.MARRIED:
            if not spouse_report_106_codes:
                logger.error("Married status requires spouse report codes but none provided")
                raise ValueError("Spouse report codes required for married status")

            logger.debug("Processing married couple - merging spouse tax codes")
            spouse_original_count = len(spouse_report_106_codes.codes)
            spouse_report_106_codes.codes = {code: value for code, value in spouse_report_106_codes.codes.items() if
                                   code in TAX_CODES_FOR_SPOUSE}
            spouse_filtered_count = len(spouse_report_106_codes.codes)
            logger.debug(f"Spouse tax codes: {spouse_original_count} -> {spouse_filtered_count}")

            # merging spouse codes if applicable
            main_codes_count = len(report_106_codes.codes)
            report_106_codes.codes.update(spouse_report_106_codes.codes)
            final_count = len(report_106_codes.codes)
            logger.debug(f"Merged codes: {main_codes_count} + {spouse_filtered_count} = {final_count}")

        try:
            data = self.prepare_form(personal_details, report_106_codes)
            response = self.submit(data)
            result = parse_tax_results(response)

            if result:
                logger.success("Tax refund calculation completed successfully")
            else:
                logger.warning("Tax calculation returned no results")

            return result

        except Exception as e:
            logger.error(f"Tax calculation failed: {e}")
            logger.exception("Full exception details:")
            raise
