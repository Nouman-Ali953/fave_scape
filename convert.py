import pandas as pd
import ast

# Load the Excel file
input_file = 'main_page_data_with_outlets.xlsx'  # Change this to your input file name
output_file = 'output.xlsx'  # Change this to your desired output file name
sheet_name = 'Sheet1'  # Change this to your sheet name if necessary

# Read the Excel file into a DataFrame
df = pd.read_excel(input_file, sheet_name=sheet_name)

# Convert the 'Outlets' column from a string representation to an actual list of dictionaries
df['Outlets'] = df['Outlets'].apply(ast.literal_eval)

# Function to expand outlets into multiple rows
def expand_outlets(row):
    outlets = row['Outlets']
    base_row = row.drop('Outlets')
    expanded_rows = []

    for i, outlet in enumerate(outlets):
        new_row = base_row.copy()
        new_row['Outlet'] = outlet['Outlet']
        new_row['Details'] = outlet['Details']
        
        if i > 0:
            new_row['Title'] = ""
            new_row['Address'] = ""
            new_row['City'] = ""
            new_row['Country'] = ""
            new_row['Category'] = ""

        expanded_rows.append(new_row)
    
    return pd.DataFrame(expanded_rows)

# Expand the outlets for each row in the DataFrame
expanded_df = pd.concat([expand_outlets(row) for _, row in df.iterrows()], ignore_index=True)

# Write the modified DataFrame back to an Excel file
expanded_df.to_excel(output_file, index=False)

print(f'Data successfully written to {output_file}')
