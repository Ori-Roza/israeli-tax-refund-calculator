import uvicorn
from rest import app

from rest.endpoints import check_tax_refund

# All endpoints are now imported from rest.endpoints

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)