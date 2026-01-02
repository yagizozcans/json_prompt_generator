from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import re
import os

def generate_pdf(output_filename="Proje_Raporu.pdf"):
    # Register TrueType Font that supports Turkish characters
    font_path = os.path.join(os.getcwd(), 'DejaVuSans.ttf')
    
    try:
        pdfmetrics.registerFont(TTFont('DejaVuSans', font_path))
        font_name = 'DejaVuSans'
        print(f"Font loaded from: {font_path}")
    except Exception as e:
        print(f"Warning: Could not load font from {font_path}. Error: {e}")
        print("Falling back to Helvetica (Turkish chars may fail).")
        font_name = 'Helvetica'

    doc = SimpleDocTemplate(output_filename, pagesize=A4,
                            rightMargin=72, leftMargin=72,
                            topMargin=72, bottomMargin=18)
    
    styles = getSampleStyleSheet()
    
    # Custom Styles using the new font
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName=font_name,
        fontSize=24,
        spaceAfter=30,
        textColor=HexColor('#2c3e50'),
        alignment=1 # Center
    )
    
    h1_style = ParagraphStyle(
        'CustomH1',
        parent=styles['Heading2'],
        fontName=font_name,
        fontSize=18,
        spaceBefore=20,
        spaceAfter=10,
        textColor=HexColor('#2980b9'),
        borderPadding=5,
        borderColor=HexColor('#bdc3c7'),
        borderWidth=0,
        borderBottomWidth=1
    )
    
    h2_style = ParagraphStyle(
        'CustomH2',
        parent=styles['Heading3'],
        fontName=font_name,
        fontSize=14,
        spaceBefore=15,
        spaceAfter=5,
        textColor=HexColor('#34495e')
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=11,
        leading=16,
        spaceAfter=10,
        alignment=4 # Justify
    )
    
    code_style = ParagraphStyle(
        'Code',
        parent=styles['Code'],
        fontName=font_name, 
        fontSize=9,
        leading=12,
        backColor=HexColor('#f7f9fa'),
        borderColor=HexColor('#e1e4e8'),
        borderWidth=1,
        borderPadding=5
    )

    story = []

    # Read README.md
    if os.path.exists("README.md"):
        with open("README.md", "r", encoding="utf-8") as f:
            content = f.readlines()
    else:
        content = ["# Hata", "README.md dosyası bulunamadı."]

    for line in content:
        line = line.strip()
        if not line:
            story.append(Spacer(1, 6))
            continue
            
        # Parse Markdown headers
        if line.startswith("# "):
            story.append(Paragraph(line[2:], title_style))
        elif line.startswith("## "):
            story.append(Paragraph(line[3:], h1_style))
        elif line.startswith("### "):
            story.append(Paragraph(line[4:], h2_style))
        
        # Parse Code Blocks
        elif line.startswith("```"):
            continue 
        elif line.startswith("    ") or line.startswith("\t"):
             story.append(Paragraph(line.strip(), code_style))
             
        # Parse Lists
        elif line.startswith("* ") or line.startswith("- "):
            text = line[2:]
            text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
            story.append(Paragraph(f"• {text}", body_style))
            
        # Normal Text
        else:
            text = line
            text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
            text = re.sub(r'`(.*?)`', r'<font color="#e74c3c">\1</font>', text)
            
            story.append(Paragraph(text, body_style))

    # Build PDF
    try:
        doc.build(story)
        print(f"PDF Rapor başarıyla oluşturuldu: {output_filename}")
    except Exception as e:
        print(f"PDF oluşturulurken hata: {e}")

if __name__ == "__main__":
    generate_pdf()
