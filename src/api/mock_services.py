"""
Mock API Services for CRM, Credit Bureau, Offer Mart, and Document Upload
"""
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uvicorn
import os
import json
from datetime import datetime

from src.tools.crm_tools import (
    get_customer_by_id,
    get_customer_by_phone,
    get_existing_loans
)
from src.tools.credit_tools import fetch_credit_score
from src.tools.calculation_tools import generate_loan_offers


app = FastAPI(
    title="NBFC Mock API Services",
    description="Mock API services for CRM, Credit Bureau, and Document Management",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class CustomerResponse(BaseModel):
    success: bool
    customer: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class CreditScoreResponse(BaseModel):
    success: bool
    customer_id: str
    credit_score: Optional[int] = None
    credit_report_date: Optional[str] = None
    credit_history_months: Optional[int] = None
    active_accounts: Optional[int] = None
    total_outstanding: Optional[float] = None
    payment_history: Optional[str] = None
    bureau_remarks: Optional[str] = None
    error: Optional[str] = None


class OfferRequest(BaseModel):
    customer_id: str
    requested_amount: float


class DocumentUploadResponse(BaseModel):
    success: bool
    document_id: Optional[str] = None
    file_path: Optional[str] = None
    uploaded_at: Optional[str] = None
    error: Optional[str] = None


# ============================================================================
# CRM ENDPOINTS
# ============================================================================

@app.get("/api/crm/customer/{customer_id}", response_model=CustomerResponse)
async def get_customer_details(customer_id: str):
    """
    Fetch customer details from CRM.
    
    Args:
        customer_id: Customer ID
        
    Returns:
        Customer data
    """
    customer = get_customer_by_id(customer_id)
    
    if customer:
        return CustomerResponse(
            success=True,
            customer=customer
        )
    else:
        return CustomerResponse(
            success=False,
            error=f"Customer with ID {customer_id} not found"
        )


@app.get("/api/crm/customer/phone/{phone}", response_model=CustomerResponse)
async def get_customer_by_phone_number(phone: str):
    """
    Fetch customer details by phone number.
    
    Args:
        phone: Phone number
        
    Returns:
        Customer data
    """
    customer = get_customer_by_phone(phone)
    
    if customer:
        return CustomerResponse(
            success=True,
            customer=customer
        )
    else:
        return CustomerResponse(
            success=False,
            error=f"Customer with phone {phone} not found"
        )


@app.get("/api/crm/customer/{customer_id}/loans")
async def get_customer_loans(customer_id: str):
    """
    Get existing loans for a customer.
    
    Args:
        customer_id: Customer ID
        
    Returns:
        List of loans
    """
    loans = get_existing_loans(customer_id)
    
    return {
        "success": True,
        "customer_id": customer_id,
        "loans": loans,
        "total_loans": len(loans)
    }


# ============================================================================
# CREDIT BUREAU ENDPOINTS
# ============================================================================

@app.get("/api/credit-bureau/score/{customer_id}", response_model=CreditScoreResponse)
async def get_credit_score(customer_id: str):
    """
    Fetch credit score from credit bureau.
    
    Args:
        customer_id: Customer ID
        
    Returns:
        Credit score information
    """
    result = fetch_credit_score(customer_id)
    
    if result["success"]:
        return CreditScoreResponse(**result)
    else:
        return CreditScoreResponse(
            success=False,
            customer_id=customer_id,
            error=result.get("error", "Unable to fetch credit score")
        )


# ============================================================================
# OFFER MART ENDPOINTS
# ============================================================================

@app.post("/api/offers/generate")
async def generate_offers(request: OfferRequest):
    """
    Generate personalized loan offers for a customer.
    
    Args:
        request: Offer request with customer ID and amount
        
    Returns:
        List of loan offers
    """
    try:
        offers = generate_loan_offers(
            customer_id=request.customer_id,
            requested_amount=request.requested_amount
        )
        
        return {
            "success": True,
            "customer_id": request.customer_id,
            "requested_amount": request.requested_amount,
            "offers": offers,
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@app.get("/api/offers/{customer_id}")
async def get_preapproved_offers(customer_id: str):
    """
    Get pre-approved offers for a customer.
    
    Args:
        customer_id: Customer ID
        
    Returns:
        Pre-approved offer details
    """
    customer = get_customer_by_id(customer_id)
    
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    pre_approved_limit = customer.get("pre_approved_limit", 0)
    
    # Generate offers up to pre-approved limit
    offers = generate_loan_offers(customer_id, pre_approved_limit)
    
    return {
        "success": True,
        "customer_id": customer_id,
        "pre_approved_limit": pre_approved_limit,
        "offers": offers,
        "valid_until": "2025-11-22"
    }


# ============================================================================
# DOCUMENT MANAGEMENT ENDPOINTS
# ============================================================================

@app.post("/api/documents/upload", response_model=DocumentUploadResponse)
async def upload_document(
    customer_id: str,
    document_type: str,
    file: UploadFile = File(...)
):
    """
    Upload a document (e.g., salary slip).
    
    Args:
        customer_id: Customer ID
        document_type: Type of document
        file: Uploaded file
        
    Returns:
        Upload result
    """
    try:
        # Create upload directory
        upload_dir = os.path.join(
            os.path.dirname(__file__),
            f"../../data/uploads/{customer_id}"
        )
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{document_type}_{timestamp}_{file.filename}"
        file_path = os.path.join(upload_dir, filename)
        
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Generate document ID
        document_id = f"DOC_{customer_id}_{timestamp}"
        
        return DocumentUploadResponse(
            success=True,
            document_id=document_id,
            file_path=file_path,
            uploaded_at=datetime.now().isoformat()
        )
    except Exception as e:
        return DocumentUploadResponse(
            success=False,
            error=str(e)
        )


@app.get("/api/documents/download/{filename}")
async def download_document(filename: str):
    """
    Download a document.
    
    Args:
        filename: Filename to download
        
    Returns:
        File response
    """
    file_path = os.path.join(
        os.path.dirname(__file__),
        f"../../data/output/{filename}"
    )
    
    if os.path.exists(file_path):
        return FileResponse(
            file_path,
            media_type='application/pdf',
            filename=filename
        )
    else:
        raise HTTPException(status_code=404, detail="File not found")


# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "NBFC Mock API Services",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "crm": "/api/crm/*",
            "credit_bureau": "/api/credit-bureau/*",
            "offers": "/api/offers/*",
            "documents": "/api/documents/*"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("🚀 Starting Mock API Services...")
    print("📡 CRM API: http://localhost:8000/api/crm")
    print("💳 Credit Bureau API: http://localhost:8000/api/credit-bureau")
    print("🎁 Offer Mart API: http://localhost:8000/api/offers")
    print("📄 Document API: http://localhost:8000/api/documents")
    print("\n📚 API Documentation: http://localhost:8000/docs")
    
    uvicorn.run(
        "mock_services:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
