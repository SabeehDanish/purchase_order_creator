import camelot
import pandas as pd
import os

# --- Configuration ---
QUOTE_PDF_PATH = os.path.join('PO\'s', '111651.pdf')

print(f"--- Starting parametrized data extraction (lattice flavor) from: {QUOTE_PDF_PATH} ---")

try:
    # --- Parameters for precise table extraction ---
    table_area_coords = ['10,250,750,750']
    column_separators = [[90, 400, 470, 540]]

    print("Attempting to extract tables with Camelot using 'lattice' flavor and specified parameters...")
    tables = camelot.read_pdf(
        QUOTE_PDF_PATH,
        pages='1',
        flavor='lattice', # Changed to 'lattice'
        table_areas=table_area_coords,
        columns=column_separators,
        strip_text='\n'
    )

    if tables:
        print(f"Found {len(tables)} table(s) in specified area.")
        df_line_items = tables[0].df # Assuming the first table found is the correct one

        print("\n--- Raw Extracted Table (First Few Rows - PRE-CLEANING): ---")
        print(df_line_items.head(15)) # Print more rows to show where the header typically is

    else:
        print("No tables found by Camelot in the specified area.")

except Exception as e:
    print(f"Error during Camelot table extraction with parameters (lattice flavor): {e}")

print(f"\n--- Parametrized Lattice Extraction Attempt Complete for {QUOTE_PDF_PATH} ---")