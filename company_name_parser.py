import companynameparser as cnp
import pandas as pd

input_file = "CNBS_FOEorigin_m1.xlsx"
output_file = "CNBS_FOEorigin_m1.parse.xlsx"
cpy_column_idx = 1


def full2half(s: str):
    n = []
    for char in s:
        num = ord(char)
        if num == 0x3000:
            num = 32
        elif 0xFF01 <= num <= 0xFF5E:
            num -= 0xFEE0
        char = chr(num)
        n.append(char)
    return "".join(n).replace(" ", "")


def main():
    data_frame = pd.read_excel(input_file, sheet_name=0)
    cpy_column_name = data_frame.keys()[cpy_column_idx]

    for idx, row in enumerate(data_frame.values):
        parse_result = cnp.parse(
            full2half(str(row[cpy_column_idx])), enable_word_segment=True
        )
        parse_brand_list = parse_result["brand"].split(",")
        data_frame.at[idx, cpy_column_name] = parse_brand_list[0]

    data_frame.to_excel(output_file, index=False, engine="xlsxwriter")


if __name__ == "__main__":
    main()
