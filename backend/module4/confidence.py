import re
from typing import Dict, Any, Optional, Union
from module4.config import settings
from module4.schemas import ExtractedField


def parse_numeric_value(val: Any) -> Optional[Union[float, int]]:
    """
    Safely parses numeric values from text or numbers, supporting common
    Indian and international currency formats (Rs., INR, ₹, $, commas, k/Lakh suffixes).
    Returns float/int if successfully parsed, or None if unparseable.
    """
    if val is None:
        return None
    if isinstance(val, (int, float)):
        return float(val) if isinstance(val, float) else val

    val_str = str(val).strip()
    if not val_str or val_str.lower() in ("null", "n/a", "none", "nan", "nil"):
        return None

    # Check for multiplier suffixes like 87.5k, 1.2 Lakh, 2.5 Cr
    multiplier = 1.0
    val_clean = val_str

    match_suffix = re.search(r"(?i)\s*(k|lakhs?|l|crores?|cr)\b", val_clean)
    if match_suffix:
        suf = match_suffix.group(1).lower()
        if suf == "k":
            multiplier = 1_000.0
        elif suf in ("l", "lakh", "lakhs"):
            multiplier = 100_000.0
        elif suf in ("cr", "crore", "crores"):
            multiplier = 10_000_000.0
        val_clean = val_clean[:match_suffix.start()].strip()

    # Strip currency symbols and prefixes safely without requiring trailing word boundaries
    val_clean = re.sub(r"(?i)(?:rs\.?|inr|usd|eur|gbp|₹|\$|€|£)\s*", "", val_clean)
    val_clean = val_clean.replace(",", "").strip()

    try:
        if "." in val_clean:
            num = float(val_clean) * multiplier
            return int(num) if num.is_integer() else round(num, 2)
        else:
            num = float(val_clean) * multiplier
            return int(num) if num.is_integer() else round(num, 2)
    except ValueError:
        return None


def evaluate_extracted_field(field_data: Any, threshold: float = settings.CONFIDENCE_THRESHOLD) -> ExtractedField:
    """
    Evaluates raw dictionary or ExtractedField object from LLM response,
    computes numeric confidence, and flags needs_review according to rules:
    - If value is None or empty string -> needs_review = True, confidence = 0.0
    - If confidence < threshold -> needs_review = True
    """
    if isinstance(field_data, ExtractedField):
        val = field_data.value
        conf = float(field_data.confidence or 0.0)
        pg = field_data.page
    elif isinstance(field_data, dict):
        val = field_data.get("value")
        conf = float(field_data.get("confidence", 0.0))
        pg = field_data.get("page")
    else:
        val = field_data
        conf = 0.80 if field_data is not None else 0.0
        pg = 1

    # Clean up empty strings or whitespace-only values
    if isinstance(val, str):
        val_clean = val.strip()
        if not val_clean or val_clean.lower() in ("null", "n/a", "none", "nil"):
            val = None
            conf = 0.0
        else:
            val = val_clean

    # Try numeric conversion if value string contains currency symbols or numeric digits
    if val is not None and isinstance(val, str) and re.search(r"\d", val):
        parsed_num = parse_numeric_value(val)
        if parsed_num is not None:
            val = parsed_num

    # Determine needs_review flag
    needs_review = False
    if val is None or conf < threshold:
        needs_review = True

    return ExtractedField(
        value=val,
        confidence=round(conf, 4),
        page=pg,
        needs_review=needs_review
    )


def process_fields_confidence(raw_fields: Dict[str, Any], threshold: float = settings.CONFIDENCE_THRESHOLD) -> Dict[str, ExtractedField]:
    """Applies confidence evaluation to all fields extracted for a document."""
    processed: Dict[str, ExtractedField] = {}
    for field_name, raw_val in raw_fields.items():
        processed[field_name] = evaluate_extracted_field(raw_val, threshold=threshold)
    return processed
