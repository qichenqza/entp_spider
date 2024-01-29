import pandas as pd

# Define the Excel file path
excel_file = "ZGC.xlsx"

# Read the Excel file into a pandas DataFrame
df = pd.read_excel(excel_file)

# Split the DataFrame into multiple DataFrames based on rows
split_dfs = [
    group for _, group in df.groupby(df.index // 2500)
]  # Change 1000 to the desired row count for each split

# Save each split DataFrame into separate Excel files
for i, split_df in enumerate(split_dfs):
    split_df.to_excel(f"split/ZGC_{i+1}.xlsx", index=False, engine="xlsxwriter")
