#! /usr/bin/env python3
# -*- coding:utf-8 -*-

# require python <= 3.9

import json
import time
from urllib.parse import parse_qs, urlparse

import ddddocr
import fire
import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

ocr = ddddocr.DdddOcr(show_ad=False)

# browser header build
# required
http_headers = {
    "Host": "wzxxbg.mofcom.gov.cn",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
    "Connection": "keep-alive",
    "Referer": "https://wzxxbg.mofcom.gov.cn/gspt",
}

session = requests.Session()

retry = Retry(connect=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount("http://", adapter)
session.mount("https://", adapter)


class EntpReader:
    def __init__(self) -> None:
        pass

    def url(self, input_file: str, output_file: str, dump_json=False):
        """
        read url from input file, parse html file of url and format the result into output file
        the FIRST column of input file should be url
        """
        url_result = []

        data_frame = pd.read_excel(input_file, sheet_name=0)
        skiped_row_idx = []

        for idx, row in enumerate(data_frame.values):
            print(f"start to cook row {idx}")

            http_url = ""

            for item in row:
                if pd.isna(item):
                    continue

                if str(item).startswith("https://"):
                    http_url = str(item)
                    break

            if not http_url:
                skiped_row_idx.append(idx)
                continue

            http_result = get_entp_detail_byurl(session, http_url)

            if not http_result:
                skiped_row_idx.append(idx)
                continue

            origin_row = data_frame.iloc[[idx]].to_dict("records")[0]
            origin_row.update(http_result)
            url_result.append(origin_row)

        # print skiped idx
        print(f"skiped row idx list: {repr(skiped_row_idx)}")

        skiped_data_frame = data_frame.iloc[skiped_row_idx]
        skiped_data_frame.to_excel(output_file + ".skiped.xlsx", index=False)

        if dump_json:
            with open(output_file + ".json", "w", encoding="utf8") as file:
                json.dump(url_result, file, ensure_ascii=False)

        data_frame = pd.DataFrame(url_result)

        # Write the DataFrame to an Excel file
        data_frame.to_excel(output_file + ".xlsx", index=False, engine="xlsxwriter")

    def search(self, input_file: str, output_file: str, dump_json=False):
        """
        get key word from input file, get FIRST search result and format the result into output file
        the FIRST column of input file should be key word which means (企业名称 / 统一社会信用代码 / 组织机构代码)
        if on result got from FIRST column, will try the SECOND column
        """
        search_result = []

        data_frame = pd.read_excel(input_file, sheet_name=0)
        skiped_row_idx = []

        for idx, row in enumerate(data_frame.values):
            print(f"start to cook row {idx}")
            http_result = []

            if not pd.isnull(row[0]):
                http_result = search_entp(session, str(row[0]).replace("-", ""))

            if not http_result and not pd.isnull(row[1]):
                http_result = search_entp(session, full2half(str(row[1])))

            if not http_result:
                skiped_row_idx.append(idx)
                continue

            http_result = get_entp_detail(
                session, http_result[0]["entpId"], http_result[0]["token"]
            )

            if not http_result:
                skiped_row_idx.append(idx)
                continue

            origin_row = data_frame.iloc[[idx]].to_dict("records")[0]
            origin_row.update(http_result)
            search_result.append(origin_row)

        # print skiped idx
        print(f"skiped row idx list: {repr(skiped_row_idx)}")

        skiped_data_frame = data_frame.iloc[skiped_row_idx]
        skiped_data_frame.to_excel(output_file + ".skiped.xlsx", index=False)

        if dump_json:
            with open(output_file + ".json", "w", encoding="utf8") as file:
                json.dump(search_result, file, ensure_ascii=False)

        data_frame = pd.DataFrame(search_result)

        # Write the DataFrame to an Excel file
        data_frame.to_excel(output_file + ".xlsx", index=False, engine="xlsxwriter")


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


def search_entp(http_session: requests.Session, key_word: str):
    unix_timestamp = int(time.time() * 1000)

    for _ in range(5):
        try:
            search_res_data = {}

            capcha_res = http_session.get(
                f"https://wzxxbg.mofcom.gov.cn/gspt/infoPub/entp/search/vCode?r={unix_timestamp}",
                headers=http_headers,
            )
            capcha_text = ocr.classification(capcha_res.content)
            if len(capcha_text) != 4:
                raise Exception("ocr result of capcha is wrong")

            # sleep wait server response
            # required
            time.sleep(3)

            search_http_res = http_session.post(
                url="https://wzxxbg.mofcom.gov.cn/gspt/infoPub/entp/search/searchEntpList",
                data={"keyWord": key_word, "searchWzCode": capcha_text},
                headers=http_headers,
            )

            search_http_res.raise_for_status()

            search_res_data = json.loads(search_http_res.content.decode("utf8"))

            if search_res_data["status"] == "1":
                # no data found, just jump out
                break

            # capcha ocr result is wrong
            if search_res_data["status"] != "0":
                raise Exception(search_res_data["message"])

            break
        except Exception as err:
            print(repr(err))
            continue

    if not search_res_data or search_res_data["status"] != "0":
        return None

    search_result = []
    for item in search_res_data["data"]["wzResult"]["result"]:
        search_result.append({"entpId": item["ENTP_MAIN_ID"], "token": item["TOKEN"]})
    return search_result


def get_entp_detail_byurl(http_session: requests.Session, url: str):
    parse_res = parse_qs(urlparse(url).query)
    return get_entp_detail(
        http_session, "".join(parse_res["entpId"]), "".join(parse_res["token"])
    )


def get_entp_detail(http_session: requests.Session, entp_id: str, token: str):
    detail_res = http_session.post(
        url="https://wzxxbg.mofcom.gov.cn/gspt/infoPub/entp/search/wzEntpDetail",
        data={
            "entpId": entp_id,
            "token": token,
        },
        headers=http_headers,
    )

    detail_res_data = json.loads(detail_res.content.decode("utf8"))
    if detail_res_data["status"] != "0":
        return None

    detail_res_info = detail_res_data["data"]["wzResult"]
    detail_res_info["ENTP_ID"] = entp_id
    detail_res_info["TOKEN"] = token
    detail_res_info["INVESTOR_NUM"] = len(detail_res_data["data"]["investorResult"])

    detail_res_info["INVESTOR_NUM_CHINA"] = 0
    detail_res_info["INVESTOR_NUM_HONGKONG"] = 0
    detail_res_info["INVESTOR_NUM_MACAO"] = 0
    detail_res_info["INVESTOR_NUM_TAIWAN"] = 0
    detail_res_info["INVESTOR_NUM_OTHERS"] = 0

    detail_res_info["INVESTOR_CAPITAL_CHINA"] = 0
    detail_res_info["INVESTOR_CAPITAL_HONGKONG"] = 0
    detail_res_info["INVESTOR_CAPITAL_MACAO"] = 0
    detail_res_info["INVESTOR_CAPITAL_TAIWAN"] = 0
    detail_res_info["INVESTOR_CAPITAL_OTHERS"] = 0

    for idx, item in enumerate(detail_res_data["data"]["investorResult"]):
        if item["COUNTRYNAME"] == "中国":
            detail_res_info["INVESTOR_NUM_CHINA"] += 1
            detail_res_info["INVESTOR_CAPITAL_CHINA"] += float(item["CAPITAL_AMOUNT"])
        elif item["COUNTRYNAME"] == "香港地区":
            detail_res_info["INVESTOR_NUM_HONGKONG"] += 1
            detail_res_info["INVESTOR_CAPITAL_HONGKONG"] += float(
                item["CAPITAL_AMOUNT"]
            )
        elif item["COUNTRYNAME"] == "澳门地区":
            detail_res_info["INVESTOR_NUM_MACAO"] += 1
            detail_res_info["INVESTOR_CAPITAL_MACAO"] += float(item["CAPITAL_AMOUNT"])
        elif item["COUNTRYNAME"] == "台湾地区":
            detail_res_info["INVESTOR_NUM_TAIWAN"] += 1
            detail_res_info["INVESTOR_CAPITAL_TAIWAN"] += float(item["CAPITAL_AMOUNT"])
        else:
            detail_res_info["INVESTOR_NUM_OTHERS"] += 1
            detail_res_info["INVESTOR_CAPITAL_OTHERS"] += float(item["CAPITAL_AMOUNT"])

        for key in item:
            detail_res_info[f"{key}_{idx}"] = item[key]

    return detail_res_info


if __name__ == "__main__":
    fire.Fire(EntpReader)
