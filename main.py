import time
from typing import Optional

from pandas import DataFrame
from bs4 import BeautifulSoup

from pkg.db import SQLite
from pkg.gmail import Gmail
from pkg.yc import YamlConfig
from pkg.ndl import NationalDietLibrary


def _check_digit(cd_sum: int) -> str:
    cd_num: int = 11 - (cd_sum % 11)
    if cd_num == 10:
        return "X"
    elif cd_num == 11:
        return "0"
    return str(cd_num)


def isbn13to10(isbn13: str):
    isbn_base = isbn13[3:12]
    cd_sum: int = sum([int(n) * (10 - i) for i, n in enumerate(isbn_base)])
    cd: str = _check_digit(cd_sum)
    return f"{isbn_base}{cd}"


def get_bibliography_df(title_list: list,
                        params: list, keywords: list) -> DataFrame:
    api = NationalDietLibrary()
    df: DataFrame = DataFrame()
    for html, keyword in api.get_bibliography(params=params, keywords=keywords):
        bs = BeautifulSoup(html, "lxml-xml")
        for html_record in bs.find_all("record"):
            raw_title = html_record.find("dc:title").text
            title = raw_title.replace("　", " ")
            author = html_record.find("dc:creator").text
            if not df.empty and title in df.title.tolist():
                continue
            elif title in title_list:
                continue
            time.sleep(1)
            isbn: Optional[str] = api.get_isbn(title=title)
            if isbn is None:
                continue
            record: dict = {
                "title": title,
                "author": author,
                "isbn": isbn13to10(isbn),
                "keyword": keyword,
            }
            df = df.append(record, ignore_index=True)
        time.sleep(1)
    if not df.empty:
        df = df[["title", "author", "isbn", "keyword"]]
    return df


def main():
    # Init
    yc = YamlConfig(file_path="./settings/config.yml")
    yml: dict = yc.load()
    settings: dict = yml["settings"]
    api_settings: dict = settings["api"]
    google_settings: dict = settings["google"]
    google_account: dict = google_settings["account"]
    gmail_settings: dict = google_settings["gmail"]
    sqlite_db = SQLite("./db/bibliography.db")
    
    # Scraping
    try:
        # Get the latest bibliographic information
        db_df: DataFrame = sqlite_db.get_table()
        df: DataFrame = get_bibliography_df(
            title_list=list(db_df.title),
            params=api_settings["params"],
            keywords=api_settings["keywords"],
        )
        # If there is no bibliographic information, exit
        if df.empty:
            exit()
        
        # Alert
        df["url"] = df.isbn.map(lambda isbn: f"https://amazon.co.jp/dp/{isbn}")
        body = df.to_html(index=False, escape=False)
        gm = Gmail(
            from_=google_account["user"],
            **gmail_settings,
            body=body,
        )
        try:
            gm.login(**google_account)
            gm.send(is_html=True)
        finally:
            gm.close()
        
        # Update DB
        del df["url"]
        sqlite_db.insert_many(records=list(df.values))
    finally:
        sqlite_db.close()


if __name__ == "__main__":
    main()
