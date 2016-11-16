### 2015.1.1-2015.12.31의 기사로 만들어진 딕션을 업데이트하며, 다음 종가를 예측하여 2016년 주가를 예측하는 백테스팅 코드 ###
__author__ = 'Jiyoung Park'

import sys
import datetime as dt
import pandas as pd
import pandas.io.data as wb
import urllib
from bs4 import BeautifulSoup
import datetime
from dateutil.relativedelta import relativedelta
from konlpy.tag import Twitter
from KSIF.util import format

DICT_PATH = 'D:\School works\Business School\KSIF3\program\python\others\\'
URL_DONGA = "http://news.donga.com/List/01?"
URL_KOSCOM = "https://testbed.koscom.co.kr/gateway/v1/market/stocks/lists"



def LoadDiction(filename):
    """
     Diction 엑셀파일 불러 DataFrame으로 저장

    :param filename: str Diction path
    :return: dict 단어:score, dict 단어:counts
    """

    dic = pd.ExcelFile(filename + '.xlsx').parse()
    diction = {key: value for key, value in zip(dic.index, dic.scores)}
    counts = {key: value for key, value in zip(dic.index, dic.counts)}

    return diction, counts


def SaveDiction(date, diction, counts):
    """
     Diction DataFrame을 엑셀로 저장

    :param date: 저장할 year
    :param diction: dict
    :param counts: dict
    :return:
    """
    savedic = pd.DataFrame(columns=['scores', 'counts'], index=list(diction.keys()))
    savedic['scores'] = list(diction.values())
    savedic['counts'] = list(counts.values())
    writer = pd.ExcelWriter(date + ' diction.xlsx', engine='xlsxwriter')
    savedic.to_excel(writer, sheet_name='Sheet1')
    writer.save()


def StockReturns(dates, time_diff=(15, 0), stock="KOSPI200", website="google", price="Close"):
    """
     Get Stock Price

    :param dates: datetime
    :param time_diff:
    :param stock:
    :param website: {google | yahoo}
    :param price:
    :return:
    """
    close = wb.DataReader(stock, "google", dates[0], dates[-1])['Close']
    close.index = [date + relativedelta(hours=time_diff[0], minutes=time_diff[1]) for date in close.index]  # 시차 적용
    close = close.pct_change()  # 퍼센트 수익으로 변환
    stock_returns = pd.DataFrame(columns=['returns'], index=dates)
    for i in dates:
        if i in close.index:
            stock_returns.ix[i, ['returns']] = float(close.ix[i, [stock]])  # ???

    stock_returns = stock_returns.fillna(method='bfill')
    stock_returns.ix[dates[0], ['returns']] = 0
    stock_returns = stock_returns.fillna(0)

    return stock_returns


def later(start, years=0, months=0, days=0):
    """
     start로 부터 지난 시간 계산

    :param start:
    :param years:
    :param months:
    :param days:
    :return:
    """
    if type(start) == str:
        form = format.get_form(start)
        datetime_start = format.str_to_date(start)
        datetime_end = datetime_start + relativedelta(years=years, months=months, days=days)
        return datetime_end.strftime(form)

    elif type(start) in [pd.tslib.Timestamp, pd.datetime]:
        datetime_end = start + relativedelta(years=years, months=months, days=days)
        return datetime_end


def Datetimes(start, end, time_diff=(15, 30), option=None):
    """
    뉴스를 장마감시간인 오후 3시 기준으로 정렬
    Return list of days

    :param option:
    :param start:
    :param end:
    :param time_diff: tuple (시간, 분)
    :return: list of datetime
    """
    datetime_start = format.str_to_date(start) + relativedelta(hours=time_diff[0], minutes=time_diff[1])
    datetime_end = format.str_to_date(end) + relativedelta(hours=time_diff[0], minutes=time_diff[1])

    if option is 'start':
        datetime_start -= datetime.timedelta(days=1)
    elif option is 'end':
        datetime_end -= datetime.timedelta(days=1)
    elif option is 'txt':
        datetime_start -= datetime.timedelta(days=1)
        datetime_end += datetime.timedelta(days=1)
    elif option is 'return':
        datetime_start -= datetime.timedelta(days=1)
        datetime_end += datetime.timedelta(days=6)

    return [datetime_start+datetime.timedelta(i) for i in range((datetime_end-datetime_start).days+1)]


def webcrawler(dates_txt):
    """
    Headline 크롤링

    :param dates_txt:
    :return: list of headline
    """
    headlines = []
    headlines_error = []

    for date in dates_txt:
        for page in range(30):
            url = (URL_DONGA
                   + 'p=%s' % (1 + (16 * page))
                   + "&ymd=%s" % date.strftime("%Y%m%d")
                   + "&m=")
            print(url)
            read = urllib.request.urlopen(url).read()
            parsing = BeautifulSoup(read, "lxml")
            page_headlines = parsing.findAll("p", attrs={'class': 'title'})

            for headline in page_headlines:
                headline_form = headline.text.replace(']', '').rsplit('[', 1)
                headline_form[0] = headline_form[0].replace('[', '')
                try:
                    datetime.datetime.strptime(headline_form[1], '%Y-%m-%d %H:%M:%S')
                except:
                    headlines_error.append(headline_form)
                    print('error!')
                    print(headline)
                else:
                    headlines.append(headline_form)

    return headlines, headlines_error


def morphemes_bydate(headlines, dates_txt):
    """
    Headlines에서 단어를 추출하여 Time-Sereis로 쭉 나열

    Note
    ----
    명사 추출 = twitter.noun
    형태소 추출 = twitter.morphs
    품사 추출 = twitter.pos


    :param headlines:
    :param dates_txt:
    :return: pd.DataFrame
    """

    def nearest(items, pivot):
        return min(items, key=lambda x: pivot - x if x <= pivot else dt.timedelta(days=999999999))

    twitter = Twitter()

    word_dict = {k:[] for k in dates_txt}

    for headline in headlines:
        headline_date = format.str_to_date(headline[1], '%Y-%m-%d %H:%M:%S')

        nearest_date = nearest(dates_txt, headline_date)
        results = twitter.pos(headline[0], norm=True, stem=True)

        for result in results:
            word = result[0]
            morpheme = result[1]

            if len(word) > 1 and (morpheme == 'Noun' or morpheme == 'Verb' or morpheme == 'Alpha'):
                word_dict[nearest_date].append(word)

    return pd.DataFrame.from_dict(word_dict, orient='index')


def scoring(counts, diction, dates, morphemes_bydate, stock_returns):
    """
     diction 안에 있는 단어가 morphemes에 나올때마다 주식 수익률 더해서 score 계산

    :param counts:
    :param diction:
    :param dates:
    :param morphemes_bydate:
    :param stock_returns:
    :return:
    """
    for i in dates:
        for x in pd.Series(list(morphemes_bydate[i])).dropna():
            if x in diction.keys():
                diction[x] += stock_returns['returns'][i]
                counts[x] += 1
            else:
                diction[x] = stock_returns['returns'][i]
                counts[x] = 1


def UpdateNScore(counts, diction, dates, dates_returns, morphemes_bydate, stock='KOSPI200'):

    # 종가 가져오고
    stock_returns = StockReturns(dates_returns, time_diff=(15, 0), stock="KOSPI200", website="google", price="Close")

    savescore = []
    for date in dates:
        words = []
        words.extend(list(pd.Series(morphemes_bydate[date]).dropna()))

        # 주가 없으면 7일 전까지 단어들 누적 -> words
        for c in range(1, 7):
            if date >= dates[c]:
                cdaysago = date - relativedelta(days=c)
                if str(stock_returns['returns'][cdaysago]) == 'nan':
                    words.extend(list(pd.Series(list(morphemes_bydate[cdaysago])).dropna()))
                elif str(stock_returns['returns'][cdaysago]) != 'nan':
                    break
            elif date < dates[c]:
                break

        # score 계산 : words가 diction에 있으면 그 word의 score / 빈도수 만큼 score 계산
        score = 0
        lenth = 0
        for word in words:
            if word in diction.keys():
                score += diction[word] / counts[word]
                lenth += 1
        if lenth != 0:
            score = score / lenth
        elif lenth == 0:
            score = 0
        savescore.append(score)

        # 주가가 있으면 새로 수집된 diction의 단어가 기존 diction에 있을 때 기존 score에 수익률 더한다
        # diction update
        if not pd.isnull(stock_returns['returns'][date]):
            for word in list(pd.Series(morphemes_bydate[date]).dropna()):
                if word in diction.keys:
                    diction[word] += stock_returns['returns'][date]
                    counts[word] += 1
                else:
                    diction[word] = stock_returns['returns'][date]
                    counts[word] = 1

            for c in range(1, 7):
                if date >= dates[c]:
                    cdaysago = date - relativedelta(days=c)
                    # 7일 과거 주가가 없다면 현재 주가로 대체
                    if pd.isnull(stock_returns['returns'][cdaysago]):
                        stock_returns['returns'][cdaysago] = stock_returns['returns'][date]

                        for word in list(pd.Series(morphemes_bydate[cdaysago]).dropna()):
                            if word in diction.keys():
                                diction[word] += stock_returns['returns'][cdaysago]
                                counts[word] += 1
                            else:
                                diction[word] = stock_returns['returns'][cdaysago]
                                counts[word] = 1
                    else:
                        break

    result = pd.DataFrame(index=dates, columns=['score', 'actual'])
    result['score'] = savescore
    result['actual'] = stock_returns['returns']

    return result


def test():
    sys.path.append("C:\TextMining")

    year = 2016

    lastyear = str(2016)
    year = str(year)
    start = dt.datetime(year=2016, month=10, day=30)

    today = dt.datetime.today()
    today_str = today.strftime("%Y-%m-%d")

    '''2010.1.1-2010.12.31 딕션 불러오기'''
    filename = DICT_PATH + lastyear + ' diction'

    diction, counts = LoadDiction(filename)

    dates = Datetimes(start.strftime("%Y-%m-%d"), today_str, time_diff=(15, 30))
    dates_txt = Datetimes(start.strftime("%Y-%m-%d"), today_str, time_diff=(15, 30), option='txt')
    dates_return = Datetimes(start.strftime("%Y-%m-%d"), today_str, time_diff=(15, 30), option='return')


    # 수집된 기사 형태소 분석
    headlines, error_headlines = webcrawler(dates_txt)

    morphemes_bydates = morphemes_bydate(headlines, dates_txt)
    morphemes_bydates = morphemes_bydates[dates]

    # update & score
    result = UpdateNScore(counts, diction, dates, dates_return, morphemes_bydates, stock='KOSPI200')

    date = year
    SaveDiction(date, diction, counts)
    writer = pd.ExcelWriter(DICT_PATH + '2016후 scores.xlsx', engine='xlsxwriter')
    result.to_excel(writer, sheet_name='Sheet1')
    writer.save()


def naver_crawler():
    import requests
    from bs4 import BeautifulSoup
    import datetime
    from dateutil.relativedelta import relativedelta
    import re

    try:
        from urllib2 import urlopen
    except ImportError:
        from urllib.request import urlopen  # py3k

    # utility functions
    def format_Date_month(value, digit='2'):
        if digit == '2':
            return '{:02d}'.format(value)
        else:
            return '{:04d}'.format(value)

    def format_all_date(year, month, day):
        format_Date_month(year, '4') + "" + format_Date_month(month) + "" + format_Date_month(day)

    # Program starts here

    print("Start Crawling" + str(datetime.datetime.today()))
    # category numbers
    category = [274]
    # start date
    start_date = datetime.datetime(2016, 1, 2)
    # end date
    end_date = datetime.datetime(2016, 1, 2)
    # print(start_date.month, start_date.day)
    href_base_1 = "http://news.naver.com/main/list.nhn"
    href_base_1_catId = "?sid2="
    href_base_2 = "&sid1=100&mid=shm&mode=LS2D"
    href_date = "&date="
    href_page = "&page="

    start_page = 1

    # function that displays data
    def Get_page_Content(_startPage, soup, url_in_use):
        # method
        # source_code =  requests.get(href_use + href_page+ _startPage)
        # plain_text = source_code.text
        # soup = BeautifulSoup(plain_text, "lxml")

        print("on the **" + str(_startPage) + " **page")
        print("\n\n\n ******************************************************************************")
        print(url_in_use + "\n\n")
        for main_contents in soup.findAll('div', {'class': 'list_body newsflash_body'}):
            main_contents = main_contents.select('ul li dl')
            for contents_final in main_contents:
                print("\n\nNew article detail")
                try:
                    # Title
                    print("DT is " + str(len(contents_final.select('dt'))))

                    if (len(contents_final.select('dt')) == 2):
                        print(contents_final.select('dt a')[1].text.strip())
                    else:
                        print(contents_final.select('dt a')[0].text.strip())

                    # href - no needed
                    print(contents_final.select('dt a')[0]['href'])

                    # content
                    main_content_after_opening_link = requests.get(contents_final.select('dt a')[0]['href'])
                    plain_text__after_opening_link = main_content_after_opening_link.text
                    soup_after_opening_link = BeautifulSoup(plain_text__after_opening_link, "lxml")
                    for main_contents_after_opening_link in soup_after_opening_link.findAll('div', {
                        'class': 'article_body font1 size4'}):
                        print(main_contents_after_opening_link.select('div#articleBodyContents')[0].text.strip())

                    # written by
                    print(contents_final.select('dd span.writing')[0].text)
                    # date
                    print(contents_final.select('dd span.date')[0].text)

                except:
                    print
                    "Error in the HTML Tag"
                else:
                    print
                    ""

    # main code start here
    while start_date <= end_date:
        current_page = start_page
        # print("1")
        # for each category in the list
        for cat in category:
            while True:
                try:
                    # print ("2")
                    # make the paging to the current one, so that you will compare it latter with the previous .....
                    # if current page loaded index is less than it was expected to be... Break
                    Prev_calculated_page = current_page
                    href_use = href_base_1 + href_base_1_catId
                    href_use += str(cat) + href_base_2 + href_date + format_Date_month(start_date.year,
                                                                                       '4') + "" + format_Date_month(
                        start_date.month) + "" + format_Date_month(start_date.day)
                    print("link: " + href_use + href_page + str(current_page))
                    total_total = href_use + href_page + str(current_page)
                    source_code = requests.get(total_total)
                    print("3")
                    plain_text = source_code.text
                    soup = BeautifulSoup(plain_text, "lxml")
                    print("4")
                    Get_page_Content(current_page, soup, total_total)

                    # PAGING
                    main_paging = ''
                    for main_contents_pager in soup.findAll('div', {'class': 'paging'}):
                        main_paging = main_contents_pager.select('strong')  # to select valid points

                    str_main = str(main_paging).replace('[', '').replace(']', '').split(',')
                    int_v = str(re.findall(r"[\">](\d*)[</]", str_main[0])).strip('[').strip(
                        '\']')  # regular expression to select the paging
                    # if error happens, set it the original
                    if (int_v == ""):
                        int_v = current_page

                    current_page = int(int_v)
                    if (current_page < Prev_calculated_page):
                        break  # end of paging Index
                    else:
                        # increment the page index so that u will load the next page
                        current_page += 1
                except:
                    print("Error happen in the HTML tag")

        start_date += relativedelta(
            days=1)  # to loop back till the end of the the selected date, it addes one day per iteration to reach

    print("Done Crawling" + str(datetime.datetime.today()))
