import re
import cv2
import numpy as np
from PIL import Image

from tax_authority_api.const import TAX_CODES


def preprocess_image(pil_image):
    img = np.array(pil_image.convert('L'))
    _, thresh = cv2.threshold(img, 180, 255, cv2.THRESH_BINARY)
    return Image.fromarray(thresh)


def extract_values_from_text(ocr_text: str, codes: list[list[str]]) -> dict:
    code_values = {}

    for line in ocr_text.splitlines():
        # Extract all numbers (left to right)
        numbers = re.findall(r'([\d,]+\.\d{2}|[\d,]+)', line)
        numbers = [str(n.replace(',', '')) for n in numbers if n != ',']

        if not numbers:
            continue

        i = len(numbers) - 1  # reading RTL
        while i > 0:
            if {numbers[i], numbers[i - 1]} == {TAX_CODES.CODE_059, TAX_CODES.CODE_068}:
                code_values[TAX_CODES.CODE_068] = numbers[i - 2]
                code_values[TAX_CODES.CODE_069] = numbers[i - 2]
                i -= 3
                continue
            if {numbers[i], numbers[i - 1]} == {TAX_CODES.CODE_089, TAX_CODES.CODE_030}:
                code_values[TAX_CODES.CODE_089] = numbers[i - 2]
                code_values[TAX_CODES.CODE_030] = numbers[i - 2]
                i -= 3
                continue
            if {numbers[i], numbers[i - 1]} == {TAX_CODES.CODE_109, TAX_CODES.CODE_309}:
                try:
                    assert i - 3 >= 0
                    code_values[TAX_CODES.CODE_109] = numbers[i - 3]
                    code_values[TAX_CODES.CODE_309] = numbers[i - 3]
                except:
                    code_values[TAX_CODES.CODE_109] = 0
                    code_values[TAX_CODES.CODE_309] = 0
                i -= 3
                continue
            if numbers[i] == TAX_CODES.CODE_38:
                code_values[TAX_CODES.CODE_36] = numbers[i - 1]
                i -= 2
                continue
            if numbers[i] == TAX_CODES.CODE_082:
                code_values[TAX_CODES.CODE_042] = numbers[i - 1]
                i -= 2
                continue
            if [numbers[i]] in codes:
                j = i - 1
                while j >= 0:
                    if int(numbers[j]) < 1000:
                        j -= 1
                    else:
                        break
                code_values[numbers[i]] = numbers[j]
                i -= 2
            elif any([{numbers[i], numbers[i - 1]} == set(pair) for pair in codes]):
                j = i - 2
                while j >= 0:
                    if int(numbers[j]) < 1000:
                        j -= 1
                    else:
                        break
                code_values[numbers[i]] = numbers[j]
                code_values[numbers[i - 1]] = numbers[j]
                i -= 3
            else:
                i -= 1

    for code, value in code_values.items():
        if code == value:
            code_values[code] = "-1"
        else:
            try:
                code_values[code] = str(int(value))
            except ValueError:
                code_values[code] = value.replace(',', '')

    new_codes = {}
    # deletes keys with -1 or 0
    for code in code_values:
        if code_values[code] != "-1" and code_values[code] != "0":
            new_codes[code] = code_values[code]

    return new_codes
