import camelot
import pandas as pd
import os

def clean_and_extract_mcc_table(pdf_path, page_number):
    """
    Extracts the complex MCC table using the 'stream' method and cleans the data.
    """
    print(f"--- Attempting to extract table from page {page_number} using 'stream' flavor ---")
    
    # Define approximate column boundaries (x1, y1, x2, y2 coordinates)
    # Estimated based on a typical PDF width (0-800). Adjust if needed.
    # We define the 4 main columns: MCC (1), Description (2), Included (3), Similar (4)
    table_areas = ['0, 790, 770, 70'] 
    
    # Define column separators: [MCC, Description, Included, Similar]
    column_separators = ['60, 290, 525, 620']

    try:
        tables = camelot.read_pdf(
            pdf_path, 
            pages=str(page_number),
            flavor='stream', 
            table_areas=table_areas,
            columns=column_separators
        )
    except Exception as e:
        print(f"Error during PDF reading: {e}")
        return None

    if tables.n == 0:
        print("No tables extracted on the specified page.")
        return None
        
    print(f"Successfully extracted {tables.n} table(s)! Now cleaning data.")
    
    # --- Data Cleaning with Pandas ---
    df = tables[0].df

    # 1. Promote the first row (headers) to column names
    df.columns = df.iloc[0]
    df = df[1:].reset_index(drop=True)
    
    # 2. Rename the messy column headers to be clean
    df.rename(columns={
        'MCC': 'MCC',
        'MCC Title/\nMCC Description': 'MCC Title / MCC Description',
        'Included in this MCC': 'Included in this MCC',
        'Similar Merchants': 'Similar Merchants'
    }, inplace=True)
    
    # 3. Handle the alternating/merged rows by filling down the values in the MCC columns
    # This fills the blank 'MCC' and 'MCC Description' cells with the value from the row above.
    # The image shows the first column (MCC code) and second column (Description) are blank 
    # for the sub-rows, so we fill them with the main row's value.
    df['MCC'].replace('', method='ffill', inplace=True)
    df['MCC Title / MCC Description'].replace('', method='ffill', inplace=True)
    
    # 4. Clean up the 'Included in this MCC' and 'Similar Merchants' columns
    # We want to concatenate non-blank values where the MCC code is repeated.
    
    # First, drop rows where the 'Included' column is empty (these are just description continuation rows)
    # The main data starts where 'Included in this MCC' is not empty.
    # A simpler approach is to group by the MCC and concatenate the data
    
    # Group by the first two columns and aggregate the lists of values
    df_cleaned = df.groupby(['MCC', 'MCC Title / MCC Description']).agg({
        'Included in this MCC': lambda x: '\n'.join(x.astype(str).str.strip().tolist()),
        'Similar Merchants': lambda x: '\n'.join(x.astype(str).str.strip().tolist())
    }).reset_index()
    
    # Clean up the aggregated columns to remove empty lines and 'nan' strings
    for col in ['Included in this MCC', 'Similar Merchants']:
        df_cleaned[col] = df_cleaned[col].apply(
            lambda x: '\n'.join([line for line in x.split('\n') if line.strip() and line.strip().lower() != 'nan'])
        )

    return df_cleaned

if __name__ == "__main__":
    PDF_FILE_NAME = "Merchant_Data_Standards_Manual.pdf" # <-- Replace with your file name
    PAGE_TO_EXTRACT = 24 # The page number where the table starts

    # 1. Create a dummy file if you don't have the PDF to avoid crash
    if not os.path.exists(PDF_FILE_NAME):
         print(f"ERROR: Please place your PDF file named '{PDF_FILE_NAME}' in the current directory.")
         # exit() # Uncomment this line to stop execution if the file is missing

    # 2. Run the extraction
    final_df = clean_and_extract_mcc_table(PDF_FILE_NAME, PAGE_TO_EXTRACT)

    # 3. Output the result
    if final_df is not None:
        output_excel = "mcc_extracted_data.xlsx"
        print(f"\n--- Final Cleaned DataFrame Head ---\n{final_df.head().to_markdown()}")
        final_df.to_excel(output_excel, sheet_name=f"MCC_Page_{PAGE_TO_EXTRACT}", index=False)
        print(f"\n--- SUCCESS: Cleaned table saved to {output_excel} ---")