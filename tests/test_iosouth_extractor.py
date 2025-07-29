import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from po_extractor import IntelligentExtractor

def test_iosouth_extraction():
    sample_file = "PO's/111651.pdf"  # Update path if needed
    extractor = IntelligentExtractor(sample_file)
    po = extractor.extract_purchase_order()
    assert po.po_number == '111651'
    assert po.order_date == '7/16/2025'
    assert abs(po.total - 2600.00) < 0.01
    assert len(po.line_items) == 10 