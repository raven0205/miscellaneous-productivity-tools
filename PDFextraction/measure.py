import pdfplumber

filepath = "visa-merchant-data-standards-manual.pdf"

with pdfplumber.open(filepath) as pdf:
    page = pdf.pages[27]
    for table in page.find_tables():
        print(table.bbox)  # gives (x0, top, x1, bottom)
