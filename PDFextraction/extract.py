import pdfplumber
import re
import pandas as pd

PDF_PATH = "visa-merchant-data-standards-manual.pdf"
OUTPUT_PATH = "mcc_text_extracted.csv"

def extract_mcc_entries(pdf_path, start=27, end=106):
    all_rows = []
    mcc_pattern = re.compile(r"^\s*(\d{4})\s+(.+)$")  # e.g., "0742 Veterinary Services"

    with pdfplumber.open(pdf_path) as pdf:
        for page_num in range(start - 1, end):  # pdfplumber is 0-indexed
            print(f"🔍 Reading page {page_num + 1}...")
            text = pdf.pages[page_num].extract_text()

            if not text:
                print(f"⚠️ No text on page {page_num + 1} (might be scanned).")
                continue

            lines = [l.strip() for l in text.splitlines() if l.strip()]

            current_mcc = None
            current_title = ""
            current_desc = []
            current_included = []
            current_similar = []
            section = None

            for line in lines:
                # 1️⃣ Detect a new MCC entry
                m = mcc_pattern.match(line)
                if m:
                    # Save previous MCC
                    if current_mcc:
                        all_rows.append({
                            "MCC": current_mcc,
                            "MCC Title": current_title.strip(),
                            "Description": " ".join(current_desc).strip(),
                            "Included in this MCC": " ".join(current_included).strip(),
                            "Similar Merchants": " ".join(current_similar).strip(),
                            "Page": page_num + 1
                        })

                    # Start a new one
                    current_mcc = m.group(1)
                    current_title = m.group(2)
                    current_desc = []
                    current_included = []
                    current_similar = []
                    section = "desc"
                    continue

                # 2️⃣ Section transitions (detected by keywords)
                if "Included in this MCC" in line:
                    section = "included"
                    continue
                elif "Similar Merchants" in line:
                    section = "similar"
                    continue

                # 3️⃣ Accumulate lines into the correct section
                if section == "desc":
                    current_desc.append(line)
                elif section == "included":
                    current_included.append(line)
                elif section == "similar":
                    current_similar.append(line)

            # Save the last MCC on the page
            if current_mcc:
                all_rows.append({
                    "MCC": current_mcc,
                    "MCC Title": current_title.strip(),
                    "Description": " ".join(current_desc).strip(),
                    "Included in this MCC": " ".join(current_included).strip(),
                    "Similar Merchants": " ".join(current_similar).strip(),
                    "Page": page_num + 1
                })

    # Convert to DataFrame
    df = pd.DataFrame(all_rows)
    df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")
    print(f"✅ Done! Extracted {len(df)} MCC entries → {OUTPUT_PATH}")
    return df


if __name__ == "__main__":
    extract_mcc_entries(PDF_PATH)
