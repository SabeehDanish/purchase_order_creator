import camelot
import os

QUOTE_PDF_PATH = os.path.join('PO\'s', '111651.pdf')

print(f"Attempting to read PDF from: {QUOTE_PDF_PATH} with minimal parameters...")

try:
    # Let Camelot auto-detect tables without specifying areas or columns
    tables = camelot.read_pdf(
        QUOTE_PDF_PATH,
        pages='1',
        flavor='stream', # Still using stream as it's generally better for this PDF
        strip_text='\n'
    )
    print(f"Camelot read successful. Found {len(tables)} tables.")
    if tables:
        print("\n--- Raw Extracted Table (First 5 Rows): ---")
        print(tables[0].df.head())
    else:
        print("No tables found by Camelot.")

except Exception as e:
    print(f"Error during Camelot read: {e}")

print("Script finished.")