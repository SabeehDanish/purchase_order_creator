import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from po_extractor import IntelligentExtractor

def test_tdsynnex_extraction():
    sample_file = "PO's/email_quote_excel_cpo_42566579.xlsx"  # Update path if needed
    extractor = IntelligentExtractor(sample_file)
    po = extractor.extract_purchase_order()
    assert po.po_number == '42566579'
    assert po.order_date == '10/14/2025'
    assert abs(po.total - 2435.04) < 0.01
    assert len(po.line_items) == 1 