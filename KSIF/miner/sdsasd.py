"""

"""
__author__ = 'Seung Hyeon Yu'
__email__ = 'rambor12@business.kaist.ac.kr'

### 2015.1.1-2015.12.31의 기사로 만들어진 딕션을 업데이트하며, 다음 종가를 예측하여 2016년 주가를 예측하는 백테스팅 코드 ###
import sys
sys.path.append("C:\TextMining")

year = 2016

lastyear = str(2016)
year = str(year)

import datetime as dt
today = dt.datetime.today()
today_str = today.strftime("%Y-%m-%d")

'''2010.1.1-2010.12.31 딕션 불러오기'''
diction ={}
counts = {}
filename = lastyear+' diction'
import ExcelController
ExcelController.LoadDiction(filename,diction,counts)

import DateGenerator.SetPeriod as DateGenerator
dates_txt = DateGenerator.Datetimes_Txt(year+'-08-01',today_str,time=(15,30))
dates_returns = DateGenerator.Datetimes_Return(year+'-08-01',today_str,time=(15,30))
dates = DateGenerator.Datetimes(year+'-08-01',today_str,time=(15,30))

import pandas as pd

#수집된 기사 형태소 분석
error_headlines = []
headlines =[]
import TxtController
TxtController.webcrawler(dates_txt,headlines,error_headlines)

morphemes_bydate = TxtController.morphemes_bydate(headlines,dates_txt)
morphemes_bydate = morphemes_bydate[dates]

#update & score
import Grader
result = Grader.UpdateNScore(counts,diction,dates,dates_returns,morphemes_bydate,stock='KOSPI200')

date = year
ExcelController.SaveDiction(date,diction,counts)
writer = pd.ExcelWriter('2016후 scores.xlsx', engine='xlsxwriter')
result.to_excel(writer, sheet_name='Sheet1')
writer.save()
