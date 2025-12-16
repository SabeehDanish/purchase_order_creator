**Purchase Order Creator**

*Overview*

An internal automation tool that generates official purchase orders (POs) from purchase requests for equipment and services.
The program parses request data, identifies the vendor and key metadata, and automatically populates EGATE’s internal PO template to produce a finalized purchase order.

*Problem*
Creating POs manually required:

- Extracting vendor and item details from requests
- Formatting data correctly
- Manually filling out the official PO template
- This process was time-consuming and prone to human error.

*Solution*
This tool automates the PO creation workflow by:

- Parsing and normalizing purchase request data
- Recognizing vendors and relevant metadata
- Translating request details into the official PO format
- Exporting a ready-to-use purchase order document

*Tech Stack*

- Python
- Data parsing & validation
- Document templating / generation

(Internal templates and proprietary data omitted.)

*Impact*

- Reduced PO creation time
- Improved consistency and accuracy
- Streamlined internal purchasing workflow

*Notes:*
All sensitive information and internal EGATE resources have been removed or abstracted for confidentiality.
