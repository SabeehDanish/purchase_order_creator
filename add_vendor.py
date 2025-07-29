#!/usr/bin/env python3
"""
Utility script to add new vendors to the configuration.
This makes it easy to add new vendors without manually editing JSON files.
"""

import json
import os
import sys

def add_vendor():
    """Interactive script to add a new vendor configuration."""
    print("=== Add New Vendor Configuration ===\n")
    
    # Get vendor details
    vendor_name = input("Enter vendor name (e.g., 'newvendor'): ").strip().lower()
    if not vendor_name:
        print("Error: Vendor name is required.")
        return
    
    print(f"\n--- Vendor Information ---")
    vendor_display_name = input("Enter vendor display name (e.g., 'New Vendor Inc'): ").strip()
    vendor_address = input("Enter vendor address: ").strip()
    vendor_phone = input("Enter vendor phone: ").strip()
    vendor_website = input("Enter vendor website: ").strip()
    
    print(f"\n--- Detection Patterns ---")
    print("Enter patterns to detect this vendor (comma-separated):")
    print("Examples: 'new vendor', 'newvendor.com', '123 main st'")
    patterns_input = input("Patterns: ").strip()
    patterns = [p.strip() for p in patterns_input.split(',') if p.strip()]
    
    print(f"\n--- File Type ---")
    file_type = input("File type (pdf/csv) [pdf]: ").strip().lower() or 'pdf'
    
    if file_type == 'csv':
        skip_rows = input("Number of rows to skip before headers [0]: ").strip()
        skip_rows = int(skip_rows) if skip_rows.isdigit() else 0
    else:
        skip_rows = 0
        print("Enter table areas for PDF extraction (comma-separated):")
        print("Format: 'x1,y1,x2,y2' (e.g., '0,100,800,600')")
        table_areas_input = input("Table areas: ").strip()
        table_areas = [area.strip() for area in table_areas_input.split(',') if area.strip()]
        if not table_areas:
            table_areas = ['0,100,800,600']  # Default
    
    print(f"\n--- Column Headers ---")
    print("Enter the column header names used by this vendor:")
    item_header = input("Item/SKU column header: ").strip()
    desc_header = input("Description column header: ").strip()
    qty_header = input("Quantity column header: ").strip()
    price_header = input("Unit price column header: ").strip()
    total_header = input("Total/Extended column header: ").strip()
    
    # Create configuration
    config = {
        'patterns': patterns,
        'vendor_info': {
            'name': vendor_display_name,
            'address': vendor_address,
            'phone': vendor_phone,
            'website': vendor_website
        },
        'headers': {
            'item_number': item_header,
            'description': desc_header,
            'quantity': qty_header,
            'unit_price': price_header,
            'line_total': total_header
        }
    }
    
    if file_type == 'csv':
        config['file_type'] = 'csv'
        config['skip_rows'] = skip_rows
    else:
        config['table_areas'] = table_areas
    
    # Load existing config
    config_file = 'vendor_config.json'
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            data = json.load(f)
    else:
        data = {'vendors': {}}
    
    # Add new vendor
    data['vendors'][vendor_name] = config
    
    # Save updated config
    with open(config_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"\n✅ Successfully added vendor '{vendor_name}' to configuration!")
    print(f"Configuration saved to {config_file}")
    print(f"\nYou can now process {vendor_name} quotes automatically!")

def list_vendors():
    """List all configured vendors."""
    config_file = 'vendor_config.json'
    if not os.path.exists(config_file):
        print("No vendor configuration file found.")
        return
    
    with open(config_file, 'r') as f:
        data = json.load(f)
    
    vendors = data.get('vendors', {})
    if not vendors:
        print("No vendors configured.")
        return
    
    print("=== Configured Vendors ===")
    for vendor_name, config in vendors.items():
        vendor_info = config.get('vendor_info', {})
        patterns = config.get('patterns', [])
        print(f"\n{vendor_name}:")
        print(f"  Name: {vendor_info.get('name', 'N/A')}")
        print(f"  Patterns: {', '.join(patterns)}")
        print(f"  Type: {config.get('file_type', 'pdf')}")

def main():
    """Main function."""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        if command == 'list':
            list_vendors()
        elif command == 'add':
            add_vendor()
        else:
            print("Usage: python add_vendor.py [add|list]")
            print("  add  - Add a new vendor configuration")
            print("  list - List all configured vendors")
    else:
        print("Usage: python add_vendor.py [add|list]")
        print("  add  - Add a new vendor configuration")
        print("  list - List all configured vendors")

if __name__ == "__main__":
    main() 