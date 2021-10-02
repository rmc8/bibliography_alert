import re
import html
import itertools
from typing import Optional, Tuple
from datetime import date, timedelta

import requests


class NationalDietLibrary:
    def __init__(self, offset: int = 30):
        self.BASE_SRU_URL: str = "https://iss.ndl.go.jp/api/sru?operation=searchRetrieve&query={param}%3d%22{keyword}%22%20AND%20from%3d%22{dt:%Y-%m}"
        self.BASE_OS_URL: str = "https://iss.ndl.go.jp/api/opensearch?title={title}"
        self.dt = date.today() - timedelta(days=offset)
    
    def get_bibliography(self, params: list, keywords: list) -> Tuple[str, str]:
        for param, keyword in itertools.product(params, keywords):
            res = requests.get(self.BASE_SRU_URL.format(param=param, keyword=keyword, dt=self.dt))
            yield html.unescape(res.text), keyword
    
    def get_isbn(self, title: str) -> Optional[str]:
        res = requests.get(self.BASE_OS_URL.format(title=title)).text
        htm = html.unescape(res)
        m = re.search(r'(?<=<dc:identifier xsi:type="dcndl:ISBN">)\d+(?=</dc:identifier>)', htm)
        if m:
            return m.group()
