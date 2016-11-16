"""
 KOSCOM Web API
"""
__author__ = 'Seung Hyeon Yu'
__email__ = 'rambor12@business.kaist.ac.kr'

import requests
import json
from konlpy.utils import pprint
import lxml.html
import re
import os
import subprocess
import urllib
import xlrd
import win32com.client
import pandas as pd
import numpy as np

URL_KOSCOM = "https://testbed.koscom.co.kr/gateway/v1/market/stocks/lists?"


def url(url_base, params):
    """
    Make URL address

    :param url_base: Web API 기본 주소
    :param params:
    :return: url 주소
    """
    if url_base[-1] != '?':
        url_base += '?'
    url_out = url_base
    for k, v in params.items():
        if url_out[-1] != '?':
            url_out += '&'
        url_out += '%s=%s' % (k, v)
    return url_out


url = url(URL_KOSCOM, {'infoTpCd': '01', 'mktTpCd': 2})
text = requests.get(url).text
tree = lxml.html.fromstring(text)
onclick = tree.xpath('//*[@id="north"]/div[2]/ul/li[1]/a')[0].attrib['onclick']
pattern = re.compile("^openPdfDownload\('\d+',\s*'(\d+)'\)")
dcm = pattern.search(onclick).group(1)
# You can Choose XBRL or EXCEL Type
url = URL_DART_EXCEL + str(rpt_no) + "&dcm_no=" + dcm
filename = path + "\\" + str(crp_cd) + "_" + str(bsn_tp) + "_" + str(rpt_no) + ".xls"
print(url)
urllib.request.urlretrieve(url, filename)
