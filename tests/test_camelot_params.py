import camelot
import pandas as pd
import re
import os
import sys

# --- Configuration ---
QUOTE_PDF_PATH = os.path.join('PO\'s', '111651.pdf')
OUTPUT_DIR = 'extracted_data'

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

print(f"--- Starting data extraction from: {QUOTE_PDF_PATH} ---")
# Debugging information - these were added in a previous step, kept for verification
print(f"Python Executable: {sys.executable}")
print(f"Python Path: {sys.path}")

# --- 1. Extract Tabular Data (Line Items) using Camelot ---
print("Attempting to extract tables with Camelot...")
df_line_items = pd.DataFrame() # Initialize empty DataFrame in case of errors

try:
    table_area_coords = ['10,250,600,750'] # [x_start, y_top, x_end, y_bottom] - Still broad to capture header
    # Explicitly define column x-coordinates. Even if Camelot doesn't split QtyCost,
    # this might help with other column boundaries.
    column_separators = ['80,390,460,530']

    tables = camelot.read_pdf(
        QUOTE_PDF_PATH,
        pages='1',
        flavor='stream',
        table_areas=table_area_coords,
        columns=column_separators, # Use explicit column separators
        strip_text='\n'
    )

    if tables:
        print(f"Found {len(tables)} table(s) in specified specified area.")
        raw_df = tables[0].df # Get the raw DataFrame from Camelot

        print("\n--- Raw Extracted Table (First Few Rows - BEFORE CLEANING): ---")
        print(raw_df.head(15))

        # --- Robust header detection and removal ---
        header_row_index = -1
        # Search for the header row by looking for key terms
        for i, row in raw_df.iterrows():
            row_str = " ".join(row.astype(str)).lower()
            # Look for core keywords for the header
            if 'item' in row_str and 'description' in row_str and ('qty' in row_str or 'quantity' in row_str) and ('cost' in row_str or 'unit_price' in row_str) and 'total' in row_str:
                header_row_index = i
                break

        if header_row_index != -1:
            # Extract raw column names from the identified header row
            raw_header_names = raw_df.iloc[header_row_index].astype(str).str.strip().tolist()
            # Get the data rows, starting from the row after the header
            df_line_items = raw_df.iloc[header_row_index + 1:].copy()
            df_line_items.reset_index(drop=True, inplace=True)

            # Ensure the number of column names matches the actual number of columns in the DataFrame
            num_actual_data_cols = df_line_items.shape[1]
            if len(raw_header_names) > num_actual_data_cols:
                raw_header_names = raw_header_names[:num_actual_data_cols]
            elif len(raw_header_names) < num_actual_data_cols:
                # Add generic names for any extra columns Camelot might have found
                raw_header_names.extend([f'Unnamed_{j}' for j in range(len(raw_header_names), num_actual_data_cols)])
            
            df_line_items.columns = raw_header_names # Assign the processed column names
            
            # --- Specific handling for 'QtyCost' column (if Camelot didn't split it) ---
            if 'QtyCost' in df_line_items.columns:
                # Fill empty strings with NaN for consistent processing
                df_line_items['QtyCost'] = df_line_items['QtyCost'].replace('', pd.NA)

                # Use regex to extract quantity and unit price from the 'QtyCost' string
                # This regex looks for a number (quantity) followed by another number (price),
                # potentially separated by space or nothing.
                # It handles optional '$' and commas in the price.
                extracted = df_line_items['QtyCost'].astype(str).str.extract(r'^\s*(\d+)\s*([$]?[\d,.]+)$', expand=True)
                
                # Assign extracted values to new temporary columns
                df_line_items['quantity_str'] = extracted[0]
                df_line_items['unit_price_str'] = extracted[1]

                # Handle cases where only quantity might be present in 'QtyCost'
                mask_only_qty = df_line_items['quantity_str'].isna() & df_line_items['QtyCost'].notna()
                if not df_line_items.loc[mask_only_qty, 'QtyCost'].empty:
                    df_line_items.loc[mask_only_qty, 'quantity_str'] = df_line_items.loc[mask_only_qty, 'QtyCost'].astype(str).str.extract(r'^\s*(\d+(?:\.\d+)?)\s*$', expand=False)
                    df_line_items.loc[mask_only_qty, 'unit_price_str'] = '0' # Assign '0' as default for unit_price if only quantity is found

                # Convert extracted strings to numeric, coercing errors to NaN, then filling NaN with 0
                df_line_items['quantity'] = pd.to_numeric(df_line_items['quantity_str'].astype(str).str.replace(r'[$,]', '', regex=True), errors='coerce').fillna(0)
                df_line_items['unit_price'] = pd.to_numeric(df_line_items['unit_price_str'].astype(str).str.replace(r'[$,]', '', regex=True), errors='coerce').fillna(0)

                # Drop the original 'QtyCost' column and intermediate string columns
                df_line_items.drop(columns=['QtyCost', 'quantity_str', 'unit_price_str'], errors='ignore', inplace=True)
            else:
                # If 'QtyCost' was somehow already split into 'Qty' and 'Cost' by Camelot (less likely with stream)
                if 'Qty' in df_line_items.columns:
                    df_line_items.rename(columns={'Qty': 'quantity'}, inplace=True)
                if 'Cost' in df_line_items.columns:
                    df_line_items.rename(columns={'Cost': 'unit_price'}, inplace=True)

            # Standardize other column names
            df_line_items.rename(columns={
                'Item': 'item_number',
                'Description': 'description',
                'Total': 'line_total'
            }, inplace=True)
            
            # Ensure only the target columns are kept and in the correct order
            final_cols = ['item_number', 'description', 'quantity', 'unit_price', 'line_total']
            df_line_items = df_line_items[[col for col in final_cols if col in df_line_items.columns]]

            # Filter out non-item rows (e.g., empty item numbers or descriptive text)
            if 'item_number' in df_line_items.columns:
                df_line_items = df_line_items[df_line_items['item_number'].astype(str).str.strip() != '']
                df_line_items = df_line_items[df_line_items['item_number'].notna()]
            
            df_line_items.dropna(how='all', inplace=True) # Drop rows that are entirely NaN after cleaning

            # Convert numerical columns to appropriate types (adjusted to avoid FutureWarning)
            numeric_cols = ['quantity', 'unit_price', 'line_total']
            for col in numeric_cols:
                if col in df_line_items.columns:
                    # Remove non-numeric characters (like '$', ',', 'T' from 'Total' column)
                    df_line_items.loc[:, col] = df_line_items[col].astype(str).str.replace(r'[$,T]', '', regex=True).str.strip()
                    df_line_items.loc[:, col] = pd.to_numeric(df_line_items[col], errors='coerce')
                    df_line_items.loc[:, col] = df_line_items[col].fillna(0) # Corrected inplace operation

            print("\n--- Cleaned Line Items: ---")
            print(df_line_items[['item_number', 'description', 'quantity', 'unit_price', 'line_total']].head())

            output_csv_path = os.path.join(OUTPUT_DIR, 'raw_line_items_111651_refined_v10.csv') # New filename
            df_line_items.to_csv(output_csv_path, index=False)
            print(f"\nCleaned line items saved to: {output_csv_path}")

        else:
            print("Could not find expected header in the extracted table. Please check 'raw_df.head()' output and adjust 'table_areas' or header keywords.")
            df_line_items = pd.DataFrame() # Ensure df_line_items is empty on failure

    else:
        print("No tables found by Camelot in the specified area.")

except Exception as e:
    print(f"Error during Camelot table extraction: {e}")
    df_line_items = pd.DataFrame() # Ensure df_line_items is empty on error


# --- 2. Extract Non-Tabular Data (Header/Summary Info) using PyMuPDF and Regex ---
print("\nAttempting to extract non-tabular data with PyMuPDF and Regex...")
quote_data = {} # Initialize dictionary for non-tabular data

try:
    import fitz # Moved import here to catch potential ImportError more explicitly

    with fitz.open(QUOTE_PDF_PATH) as doc:
        text = ""
        for page in doc:
            text += page.get_text()

        blocks = doc.load_page(0).get_text("blocks")

        # --- Extract Quote Header Information (Date, Quote Number) ---
        date_match = re.search(r'Date\s*(\d{1,2}/\d{1,2}/\d{4})', text)
        if date_match:
            quote_data['quote_date'] = date_match.group(1).strip()
        else:
            quote_data['quote_date'] = "Not Found"

        quote_num_match = re.search(r'Quote #\s*(\d+)', text)
        if quote_num_match:
            quote_data['quote_number'] = quote_num_match.group(1).strip()
        else:
            quote_data['quote_number'] = "Not Found"

        # --- Customer Name Extraction (Egate) ---
        customer_name_found = False
        for i, b in enumerate(blocks):
            x0, y0, x1, y1, block_text, block_type, block_no = b
            if "Name / Address" in block_text:
                if i + 1 < len(blocks):
                    customer_block = blocks[i+1]
                    # Check if the customer block is horizontally aligned with "Name / Address"
                    if abs(customer_block[0] - x0) < 50: # Tolerance of 50 units for x-coordinate
                        quote_data['customer_name'] = customer_block[4].strip()
                        customer_name_found = True
                        break
        if not customer_name_found:
            quote_data['customer_name'] = "Not Found"

        # --- REFINED Vendor Name, Address, and Phone Extraction ---
        # Collect blocks from the very top of the page (y0 < 250)
        top_text_area = ""
        for b in blocks:
            x0, y0, x1, y1, block_text, block_type, block_no = b
            if y0 < 250: # A higher threshold for collecting top blocks
                top_text_area += block_text + "\n"
            else:
                break # Stop once we are past the top header area

        print(f"\n--- DEBUG: Content of top_text_area ---")
        print(top_text_area)
        print(f"--- END DEBUG ---")

        # Extract Vendor Name
        vendor_name_match = re.search(r'(I/O South, LLC)', top_text_area, re.MULTILINE)
        if vendor_name_match:
            quote_data['vendor_name'] = vendor_name_match.group(1).strip()

            # Extract Vendor Address: Lines immediately following vendor name, before other key headers
            address_match = re.search(
                r'I/O South, LLC\s*\n(.*?)(?=\n(?:Date|Quote #|www\.iosouth\.com|Name / Address|Item|Description|Qty|Cost|Total))',
                top_text_area, re.DOTALL
            )
            if address_match:
                address_content = address_match.group(1).strip()
                # Filter out phone number if it's mixed in the address block
                address_lines = [line for line in address_content.split('\n') if not re.search(r'^\d{3}[-.\s]?\d{3}[-.\s]?\d{4}$', line.strip())]
                quote_data['vendor_address'] = "\n".join(address_lines).strip()
            else:
                # Fallback extraction for address if complex regex fails
                after_vendor_name_text = top_text_area[top_text_area.find("I/O South, LLC") + len("I/O South, LLC"):].strip()
                address_lines_fallback = []
                for line in after_vendor_name_text.split('\n'):
                    # Break if an empty line or a line with a known header/footer element is encountered
                    if not line.strip() or re.search(r'Date|Quote #|www\.|Name / Address|Item|Description|Qty|Cost|Total', line, re.IGNORECASE):
                        break
                    if not re.search(r'\d{3}[-.\s]?\d{3}[-.\s]?\d{4}', line): # Also filter out phone numbers
                        address_lines_fallback.append(line.strip())
                quote_data['vendor_address'] = "\n".join(address_lines_fallback).strip()
                if not quote_data['vendor_address']: # If still empty
                    quote_data['vendor_address'] = "Not Found"

            # Extract Vendor Phone Number
            phone_match = re.search(r'(\d{3}[-.\s]?\d{3}[-.\s]?\d{4})', top_text_area)
            if phone_match:
                quote_data['vendor_phone'] = phone_match.group(1)
            else:
                quote_data['vendor_phone'] = "Not Found"
        else:
            quote_data['vendor_name'] = "Not Found"
            quote_data['vendor_address'] = "Not Found"
            quote_data['vendor_phone'] = "Not Found"

except Exception as e:
    print(f"Error during PyMuPDF extraction: {e}")
    # Populate with 'Error' if any part of PyMuPDF extraction fails
    if not quote_data: # Only set if not already partially populated
        quote_data = {
            'quote_date': 'Error', 'quote_number': 'Error', 'customer_name': 'Error',
            'vendor_name': 'Error', 'vendor_address': 'Error', 'vendor_phone': 'Error'
        }

print("\n--- Extracted Non-Tabular Data: ---")
for key, value in quote_data.items():
    print(f"{key}: {value}")

print(f"\n--- Extraction Complete for {QUOTE_PDF_PATH} ---")