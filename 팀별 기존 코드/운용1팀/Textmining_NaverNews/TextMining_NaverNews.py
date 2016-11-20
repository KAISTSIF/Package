#-*- coding: utf-8 -*-
import sys
from bs4 import BeautifulSoup
import urllib.request
from urllib.parse import quote
import numpy as np
import pandas as pd
from konlpy.tag import Kkma
from konlpy.utils import pprint
from datetime import timedelta
import math
 
 
def get_price():
    file_name = '/Users/Sejoon/Documents/KSIF/data/input/TextMining/price_data.xlsx'
    xls = pd.ExcelFile(file_name)
    price = xls.parse(0, header = 8, index_col = 0)
    price = price.reindex(price.index[5:])
        
    return price
 

def get_badstocks(price, ticker_list):
    file_name = '/Users/Sejoon/Documents/KSIF/data/input/TextMining/20160919_result1.xlsx'
    xls = pd.ExcelFile(file_name)
    bad_stocks = xls.parse()
    
    bad_stocks = bad_stocks.reindex(index = price.index)
    
    for i in range(bad_stocks.index.size):
        for j in range(bad_stocks.columns.size):
            if bad_stocks.ix[i, bad_stocks.columns[j]] not in ticker_list:
                bad_stocks.ix[i, bad_stocks.columns[j]] = math.nan
                
    
    return bad_stocks
 
 
def get_newstitle(date, company_ticker):
# date : timestamp
# company_name : str
    ticker = company_ticker[1:]
    URL = "https://search.naver.com/search.naver?ie=utf8&where=news&query=" + ticker + \
        "&sm=tab_pge&sort=0&photo=0&field=0&reporter_article=&pd=3&ds=" + date.strftime('%Y.%m.%d') + \
        "&de=" + date.strftime('%Y.%m.%d') + "&docid=&nso=so:r,p:from" + date.strftime('%Y%m%d') + \
        "to" + date.strftime('%Y%m%d') + ",a:all&mynews=0&cluster_rank=41&start=&refresh_start=0"
    i = 0
    title_list = []
    title_list_before = [] # 종료조건 체크
    while True:
        current_page_num = str(1 + i * 10)
        position = URL.find("start")
        URL_with_page_num = URL[:position + 6] + current_page_num + URL[position + 6:]
        source_code_from_URL = urllib.request.urlopen(URL_with_page_num)
        soup = BeautifulSoup(source_code_from_URL, 'lxml', from_encoding = 'utf-8')
                             
        contents = soup.find('ul', 'type01')
        
        if contents == None:
            break
        
        contents_list = contents.find_all('li')

        title_list_temp = []
                
        for j in range(len(contents_list)):
            data = contents_list[j]
            if len(data) == 5:
                title = data.select('a')[1]['title']
            else: # len == 7
                title = data.select('a')[0]['title']
            title_list_temp.append(title)

        if title_list_temp == title_list_before:
            break

        title_list.extend(title_list_temp)  
        title_list_before = title_list_temp.copy()
        i += 1
        
    return title_list
 

def get_wordbook(bad_stocks, date_index): 
# date_index 는 날짜 체크용
    wordbook = {}
    kkma = Kkma()
    for i in range(bad_stocks.index.size): #bad_stocks.index.size
        for j in range(bad_stocks.columns.size): # j 0부터? 1부터?
            # 하루전 뉴스로 단어집 구성 + 휴일 추가 포함
            holiday_counter = 1
            if str(bad_stocks.ix[i, bad_stocks.columns[j]]) == 'nan':
                continue
            while True:  
                if bad_stocks.index[i] - timedelta(holiday_counter) in date_index and holiday_counter > 1:
                    break
                
                news_titles_before = get_newstitle(bad_stocks.index[i] - timedelta(holiday_counter), bad_stocks.ix[i, bad_stocks.columns[j]])
                if len(news_titles_before) == 0:
                    holiday_counter += 1
                    continue
                for k in range(len(news_titles_before)):
                    print(i, j, k, holiday_counter)
                    noun_list = kkma.nouns(news_titles_before[k])
                    if bad_stocks.ix[i, bad_stocks.columns[j]] not in wordbook:
                        worddict_temp = {}
                        for l in range(len(noun_list)):
                            if noun_list[l] not in worddict_temp:
                                worddict_temp[noun_list[l]] = 1
                            else:
                                worddict_temp[noun_list[l]] += 1
                        wordbook[bad_stocks.ix[i, bad_stocks.columns[j]]] = worddict_temp
    
                    else:
                        worddict_temp = wordbook[bad_stocks.ix[i, bad_stocks.columns[j]]]
                        for l in range(len(noun_list)):
                            if noun_list[l] not in worddict_temp:
                                worddict_temp[noun_list[l]] = 1
                            else:
                                worddict_temp[noun_list[l]] += 1
                        wordbook[bad_stocks.ix[i, bad_stocks.columns[j]]] = worddict_temp
                    
                holiday_counter += 1
                    
                    
                
    return wordbook




price = get_price()
ret = price.pct_change().dropna(how = 'all')






ticker_list = ['A005930', 'A035420', 'A005380', 'A000660', 'A012330', 'A015760', 'A055550', \
                'A005490', 'A033780', 'A090430', 'A105560', 'A000270', 'A051910', 'A028260', \
                'A096770', 'A034730', 'A000810', 'A032830', 'A017670', 'A068270']

company_list = ['삼성전자', 'NAVER', '현대차', 'SK하이닉스', '현대모비스', '한국전력', '신한지주', \
                'POSCO', 'KT&G', '아모레퍼시픽', 'KB금융', '기아차', 'LG화학', '삼성물산', \
                'SK이노베이션', 'SK', '삼성화재', '삼성생명', 'SK텔레콤', '셀트리온']  # 20개




#title_test = get_newstitle(price.index[1911], 'A005930')

bad_stocks = get_badstocks(price, ticker_list)

#wordbook_test = get_wordbook(bad_stocks, price.index)