import sys

try:
    import fitz
    print("PyMuPDF (fitz) is installed successfully.")
    print(f"PyMuPDF version: {fitz.__version__}")
    print(f"Path to fitz module: {fitz.__file__}")
except ImportError:
    print("PyMuPDF (fitz) is NOT installed or not accessible in this Python environment.")
    print("Please ensure you have installed it using 'pip install PyMuPDF'")
except Exception as e:
    print(f"An unexpected error occurred: {e}")

print(f"\nCurrently running Python from: {sys.executable}")
print(f"Python path (sys.path):")
for path in sys.path:
    print(f"  {path}")