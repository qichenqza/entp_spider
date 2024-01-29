import pandas as pd
import glob

xlsx_label = "m4"

# input_path = f"C:\\Users\\admin\\Desktop\\work\\spider\\dist\\entp\\_internal\\example\\output\\CNBS_FOEorigin_{xlsx_label}_*_output.xlsx"
# output_path = f"C:\\Users\\admin\\Desktop\\work\\spider\\dist\\entp\\_internal\\example\\output\\{xlsx_label}\\CNBS_FOEorigin_{xlsx_label}_output.xlsx"

input_path = f"C:\\Users\\admin\\Desktop\\work\\spider\\dist\\entp\\_internal\\example\\output\\CNBS_FOEorigin_{xlsx_label}_*_output.skiped.xlsx"
output_path = f"C:\\Users\\admin\\Desktop\\work\\spider\\dist\\entp\\_internal\\example\\output\\{xlsx_label}\\CNBS_FOEorigin_{xlsx_label}_output.skiped.xlsx"

all_files = glob.glob(input_path)
data_frame_list = []

for file_path in all_files:
    df = pd.read_excel(file_path)
    data_frame_list.append(df)

merged_df = pd.concat(data_frame_list, ignore_index=True)
merged_df = merged_df.sort_values(by="coid")

merged_df.to_excel(output_path, index=False, engine="xlsxwriter")