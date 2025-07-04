import ai_analyzer

def test_low_complexity():
    text = "This is a simple document."
    result = ai_analyzer.analyze_document(text, [], "General")
    assert result["ai_document_complexity"] == "Low"
    assert result["ai_overall_risk_status"] == "Normal"

def test_high_complexity():
    text = "word " * 4000
    result = ai_analyzer.analyze_document(text, [], "Technical")
    assert result["ai_document_complexity"] == "High"
    assert result["ai_overall_risk_status"] == "Critical"

def test_pii_detection():
    text = "This document contains SSN and passport information."
    result = ai_analyzer.analyze_document(text, [], "General")
    assert "PII" in result["ai_sensitive_data_alert_summary"]
    assert result["ai_overall_risk_status"] == "Critical"

def test_legal_content():
    text = "This contract is subject to court law."
    result = ai_analyzer.analyze_document(text, [], "Legal")
    assert "legal" in result["ai_key_challenges"].lower()
    assert "Legal specialist" in result["ai_recommended_linguist_profile_text"]

def test_medical_content():
    text = "The patient received clinical treatment."
    result = ai_analyzer.analyze_document(text, [], "Medical")
    assert "medical" in result["ai_key_challenges"].lower()
    assert "Medical specialist" in result["ai_recommended_linguist_profile_text"] 