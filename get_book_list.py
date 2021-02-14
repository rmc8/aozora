import os
import re
import sys
from time import sleep

import requests as r
from bs4 import BeautifulSoup


def get_index_of_kana():
    res = r.get("https://www.aozora.gr.jp/")
    return re.findall(r"(?:index_pages/(sakuhin_\w?[az]1.html))", res.text)


def write_rec(title, url, author):
    file_name = "book_list.csv"
    mode = "a" if os.path.exists(file_name) else "w"
    with open(file_name, mode=mode, encoding="utf-8") as f:
        print(title, url, author, sep=",", file=f)


def read_record(records):
    record, *records = records
    a_elm = record.find("a")
    title = re.sub(r"\u3000", " ", a_elm.text)
    ret_dict = {
        "title": title,
        "url": a_elm["href"].strip("./"),
        "author": record.select("td:nth-child(4)")[0].text
    }
    write_rec(**ret_dict)
    if records:
        read_record(records)


def get_records(url):
    sleep(1)
    res = r.get(f"https://www.aozora.gr.jp/index_pages/{url}")
    res.encoding = res.apparent_encoding
    bs = BeautifulSoup(res.content, "lxml")
    next_url = re.findall(r"sakuhin_\w?[az]\d+\.html(?=\">次の50件)", res.text)
    yield bs.select("table.list tr")[1:]
    if next_url:
        yield from get_records(next_url[0])


def get_book_list(url_list):
    url, *url_list = url_list
    records_2d = list(get_records(url))
    records = sum(records_2d, [])
    read_record(records)
    if url_list:
        get_book_list(url_list)


def main():
    HUGE_NUM = 10**9
    sys.setrecursionlimit(HUGE_NUM)
    url_list = get_index_of_kana()
    get_book_list(url_list)


if __name__ == "__main__":
    main()
