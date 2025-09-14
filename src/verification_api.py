from fastapi import FastAPI, Header
from typing import Optional
from pydantic import BaseModel

app = FastAPI(title='TaskOn Verification API Demo (Embedded)')

class VerificationResponse(BaseModel):
    result: dict
    error: Optional[str] = None

DEMO_COMPLETED = {
    '0x742d35Cc6634C0532925a3b844Bc454e4438f44e'.lower(),
    'taskonxyz',
}

@app.get('/api/task/verification', response_model=VerificationResponse)
async def verify(address: str, authorization: Optional[str] = Header(None)):
    is_valid = address.lower() in DEMO_COMPLETED
    return VerificationResponse(result={'isValid': is_valid}, error=None)
