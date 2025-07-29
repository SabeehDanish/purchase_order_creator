import pdfplumber
import pandas as pd
import os

# --- Configuration ---
QUOTE_PDF_PATH = os.path.join('PO\'s', '111651.pdf')
OUTPUT_DIR = 'extracted_data'

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

print(f"--- Starting data extraction with pdfplumber from: {QUOTE_PDF_PATH} ---")

try:
    with pdfplumber.open(QUOTE_PDF_PATH) as pdf:
        page = pdf.pages[0] # Assuming line items are on the first page

        # Define the area of the table. Coordinates are (x0, y0, x1, y1) - left, top, right, bottom.
        table_bbox = (10, 250, 600, 750)

        # Define table settings for pdfplumber
        table_settings = {
            "vertical_strategy": "explicit",
            "horizontal_strategy": "text",
            "explicit_vertical_lines": [90, 400, 470, 540],
            "snap_tolerance": 5,
            "join_tolerance": 3,
            # "edge_tolerance": 5, # REMOVED THIS LINE
            "text_tolerance": 5,
            "min_words_horizontal": 1,
            "min_words_vertical": 1,
        }

        # Crop the page to the table area before extraction to focus pdfplumber
        cropped_page = page.crop(table_bbox)

        tables = cropped_page.extract_tables(table_settings=table_settings)

        df_line_items = pd.DataFrame() # Initialize empty DataFrame

        if tables:
            print(f"Found {len(tables)} table(s) with pdfplumber.")
            raw_data = tables[0]

            header = raw_data[0]
            data_rows = raw_data[1:]

            df_line_items = pd.DataFrame(data_rows, columns=header)

            print("\n--- Raw Extracted Table (First Few Rows - BEFORE CLEANING): ---")
            print(df_line_items.head(15))

            # --- Apply cleaning logic similar to Camelot output ---
            df_line_items.rename(columns={
                'Item': 'item_number',
                'Description': 'description',
                'Qty': 'quantity',
                'Cost': 'unit_price',
                'Total': 'line_total'
            }, inplace=True)

            final_cols = ['item_number', 'description', 'quantity', 'unit_price', 'line_total']
            df_line_items = df_line_items[[col for col in final_cols if col in df_line_items.columns]]

            if 'item_number' in df_line_items.columns:
                df_line_items = df_line_items[df_line_items['item_number'].astype(str).str.strip() != '']
                df_line_items = df_line_items[df_line_items['item_number'].notna()]
            
            df_line_items.dropna(how='all', inplace=True)


            numeric_cols = ['quantity', 'unit_price', 'line_total']
            for col in numeric_cols:
                if col in df_line_items.columns:
                    df_line_items[col] = df_line_items[col].astype(str).str.replace(r'[^\d.-]', '', regex=True).str.strip()
                    df_line_items[col] = pd.to_numeric(df_line_items[col], errors='coerce')
                    df_line_items[col].fillna(0, inplace=True)

            print("\n--- Cleaned Line Items: ---")
            print(df_line_items[['item_number', 'description', 'quantity', 'unit_price', 'line_total']].head(10))

            output_csv_path = os.path.join(OUTPUT_DIR, 'raw_line_items_111651_pdfplumber_v3.csv')
            df_line_items.to_csv(output_csv_path, index=False)
            print(f"\nCleaned line items saved to: {output_csv_path}")

        else:
            print("No tables found by pdfplumber in the specified area.")

except ImportError:
    print("Error: pdfplumber not installed. Please install it using: pip install pdfplumber pandas")
except Exception as e:
    print(f"Error during pdfplumber table extraction: {e}")

print(f"\n--- Extraction Complete for {QUOTE_PDF_PATH} ---")