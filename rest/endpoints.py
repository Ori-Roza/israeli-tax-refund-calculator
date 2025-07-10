from fastapi import File, UploadFile, HTTPException, Form, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

from rest import app
from tax_authority_api.const import FamilyStatus
from tax_authority_api.rest import TaxSimulator
import tempfile
from tax_documents_parser import parse_106_pdf


# Set up templates directory
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/check_tax_refund")
async def check_tax_refund(
    file: UploadFile = File(...),
    tax_year: str = Form(...),
    dob_month: str = Form(...),
    dob_year: str = Form(...),
    family_status: str = Form(...),
    gender: str = Form(...),
    spouse_gender: str = Form(None),
    spouse_dob_month: str = Form(None),
    spouse_dob_year: str = Form(None),
    spouse_file: UploadFile = File(None)
):
    # Save uploaded file to a temp file
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to save file: {e}")

    personal_details = {
        'dob': {'month': dob_month, 'year': dob_year},
        'family_status': family_status,
        'gender': gender,
    }
    report_106_codes = parse_106_pdf(tmp_path)
    spouse_report_106_codes = None
    if family_status == FamilyStatus.MARRIED:
        if not spouse_file:
            raise HTTPException(status_code=400, detail="Spouse 106 document is required for married status.")
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as spouse_tmp:
                spouse_content = await spouse_file.read()
                spouse_tmp.write(spouse_content)
                spouse_tmp_path = spouse_tmp.name
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to save spouse file: {e}")

        personal_details['spouse'] = {
            'gender': spouse_gender,
            'dob': {'month': spouse_dob_month, 'year': spouse_dob_year}
        }
        spouse_report_106_codes = parse_106_pdf(spouse_tmp_path)
        # Merge or handle both report_106_codes and spouse_report_106_codes as needed
        # For now, just add to personal_details for downstream logic

    simulator = TaxSimulator(year_suffix=str(tax_year)[-2:])
    try:
        result = simulator.calculate_refund(personal_details, report_106_codes, spouse_report_106_codes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calculation failed: {e}")
    return JSONResponse(content={"result": result.model_dump() if result else None})
