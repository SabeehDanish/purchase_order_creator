import camelot
import os

QUOTE_PDF_PATH = os.path.join('PO\'s', '111651.pdf')

print(f"Attempting to read PDF from: {QUOTE_PDF_PATH}")

try:
    # This is the exact parameter format Camelot expects:
    # table_areas: A list of strings (each string is a comma-separated coordinate)
    # columns: A list of lists of numbers (each inner list is a set of x-coordinates for columns)
    tables = camelot.read_pdf(
        QUOTE_PDF_PATH,
        pages='1',
        flavor='stream',
        table_areas=['10,250,750,750'], # This must be a list of strings
        columns=[[90, 400, 470, 540]],  # This must be a list of lists of numbers
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