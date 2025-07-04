import re
from collections import Counter

def analyze_document(text, current_linguist_profiles, content_type):
    # Heuristic: Risk based on keywords and length
    pii_keywords = ["SSN", "passport", "medical record", "DOB", "address", "phone", "email"]
    technical_keywords = ["algorithm", "API", "compliance", "regulation", "contract", "legal", "pharma", "clinical"]
    legal_keywords = ["court", "law", "contract", "agreement", "witness"]
    medical_keywords = ["patient", "diagnosis", "treatment", "clinical", "pharma"]
    word_count = len(text.split())
    sentence_count = max(1, text.count('.') + text.count('!') + text.count('?'))
    avg_sentence_length = word_count / sentence_count
    
    # Detect PII
    found_pii = [kw for kw in pii_keywords if kw.lower() in text.lower()]
    sensitive_summary = "Potential PII/PHI detected. Manual review required." if found_pii else "No obvious PII/PHI detected."
    
    # Complexity
    if word_count > 3000 or avg_sentence_length > 30:
        complexity = "High"
    elif word_count > 1000:
        complexity = "Medium"
    else:
        complexity = "Low"
    
    # Risk
    if found_pii or complexity == "High":
        risk_status = "Critical"
        risk_reason = "Sensitive data and/or high complexity detected."
    elif complexity == "Medium":
        risk_status = "Elevated"
        risk_reason = "Medium document complexity."
    else:
        risk_status = "Normal"
        risk_reason = "No major risks detected."
    
    # Key challenges
    if content_type.lower() == "legal" or any(kw in text.lower() for kw in legal_keywords):
        key_challenges = "Requires legal expertise."
    elif content_type.lower() == "medical" or any(kw in text.lower() for kw in medical_keywords):
        key_challenges = "Requires medical expertise."
    elif any(kw in text.lower() for kw in technical_keywords):
        key_challenges = "Extensive technical terms."
    else:
        key_challenges = "General content."
    
    # Linguist recommendation
    if content_type.lower() == "legal":
        linguist_profile = "Legal specialist linguist"
    elif content_type.lower() == "medical":
        linguist_profile = "Medical specialist linguist"
    elif content_type.lower() == "technical":
        linguist_profile = "Technical specialist linguist"
    else:
        linguist_profile = "Generalist linguist"
    
    # Team size
    if complexity == "High":
        team_size = 3
    elif complexity == "Medium":
        team_size = 2
    else:
        team_size = 1
    
    # Deadline fit
    if complexity == "High":
        deadline_fit = "Challenging"
    elif complexity == "Medium":
        deadline_fit = "Manageable"
    else:
        deadline_fit = "Easily achievable"
    
    # Strategic recommendations
    if risk_status == "Critical":
        recommendations = "Manual QA and compliance review required."
    elif content_type.lower() == "legal":
        recommendations = "Strict TM/TB adherence critical."
    elif content_type.lower() == "medical":
        recommendations = "Consult medical SME for terminology."
    else:
        recommendations = "Standard workflow recommended."
    
    # Simulate output fields
    return {
        "ai_overall_risk_status": risk_status,
        "ai_risk_reason": risk_reason,
        "ai_document_complexity": complexity,
        "ai_key_challenges": key_challenges,
        "ai_sensitive_data_alert_summary": sensitive_summary,
        "ai_recommended_linguist_profile_text": linguist_profile,
        "ai_optimal_team_size": team_size,
        "ai_deadline_fit_assessment": deadline_fit,
        "ai_strategic_recommendations": recommendations,
        "ai_analysis_timestamp": None  # To be set in main.py
    } 