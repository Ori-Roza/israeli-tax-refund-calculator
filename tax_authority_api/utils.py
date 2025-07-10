import re

from bs4 import BeautifulSoup

from tax_authority_api.const import HEBREW_TO_ENGLISH
from tax_authority_api.schemes import TaxResult


def parse_number(val: str) -> float | None:
    val = val.replace(",", "").replace("−", "-").strip()
    return float(val) if re.match(r'^-?\d+(\.\d+)?$', val) else None


def parse_tax_results(text: str) -> TaxResult | None:
    # Parse HTML
    soup = BeautifulSoup(text, 'html.parser')
    inner_table = soup.find("table", {"id": "dgResult"})
    result = {}

    if inner_table:
        rows = inner_table.find_all("tr")[1:]  # Skip header
        for row in rows:
            cols = row.find_all("td")
            if len(cols) == 4:
                partner = cols[0].get_text(strip=True).replace('\xa0', '')
                spouse = cols[1].get_text(strip=True).replace('\xa0', '')
                total = cols[2].get_text(strip=True).replace('\xa0', '')
                component_he = cols[3].get_text(strip=True)

                key = HEBREW_TO_ENGLISH.get(component_he, component_he)  # Use English if known, else Hebrew

                result[key] = {
                    "partner_value": parse_number(partner),
                    "spouse_value": parse_number(spouse),
                    "total_value": parse_number(total)
                }
    return TaxResult(**result)
