"""
Document Generation and Management Tools
"""
import os
from typing import Dict, Any
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_JUSTIFY
from src.tools.crm_tools import get_customer_by_id


def generate_sanction_letter(
    customer_id: str,
    loan_amount: float,
    tenure_months: int,
    interest_rate: float,
    monthly_emi: float
) -> Dict[str, Any]:
    """
    Generate PDF sanction letter for approved loan.
    
    Args:
        customer_id: Customer ID
        loan_amount: Approved loan amount
        tenure_months: Loan tenure in months
        interest_rate: Annual interest rate
        monthly_emi: Monthly EMI amount
        
    Returns:
        Document generation result with file path
    """
    customer = get_customer_by_id(customer_id)
    
    if not customer:
        return {
            "success": False,
            "error": "Customer not found"
        }
    
    # Generate reference number
    ref_no = f"SL/{datetime.now().strftime('%Y%m%d')}/{customer_id}"
    
    # Create output directory if it doesn't exist
    output_dir = os.path.join(
        os.path.dirname(__file__),
        "../../data/output"
    )
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate filename
    filename = f"sanction_letter_{customer_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    filepath = os.path.join(output_dir, filename)
    
    # Create PDF
    doc = SimpleDocTemplate(filepath, pagesize=A4)
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#1e3a8a'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#4b5563'),
        spaceAfter=20,
        alignment=TA_RIGHT
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=12,
        alignment=TA_JUSTIFY
    )
    
    # Add company header
    story.append(Paragraph("FINTECH NBFC LIMITED", title_style))
    story.append(Paragraph(
        "Registered Office: 123 Financial District, Mumbai 400001<br/>"
        "CIN: U65999MH2020PLC123456 | www.fintechnbfc.com",
        header_style
    ))
    story.append(Spacer(1, 0.3 * inch))
    
    # Add reference and date
    story.append(Paragraph(f"<b>Reference No:</b> {ref_no}", body_style))
    story.append(Paragraph(f"<b>Date:</b> {datetime.now().strftime('%d %B %Y')}", body_style))
    story.append(Spacer(1, 0.3 * inch))
    
    # Add customer details
    story.append(Paragraph(f"<b>To,</b>", body_style))
    story.append(Paragraph(f"{customer['name']}", body_style))
    story.append(Paragraph(f"{customer['address']}", body_style))
    story.append(Paragraph(f"Email: {customer['email']}", body_style))
    story.append(Paragraph(f"Phone: {customer['phone']}", body_style))
    story.append(Spacer(1, 0.3 * inch))
    
    # Add subject
    story.append(Paragraph(
        "<b>Subject: Sanction of Personal Loan</b>",
        ParagraphStyle('Subject', parent=body_style, fontSize=12, textColor=colors.HexColor('#1e3a8a'))
    ))
    story.append(Spacer(1, 0.2 * inch))
    
    # Add greeting
    story.append(Paragraph(f"Dear {customer['name'].split()[0]},", body_style))
    story.append(Spacer(1, 0.1 * inch))
    
    # Add body
    story.append(Paragraph(
        "We are pleased to inform you that your personal loan application has been approved. "
        "We appreciate your trust in FinTech NBFC Limited and are committed to providing you "
        "with the best financial services.",
        body_style
    ))
    story.append(Spacer(1, 0.2 * inch))
    
    # Loan details table
    total_interest = (monthly_emi * tenure_months) - loan_amount
    total_payable = loan_amount + total_interest
    processing_fee = loan_amount * 0.02
    validity_date = (datetime.now() + timedelta(days=30)).strftime('%d %B %Y')
    
    loan_details = [
        ['Loan Details', ''],
        ['Loan Amount Sanctioned', f'₹{loan_amount:,.2f}'],
        ['Interest Rate (Per Annum)', f'{interest_rate * 100:.2f}%'],
        ['Loan Tenure', f'{tenure_months} months ({tenure_months // 12} years)'],
        ['Monthly EMI', f'₹{monthly_emi:,.2f}'],
        ['Processing Fee', f'₹{processing_fee:,.2f}'],
        ['Total Interest', f'₹{total_interest:,.2f}'],
        ['Total Amount Payable', f'₹{total_payable:,.2f}'],
        ['Sanction Valid Until', validity_date],
    ]
    
    table = Table(loan_details, colWidths=[3.5 * inch, 2.5 * inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f3f4f6')]),
    ]))
    
    story.append(table)
    story.append(Spacer(1, 0.3 * inch))
    
    # Terms and conditions
    story.append(Paragraph("<b>Terms and Conditions:</b>", body_style))
    story.append(Spacer(1, 0.1 * inch))
    
    terms = [
        "This sanction is valid for 30 days from the date of this letter.",
        "The loan will be disbursed upon completion of documentation and verification.",
        "EMI payments must be made on or before the due date to avoid penal charges.",
        "Prepayment of the loan is allowed with applicable charges as per policy.",
        "The loan is subject to the terms and conditions specified in the loan agreement.",
        "All applicable taxes and charges are to be borne by the borrower.",
        "The interest rate is fixed for the entire tenure of the loan.",
        "The loan is for personal use only and cannot be used for speculative purposes."
    ]
    
    for i, term in enumerate(terms, 1):
        story.append(Paragraph(f"{i}. {term}", body_style))
    
    story.append(Spacer(1, 0.3 * inch))
    
    # Closing
    story.append(Paragraph(
        "Please visit our nearest branch or contact our customer service team to complete "
        "the documentation process. We look forward to serving you.",
        body_style
    ))
    story.append(Spacer(1, 0.2 * inch))
    
    story.append(Paragraph("Thank you for choosing FinTech NBFC Limited.", body_style))
    story.append(Spacer(1, 0.4 * inch))
    
    story.append(Paragraph("<b>For FinTech NBFC Limited</b>", body_style))
    story.append(Spacer(1, 0.5 * inch))
    story.append(Paragraph("<b>Authorized Signatory</b>", body_style))
    
    # Build PDF
    doc.build(story)
    
    return {
        "success": True,
        "reference_number": ref_no,
        "file_path": filepath,
        "filename": filename,
        "generated_at": datetime.now().isoformat(),
        "validity_date": validity_date
    }


def save_uploaded_document(
    customer_id: str,
    document_type: str,
    file_content: bytes,
    filename: str
) -> Dict[str, Any]:
    """
    Save uploaded document (e.g., salary slip).
    
    Args:
        customer_id: Customer ID
        document_type: Type of document (salary_slip, id_proof, etc.)
        file_content: Binary content of the file
        filename: Original filename
        
    Returns:
        Save result with file path
    """
    # Create upload directory
    upload_dir = os.path.join(
        os.path.dirname(__file__),
        f"../../data/uploads/{customer_id}"
    )
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate safe filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    safe_filename = f"{document_type}_{timestamp}_{filename}"
    filepath = os.path.join(upload_dir, safe_filename)
    
    # Save file
    with open(filepath, 'wb') as f:
        f.write(file_content)
    
    return {
        "success": True,
        "document_type": document_type,
        "file_path": filepath,
        "filename": safe_filename,
        "uploaded_at": datetime.now().isoformat()
    }


def get_document_download_url(filepath: str) -> str:
    """
    Generate download URL for a document.
    
    Args:
        filepath: File path
        
    Returns:
        Download URL
    """
    # In production, this would be a proper URL
    # For demo, we'll return a local file path
    filename = os.path.basename(filepath)
    return f"/api/documents/download/{filename}"
