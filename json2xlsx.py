import json
import pandas as pd
import re

json_data = ""
with open(".\dist\entp\_internal\example\output\CNBS_FOEorigin_m3_1_output.json", 'rb') as json_file:
    json_data = json.load(json_file)

data_frame = pd.DataFrame(json_data)

data_frame.to_excel("test.xlsx", engine="xlsxwriter")

if __name__ == "__main__":
    pass