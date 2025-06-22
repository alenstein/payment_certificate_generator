import io
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch
from datetime import datetime


def generate_certificate_pdf(project, certificate, calculations):
    """Generate PDF for certificate"""
    # Create the HttpResponse object with PDF headers
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="certificate_{certificate.id}.pdf"'
    
    # Create the PDF object
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    heading_style = styles['Heading2']
    normal_style = styles['Normal']
    
    # Add title
    title = Paragraph("PAYMENT CERTIFICATE", title_style)
    elements.append(title)
    elements.append(Spacer(1, 12))
    
    # Add certificate info
    cert_info = Paragraph(f"Certificate #{certificate.id}", normal_style)
    elements.append(cert_info)
    elements.append(Spacer(1, 12))
    
    # Project details section
    project_heading = Paragraph("Project Details", heading_style)
    elements.append(project_heading)
    elements.append(Spacer(1, 6))
    
    project_data = [
        ['Contractor:', project.name_of_contractor],
        ['Contract No:', project.contract_no],
        ['Vote No:', project.vote_no],
        ['Tender Sum:', f"{certificate.currency} {project.tender_sum:,.2f}"],
        ['Currency:', certificate.currency],
        ['Date:', datetime.now().strftime('%B %d, %Y')],
    ]
    
    project_table = Table(project_data, colWidths=[2*inch, 4*inch])
    project_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    elements.append(project_table)
    elements.append(Spacer(1, 20))
    
    # Certificate summary section
    summary_heading = Paragraph("Certificate Summary", heading_style)
    elements.append(summary_heading)
    elements.append(Spacer(1, 6))
    
    summary_data = [
        ['Description', f'Amount ({certificate.currency})'],
        ['Current Claim (Excl. VAT)', f'{certificate.current_claim_excl_vat:,.2f}'],
        ['VAT (15%)', f'{certificate.vat_value:,.2f}'],
        ['Previous Payment (Excl. VAT)', f'{certificate.previous_payment_excl_vat:,.2f}'],
        ['Value of Work Done (Incl. VAT)', f'{calculations.value_of_workdone_incl_vat:,.2f}'],
        ['Total Value of Work Done (Excl. VAT)', f'{calculations.total_value_of_workdone_excl_vat:,.2f}'],
        ['Retention (10%)', f'{calculations.retention:,.2f}'],
        ['Total Amount Payable', f'{calculations.total_amount_payable:,.2f}'],
    ]
    
    summary_table = Table(summary_data, colWidths=[4*inch, 2*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(summary_table)
    elements.append(Spacer(1, 30))
    
    # Approval section
    approval_heading = Paragraph("Approval", heading_style)
    elements.append(approval_heading)
    elements.append(Spacer(1, 20))
    
    approval_data = [
        ['_' * 30, '_' * 30],
        ['Authorized Signature', 'Authorized Signature'],
        ['Project Manager', 'Finance Officer'],
    ]
    
    approval_table = Table(approval_data, colWidths=[3*inch, 3*inch])
    approval_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica-Bold'),
    ]))
    
    elements.append(approval_table)
    elements.append(Spacer(1, 20))
    
    # Footer
    footer_text = "This certificate is issued without prejudice to the rights and obligations of the parties under the Contract."
    footer = Paragraph(footer_text, normal_style)
    elements.append(footer)
    
    # Build PDF
    doc.build(elements)
    
    # Get the value of the BytesIO buffer and write it to the response
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    
    return response
