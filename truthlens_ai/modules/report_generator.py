import datetime
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from truthlens_ai.config import REPORTS_DIR

def generate_pdf_report(analysis_data: dict) -> str:
    """Generates a structured, publication-ready PDF report of the news verification analysis."""
    timestamp_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"truthlens_report_{timestamp_str}.pdf"
    file_path = REPORTS_DIR / filename
    
    doc = SimpleDocTemplate(
        str(file_path),
        pagesize=letter,
        rightMargin=40, leftMargin=40,
        topMargin=40, bottomMargin=40
    )
    
    styles = getSampleStyleSheet()
    
    # Custom Brand Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0f172a'),
        alignment=1 # Center
    )
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#475569'),
        alignment=1
    )
    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=colors.HexColor('#1e293b'),
        spaceBefore=10,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#334155')
    )
    disclaimer_style = ParagraphStyle(
        'DisclaimerText',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#64748b')
    )
    
    elements = []
    
    # Header Banner
    elements.append(Paragraph("TRUTHLENS AI VERIFICATION REPORT", title_style))
    elements.append(Paragraph("AI-Powered Misinformation Detection & Forensic Claim Analysis System", subtitle_style))
    elements.append(Spacer(1, 12))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#2563eb'), spaceBefore=2, spaceAfter=14))
    
    # Executive Summary Card
    verdict = analysis_data.get('final_verdict', 'Inconclusive')
    score = analysis_data.get('credibility_score', 50.0)
    
    if "Genuine" in verdict:
        verdict_color = colors.HexColor('#16a34a') # Green
        verdict_bg = colors.HexColor('#f0fdf4')
    elif "Fake" in verdict:
        verdict_color = colors.HexColor('#dc2626') # Red
        verdict_bg = colors.HexColor('#fef2f2')
    else:
        verdict_color = colors.HexColor('#d97706') # Amber
        verdict_bg = colors.HexColor('#fffbeb')
        
    summary_data = [
        [
            Paragraph(f"<b>Article Title:</b> {analysis_data.get('title', 'Untitled')[:90]}", body_style),
            Paragraph(f"<b>Final Verdict:</b> <font color='{verdict_color.hexval()}'><b>{verdict.upper()}</b></font>", body_style)
        ],
        [
            Paragraph(f"<b>Source URL / Domain:</b> {analysis_data.get('domain', 'Direct Input')}", body_style),
            Paragraph(f"<b>Credibility Index:</b> <b>{score} / 100</b>", body_style)
        ],
        [
            Paragraph(f"<b>Analyzed On:</b> {datetime.datetime.now().strftime('%d %B %Y, %I:%M %p')}", body_style),
            Paragraph(f"<b>Primary Category:</b> {analysis_data.get('category', 'General')}", body_style)
        ]
    ]
    summary_table = Table(summary_data, colWidths=[320, 200])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), verdict_bg),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('PADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 14))
    
    # Model Predictions Comparison Table
    elements.append(Paragraph("1. Multi-Model Artificial Intelligence Detection", section_heading))
    ml_models = analysis_data.get('ml_prediction', {}).get('models', {})
    dl_data = analysis_data.get('deep_learning_prediction', {})
    
    models_rows = [
        ["Model Architecture", "Classification Verdict", "Genuine Confidence", "Fake Confidence"]
    ]
    
    if ml_models.get('logistic_regression'):
        lr = ml_models['logistic_regression']
        models_rows.append(["Logistic Regression (TF-IDF)", lr['prediction'], f"{lr['real_confidence']}%", f"{lr['fake_confidence']}%"])
    if ml_models.get('naive_bayes'):
        nb = ml_models['naive_bayes']
        models_rows.append(["Multinomial Naive Bayes", nb['prediction'], f"{nb['real_confidence']}%", f"{nb['fake_confidence']}%"])
    if ml_models.get('random_forest'):
        rf = ml_models['random_forest']
        models_rows.append(["Random Forest Classifier", rf['prediction'], f"{rf['real_confidence']}%", f"{rf['fake_confidence']}%"])
    if dl_data:
        models_rows.append(["DistilBERT Contextual Transformer", dl_data.get('prediction', 'N/A'), f"{dl_data.get('real_probability', 0)}%", f"{dl_data.get('fake_probability', 0)}%"])
        
    m_table = Table(models_rows, colWidths=[200, 140, 90, 90])
    m_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#0f172a')),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('FONTSIZE', (0,0), (-1,-1), 8.5),
        ('ALIGN', (1,0), (-1,-1), 'CENTER'),
    ]))
    elements.append(m_table)
    elements.append(Spacer(1, 14))
    
    # Explainable AI (XAI) Influential Terms
    elements.append(Paragraph("2. Explainable AI (XAI) Influential Terms Attribution", section_heading))
    top_words = analysis_data.get('xai_highlights', {}).get('top_influential_terms', [])
    if top_words:
        xai_rows = [["Influential Word / Token", "Attribution Weight", "Directional Impact"]]
        for item in top_words[:6]:
            impact_col = colors.HexColor('#16a34a') if item['direction'] == 'Genuine' else colors.HexColor('#dc2626')
            xai_rows.append([
                item['word'],
                str(item['weight']),
                Paragraph(f"<font color='{impact_col.hexval()}'><b>{item['direction']}</b></font>", body_style)
            ])
        x_table = Table(xai_rows, colWidths=[200, 140, 180])
        x_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f8fafc')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('PADDING', (0,0), (-1,-1), 4),
            ('FONTSIZE', (0,0), (-1,-1), 8.5),
        ]))
        elements.append(x_table)
    else:
        elements.append(Paragraph("No strongly polarized vocabulary patterns identified.", body_style))
    elements.append(Spacer(1, 14))
    
    # Source Credibility & Fact Verification Findings
    elements.append(Paragraph("3. Source Credibility & Fact-Check Verification", section_heading))
    src = analysis_data.get('source_data', {})
    evi = analysis_data.get('evidence_data', {})
    
    source_summary = f"<b>Domain Reputation:</b> {src.get('domain', 'N/A')} — {src.get('status', 'Unverified')} (Score: {src.get('credibility_score', 'N/A')}/100)<br/><b>Details:</b> {src.get('details', 'No additional publisher background available.')}"
    elements.append(Paragraph(source_summary, body_style))
    elements.append(Spacer(1, 6))
    
    if evi.get('contradicting_evidence'):
        elements.append(Paragraph("<b>Contradicting Evidence Detected:</b>", body_style))
        for ce in evi['contradicting_evidence'][:2]:
            elements.append(Paragraph(f"• <b>{ce['source']}:</b> {ce['summary']} <i>({ce['verdict']})</i>", body_style))
    elif evi.get('supporting_evidence'):
        elements.append(Paragraph("<b>Corroborating Evidence Found:</b>", body_style))
        for se in evi['supporting_evidence'][:2]:
            elements.append(Paragraph(f"• <b>{se['source']}:</b> {se['summary']} <i>({se['verdict']})</i>", body_style))
    else:
        elements.append(Paragraph("• <i>No direct contradiction or confirmation found in registered fact-checker repositories.</i>", body_style))
        
    elements.append(Spacer(1, 14))
    
    # Stylometry & Clickbait
    elements.append(Paragraph("4. Emotional Tone & Sensationalism Analysis", section_heading))
    sent = analysis_data.get('sentiment_data', {}).get('sentiment', {})
    cb = analysis_data.get('sentiment_data', {}).get('clickbait', {})
    styl_text = f"<b>Sentiment:</b> {sent.get('sentiment_label', 'Neutral')} (Polarity: {sent.get('polarity', 0.0)}) | <b>Dominant Emotion:</b> {sent.get('dominant_emotion', 'Objective')} | <b>Clickbait Index:</b> {cb.get('clickbait_score', 0)}/100 ({cb.get('rating', 'Standard')})"
    elements.append(Paragraph(styl_text, body_style))
    elements.append(Spacer(1, 16))
    
    # Academic Disclaimer
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cbd5e1'), spaceBefore=4, spaceAfter=8))
    elements.append(Paragraph("<b>Methodological Notice & Ethical AI Disclaimer:</b> TruthLens AI employs statistical NLP models, deep learning contextual representations, and external fact databases to estimate credibility. Results reflect probabilistic machine evaluation and available external evidence. This report should be utilized as an assistive decision-support tool rather than an infallible declaration of absolute truth.", disclaimer_style))
    
    doc.build(elements)
    return filename
