import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from po_extractor import IntelligentExtractor

def test_dandh_extraction():
    sample_file = "PO's/DandH-Quote-11931304-0.Pdf"  # Update path if needed
    extractor = IntelligentExtractor(sample_file)
    po = extractor.extract_purchase_order()
    assert po.po_number == '11931304'
    assert po.order_date == '06/25/2025'
    assert abs(po.total - 11094.06) < 0.01
    assert len(po.line_items) == 1 