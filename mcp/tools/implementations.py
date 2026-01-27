"""Tool implementations for MCP Server."""

import asyncio
import re
from datetime import datetime, timedelta
from typing import Any, Dict

from mcp.schemas.tools import (
    AnalyzeFeedbackInput,
    AnalyzeFeedbackOutput,
    CalculateBreachInput,
    CalculateBreachOutput,
    ExtractExpiryInput,
    ExtractExpiryOutput,
    GenerateVendorReportInput,
    GenerateVendorReportOutput,
    OCRDocumentInput,
    OCRDocumentOutput,
    SentimentCategory,
)
from mcp.schemas.base import RequestContext

# Mock data for MVP
MOCK_PROPERTY_FEEDBACK = {
    "prop_001": [
        {"comment": "Great location, love the neighborhood", "sentiment": "positive"},
        {"comment": "Kitchen needs updating", "sentiment": "neutral"},
        {"comment": "Too expensive for the area", "sentiment": "negative"},
        {"comment": "Perfect for families", "sentiment": "positive"},
        {"comment": "Parking is limited", "sentiment": "neutral"},
    ]
}

MOCK_LEDGER_DATA = {
    "tenancy_001": {
        "current_balance": -150.0,  # Negative = owed
        "last_payment_date": datetime.utcnow() - timedelta(days=45),
        "lease_start": datetime.utcnow() - timedelta(days=365),
        "lease_end": datetime.utcnow() + timedelta(days=180),
        "rent_amount": 500.0,
    }
}


async def analyze_open_home_feedback(
    input_data: AnalyzeFeedbackInput, context: RequestContext
) -> AnalyzeFeedbackOutput:
    """
    Analyze open home feedback for a property.

    Returns sentiment categories and comment breakdown.
    """
    # Simulate latency
    await asyncio.sleep(0.1)

    # Get mock feedback data
    feedback_list = MOCK_PROPERTY_FEEDBACK.get(input_data.property_id, [])

    # Calculate sentiment categories
    sentiment_counts: Dict[str, int] = {}
    comments = []
    for item in feedback_list:
        sentiment = item.get("sentiment", "neutral")
        sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1
        comments.append(item.get("comment", ""))

    total = len(feedback_list)
    categories = [
        SentimentCategory(
            category=cat,
            count=count,
            percentage=round((count / total * 100) if total > 0 else 0, 2),
        )
        for cat, count in sentiment_counts.items()
    ]

    return AnalyzeFeedbackOutput(
        property_id=input_data.property_id,
        total_feedback_count=total,
        sentiment_categories=categories,
        top_comments=comments[:10],
    )


async def calculate_breach_status(
    input_data: CalculateBreachInput, context: RequestContext
) -> CalculateBreachOutput:
    """
    Calculate breach status for a tenancy.

    Returns legality and breach risk based on rent status and lease terms.
    """
    # Simulate latency
    await asyncio.sleep(0.1)

    # Get mock ledger data
    ledger = MOCK_LEDGER_DATA.get(input_data.tenancy_id, {})
    current_balance = ledger.get("current_balance", 0.0)
    last_payment = ledger.get("last_payment_date")
    rent_amount = ledger.get("rent_amount", 0.0)

    # Calculate days overdue
    days_overdue = 0
    if last_payment:
        days_since_payment = (datetime.utcnow() - last_payment).days
        # Assume rent is due monthly, so if > 30 days, it's overdue
        if days_since_payment > 30:
            days_overdue = days_since_payment - 30

    # Determine breach risk
    if days_overdue == 0:
        level = "low"
        breach_status = "compliant"
        recommended_action = "No action required"
    elif days_overdue <= 7:
        level = "medium"
        breach_status = "at_risk"
        recommended_action = "Send reminder notice"
    elif days_overdue <= 14:
        level = "high"
        breach_status = "at_risk"
        recommended_action = "Issue breach notice"
    else:
        level = "critical"
        breach_status = "breached"
        recommended_action = "Legal action required"

    from mcp.schemas.tools import BreachRisk

    return CalculateBreachOutput(
        tenancy_id=input_data.tenancy_id,
        breach_risk=BreachRisk(
            level=level,
            days_overdue=days_overdue if days_overdue > 0 else None,
            breach_legal_status=breach_status,
            recommended_action=recommended_action,
        ),
        current_balance=abs(current_balance) if current_balance < 0 else None,
        last_payment_date=last_payment,
    )


async def ocr_document(
    input_data: OCRDocumentInput, context: RequestContext
) -> OCRDocumentOutput:
    """
    Extract text from uploaded documents using OCR.

    In MVP, this is a mock implementation.
    """
    # Simulate latency
    await asyncio.sleep(0.3)

    # Mock OCR extraction
    mock_text = """
    PROPERTY MANAGEMENT AGREEMENT
    
    This agreement is dated: 15 January 2025
    Expiry Date: 15 January 2026
    
    Property Address: 123 Main Street, Brisbane QLD 4000
    Owner: John Smith
    Manager: Ray White Property Management
    
    Terms and Conditions:
    1. Management fee: 8.5% of gross rent
    2. Agreement valid until expiry date above
    3. Renewal requires 30 days notice
    """

    return OCRDocumentOutput(
        document_url=input_data.document_url,
        extracted_text=mock_text.strip(),
        confidence_score=0.95,
        page_count=1,
    )


async def extract_expiry_date(
    input_data: ExtractExpiryInput, context: RequestContext
) -> ExtractExpiryOutput:
    """
    Extract expiry dates from text.

    Uses regex patterns to find date-like strings.
    """
    # Simulate latency
    await asyncio.sleep(0.1)

    # Date patterns
    date_patterns = [
        (r"expir(?:y|ation|es)\s*(?:date|on)?\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})", "expiry_date"),
        (r"valid\s+until\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})", "valid_until"),
        (r"end\s+date\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})", "end_date"),
    ]

    extracted_dates = []
    for pattern, field_name in date_patterns:
        matches = re.finditer(pattern, input_data.text, re.IGNORECASE)
        for match in matches:
            date_str = match.group(1)
            try:
                # Try to parse date
                if "/" in date_str:
                    parts = date_str.split("/")
                elif "-" in date_str:
                    parts = date_str.split("-")
                else:
                    continue

                if len(parts) == 3:
                    # Assume DD/MM/YYYY or DD-MM-YYYY
                    day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
                    if year < 100:
                        year += 2000
                    date_value = datetime(year, month, day)
                    extracted_dates.append(
                        {
                            "field_name": field_name,
                            "date_value": date_value,
                            "confidence": 0.8,
                        }
                    )
            except (ValueError, IndexError):
                continue

    from mcp.schemas.tools import ExtractedDate

    return ExtractExpiryOutput(
        extracted_dates=[
            ExtractedDate(**d) for d in extracted_dates if "date_value" in d
        ]
    )


async def generate_vendor_report(
    input_data: GenerateVendorReportInput, context: RequestContext
) -> GenerateVendorReportOutput:
    """
    Generate weekly vendor report combining feedback, REA stats, and trends.

    This is a composite tool that would typically call other tools/resources.
    """
    # Simulate latency
    await asyncio.sleep(0.2)

    # Get feedback analysis (would call analyze_open_home_feedback in real implementation)
    feedback_list = MOCK_PROPERTY_FEEDBACK.get(input_data.property_id, [])
    positive_count = sum(1 for f in feedback_list if f.get("sentiment") == "positive")
    total_count = len(feedback_list)

    feedback_summary = {
        "total_feedback": total_count,
        "positive_sentiment": positive_count,
        "positive_percentage": round((positive_count / total_count * 100) if total_count > 0 else 0, 2),
    }

    recommendations = []
    if positive_count / total_count < 0.5 if total_count > 0 else False:
        recommendations.append("Consider price adjustment based on negative feedback")
    if total_count < 5:
        recommendations.append("Increase marketing to generate more interest")

    return GenerateVendorReportOutput(
        property_id=input_data.property_id,
        report_date=datetime.utcnow(),
        feedback_summary=feedback_summary,
        market_trends={"avg_days_on_market": 45, "price_trend": "stable"},
        recommendations=recommendations,
    )


async def prepare_breach_notice(
    input_data: Dict[str, Any], context: RequestContext
) -> Dict[str, Any]:
    """
    Prepare breach notice document (draft-only in MVP).

    This is a HIGH-RISK mutation tool that requires HITL token.
    In MVP, it only generates a draft document without sending.
    """
    # Simulate latency
    await asyncio.sleep(0.2)

    tenancy_id = input_data.get("tenancy_id", "")
    breach_details = input_data.get("breach_details", {})

    # Generate draft breach notice
    draft_notice = {
        "notice_id": f"BN-{tenancy_id}-{datetime.utcnow().strftime('%Y%m%d')}",
        "tenancy_id": tenancy_id,
        "issue_date": datetime.utcnow().isoformat(),
        "breach_type": breach_details.get("breach_type", "rent_arrears"),
        "breach_description": breach_details.get("description", "Rent arrears"),
        "remedy_period_days": 14,
        "status": "draft",  # Always draft in MVP
        "requires_hitl_approval": True,
        "note": "This is a draft notice. HITL approval required before sending.",
    }

    return draft_notice
