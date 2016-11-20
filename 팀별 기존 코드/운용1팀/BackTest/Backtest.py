# -*- coding: utf-8 -*-

import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import math

    
def get_frequency(portfolio):
    diff = abs((portfolio.index[0] - portfolio.index[1]).days)
    
    if diff < 7:
        return 'Daily'
    elif diff == 7:
        return 'Weekly'
    else:
        return 'Monthly'
        

def get_AdjPrice(file_name = 'Data.xlsx'):
    # 일별 수정주가를 읽어 DataFrame 형태로 반환하는 함수
    xls = pd.ExcelFile(file_name)
    price = xls.parse(0, header = 8, index_col = 0)
    price = price.reindex(price.index[5:])
        
    return price
    

def get_Portfolio(port_file_name):
    xls = pd.ExcelFile(port_file_name)
    portfolio = xls.parse(0)
    
    return portfolio
    
        
def get_weight(file_name):
#TODO: file_name 입력
    xls = pd.ExcelFile(file_name)
    
    return xls.parse()
    

def get_universe(frequency, file_name = 'MKF500_Largemid_Constituent_daily.xlsx'):
    xls = pd.ExcelFile(file_name)
    universe = xls.parse(0)
    
    if frequency == 'Monthly':
        return universe.asfreq('M', method = 'ffill')
    elif frequency == 'Weekly':
        return universe.asfreq('W-Tue', method = 'ffill')
    else:
        return universe


def get_common_data(portfolio, universe):
    # portfolio와 universe 의 공통 index로 reindex
    portfolio_index = portfolio.index
    universe_index = universe.index
    common_index = portfolio_index.intersection(universe_index)
    
    portfolio = portfolio.reindex(common_index)
    universe = universe.reindex(common_index)
    
    return portfolio, universe


def get_marketcap_verified(universe, frequency, file_name = 'Data.xlsx'): 
    xls = pd.ExcelFile(file_name)
    market_cap = xls.parse(2, header = 8, index_col = 0)
    market_cap = market_cap.reindex(market_cap.index[5:])

    if frequency == 'Monthly':
        market_cap = market_cap.asfreq('M', method = 'ffill')
    elif frequency == 'Weekly':
        market_cap = market_cap.asfreq('W-Tue', method = 'ffill')

    universe, market_cap = get_common_data(universe, market_cap)

    
    for i in range(market_cap.index.size):
        universe_temp = list(universe.ix[i, :])
        for j in range(market_cap.columns.size):
            if market_cap.columns[j] not in universe_temp:
                market_cap.ix[i, j] = math.nan
    
    return market_cap
    

def get_Portfolio_verified(portfolio, universe, frequency, adj_price):    
    portfolio_verified = portfolio.copy()
    
    for i in range(portfolio_verified.index.size):
        portfolio_temp = set(portfolio_verified.ix[i, :].dropna())
        universe_temp = set(universe.ix[i, :].dropna())
        portfolio_verified_temp = list(portfolio_temp.intersection(universe_temp))
        while True:
            try:
                portfolio_verified.ix[i, :] = portfolio_verified_temp
                break
            except ValueError:
                portfolio_verified_temp.append(math.nan)
                continue
   
    if frequency == 'Daily':
       price_index = adj_price.index
       portfolio_index = portfolio_verified.index
       common_index = portfolio_index.intersection(price_index)
       portfolio_verified = portfolio_verified.reindex(index = common_index)
        
    
    return portfolio_verified
        
        
def get_Benchmark_index(file_name = 'Data.xlsx'):
    # 일별 벤치마크 지수 자료를 읽어 DataFrame 형태로 반환
    xls = pd.ExcelFile(file_name)
    benchmark = xls.parse(1, header = 13, index_col = 0)
    del benchmark['Unnamed: 2']
    benchmark.columns = ['MKF500_Largemid']
    
    return benchmark
    

def get_total_marketcap_verified(market_cap_verified):
    return market_cap_verified.sum(axis = 1)
    
    
def get_marketcap_weight_verified(marketcap_verified):
    total_marketcap_verified = get_total_marketcap_verified(marketcap_verified)
    
    return marketcap_verified.div(total_marketcap_verified, axis = 'index')


def portfolio_convert(portfolio):
# 0과 1로 포트폴리오에 포함되는지 판별
    portfolio_total = set()
    for i in range(portfolio.index.size):
        portfolio_temp = set(portfolio.ix[i, :].dropna())
        portfolio_total.update(portfolio_temp)
    
    portfolio_total.discard(math.nan)
    portfolio_converted = pd.DataFrame(index = portfolio.index, columns = list(portfolio_total))
    f = lambda x: 0
    portfolio_converted = portfolio_converted.applymap(f)    
    
    for i in range(portfolio.index.size):
        for j in range(portfolio.columns.size):
            if str(portfolio.ix[i, portfolio.columns[j]]) != 'nan':
                portfolio_converted.ix[i, portfolio.ix[i, portfolio.columns[j]]] = 1
               
    return portfolio_converted
         

def get_transaction_cost(portfolio_num_before, portfolio_num_after, adj_price, buy = True, account = True):
    # account : 주식운용1 계좌이면 False, 투자전략 계좌이면 True
    def cost_high(x):
        if x < 500000:
            cost = x * 0.00502704
        elif x < 3000000:
            cost = x * 0.00127296 + 2000
        elif x < 30000000:
            cost = x * 0.00127296 + 1500
        elif x < 100000000:
            cost = x * 0.00117296
        elif x < 300000000:
            cost = x * 0.00097296
        else:
            cost = x * 0.00077296

        return cost // 10 * 10
            
    def cost_low(x):
        return x * 0.00024164 // 10 * 10
        
    def tax(x):
        return int(x * 0.003)
        
    cost = cost_high if account else cost_low
                
    if buy:
        num_buy = (portfolio_num_after - portfolio_num_before).dropna()
        num_buy = num_buy.where(num_buy > 0).dropna()
        price = (num_buy * adj_price).dropna()
        buy_cost = price.map(cost)
        return buy_cost.sum()
    else:
        num_sell = (portfolio_num_before - portfolio_num_after).dropna()
        num_sell = num_sell.where(num_sell > 0).dropna()
        price = (num_sell * adj_price).dropna()
        sell_cost = price.map(cost) + price.map(tax)
        return sell_cost.sum()
        
    

def backTest(portfolio_0_1, marketcap_weight_verified, adj_price, BM_index, \
            seedmoney, weight, frequency, equally_weighted = True, marketcap_weighted = False, account = True):
    # portfolio_verified : 포트폴리오 목록을 DataFrame 으로 입력, 0과 1로 편입여부 표시
    # marketcap_weight_verified : 시가총액의 비중
    # adj_price : 일별 수정주가를 DataFrame 으로 입력
    # BM_index : 일별 벤치마크 지수를 DataFrame 으로 입력
    # seedmoney : 초기금액(원 단위)
    # weight : 포트폴리오 각 종목별 비중, equal_weight == True 인 경우 함수 내에서 자동으로 조정
    # equally_weighted : 동일가중이면 True, 아니면 False
    # marketcap_weighted : 시가총액 가중시 True, 아니면 false
    # account : 투자전략 계좌이면 True, 주식운용1 계좌이면 False
    
    if equally_weighted == True:
        f = lambda x: 1
        weight = weight.applymap(f)
        marketcap_weight_verified = marketcap_weight_verified.applymap(f)
    elif marketcap_weighted == False:
        f = lambda x: 1
        marketcap_weight_verified = marketcap_weight_verified.applymap(f)
     
    total_portfolio_value = 0    
    
    df_ret = pd.DataFrame()
    for t in range(portfolio_0_1.index.size):
        portfolio_list = pd.DataFrame(portfolio_0_1.ix[t, :])
        portfolio_list = portfolio_list.dropna()
        
        if t == 0:
            portfolio_in_day = portfolio_0_1.index[t] + timedelta(1)
        
        
        if frequency == 'Monthly':
            year = portfolio_in_day.year if portfolio_in_day.month < 12 else portfolio_in_day.year + 1
            month = portfolio_in_day.month + 1 if portfolio_in_day.month < 12 else 1
            day = 1
            portfolio_out_day = datetime(year, month, day)
        elif frequency == 'Weekly':
            try:
                portfolio_out_day = portfolio_0_1.index[t + 1] 
            except IndexError:
                break
        else:
            try:
                portfolio_out_day = portfolio_0_1.index[t + 1]
            except IndexError:
                break
            
            
        if portfolio_out_day > adj_price.index[adj_price.index.size - 1]:
            break                
                
        while(True):
            try:
                price_portfolio_in_day = adj_price.ix[portfolio_in_day, :]
                break
            except KeyError:
                portfolio_in_day += timedelta(1)
        
        if frequency == 'Daily':
            portfolio_out_day = portfolio_in_day + timedelta(1)
        
        if t == 0:
            target_weight_tohold = marketcap_weight_verified * weight * portfolio_0_1
            target_weight_tohold = target_weight_tohold.div(target_weight_tohold.sum(axis = 1), axis = 'index')
            
        value_benchmark_initial = BM_index.ix[portfolio_in_day, 0]
          
        seedmoney_init = seedmoney if t == 0 else total_portfolio_value
        seedmoney = seedmoney_init
        
        f = lambda x: np.round(x)
        while True:
            target_weight_tohold_temp = target_weight_tohold.ix[portfolio_0_1.index[t], :]
            target_num_tohold_temp = (target_weight_tohold_temp * seedmoney) / price_portfolio_in_day
            target_num_tohold_temp = target_num_tohold_temp.map(f)
            target_num_tohold_temp = target_num_tohold_temp.dropna()
            
            value_portfolio_initial = target_num_tohold_temp * price_portfolio_in_day 
            value_portfolio_initial = value_portfolio_initial.sum()
          
            ##
            if seedmoney_init * 1.03 <= value_portfolio_initial:
                seedmoney *= 0.995
                continue
            elif seedmoney_init <= value_portfolio_initial:
                seedmoney *= 0.998
                continue
            elif value_portfolio_initial <= seedmoney_init * 0.95:
                seedmoney *= 1.005
                continue
            elif value_portfolio_initial <= seedmoney_init * 0.97:
                seedmoney *= 1.002
                continue
            else:
                break
        
        while True:
            try:
                price_portfolio_out_day = adj_price.ix[portfolio_out_day, :]
                break
            except KeyError:
                portfolio_out_day += timedelta(1)
                if portfolio_out_day > adj_price.index[adj_price.index.size - 1]:
                    break
             
          
        value_portfolio_later = (target_num_tohold_temp * price_portfolio_out_day).sum()
        try:        
            value_benchmark_later = BM_index.ix[portfolio_out_day, 0]
        except KeyError:
            break
        
        cash = seedmoney_init - value_portfolio_initial
        
  
        if t == 0:
            portfolio_num_before = portfolio_0_1.ix[0, :].dropna()
            f = lambda x: 0
            portfolio_num_before = portfolio_num_before.map(f)
            transaction_cost_buy = get_transaction_cost(portfolio_num_before, target_num_tohold_temp, adj_price.ix[portfolio_in_day, :], True, account)
            transaction_cost_sell = 0
        else:
            try:
                if np.all(portfolio_0_1.ix[t, :] == portfolio_0_1.ix[t + 1, :]):
                    transaction_cost_buy = 0
                    transaction_cost_sell = 0
                else:
                    transaction_cost_buy = get_transaction_cost(portfolio_num_before, target_num_tohold_temp, adj_price.ix[portfolio_in_day, :], True, account)
                    transaction_cost_sell = get_transaction_cost(portfolio_num_before, target_num_tohold_temp, adj_price.ix[portfolio_out_day, :], False, account)
            except IndexError:
                break
        
                  
        total_portfolio_value = value_portfolio_later + cash - transaction_cost_buy - transaction_cost_sell   
        portfolio_ret = total_portfolio_value / seedmoney_init - 1
        benchmark_ret = value_benchmark_later / value_benchmark_initial - 1
        
        df_ret = df_ret.append([[portfolio_out_day, portfolio_ret, benchmark_ret]])
        
        portfolio_in_day = portfolio_out_day

        portfolio_num_before = target_num_tohold_temp        
        
        print(t)
        
        
    df_ret.index = df_ret.pop(0)
    df_ret.columns = ['Strategy', 'BM']
    del df_ret.index.name
        
    return df_ret   
            
    

def ret_summary(ret, portfolio_0_1):
    ret_mean = ret.mean()
    ret_std = ret.std()
    sharpe_ratio = ret_mean / ret_std

    ret_strategy = ret['Strategy']    
    ret_BM = ret['BM']    
    
    win = ret_strategy > ret_BM
    win = win.where(win == True).count()
    loss = ret_strategy.size - win
    winloss_ratio = win / loss
    
    total_ret = ((ret+1).cumprod() - 1) * 100
    total_ret.plot()

    print("Total Return (Strategy, Benchmark)       (%%)  : %3.3f, %3.3f" % (total_ret.ix[total_ret.index.size - 1, 'Strategy'], total_ret.ix[total_ret.index.size - 1, 'BM']))
    print("Mean (Strategy, Benchmark)               (%%)  : %2.3f, %2.3f" % (ret_mean[0] * 100, ret_mean[1] * 100))
    print("Standard Deviation (Strategy, Benchmark) (%%)  : %2.3f, %2.3f" % (ret_std[0] * 100, ret_std[1] * 100))
    print("Sharpe Ratio (Strategy, Benchmark)            : %2.3f, %2.3f" % (sharpe_ratio[0], sharpe_ratio[1]))
    print("Win/Loss Ratio                                : %2.3f" % winloss_ratio)


     
#########
port_file_name = "1028port.xlsx"
weight_file_name = '1028weight.xlsx'
seedmoney = 100000000
account = False #투자전략계좌
equally_weighted = True
marketcap_weighted = False
#########
 
 
 
adj_price = get_AdjPrice()    
BM_index = get_Benchmark_index()
portfolio = get_Portfolio(port_file_name)
frequency = get_frequency(portfolio)

universe = get_universe(frequency)
portfolio, universe = get_common_data(portfolio, universe)

portfolio_verified = get_Portfolio_verified(portfolio, universe, frequency, adj_price)
marketcap_verified = get_marketcap_verified(universe, frequency)
marketcap_weight_verified = get_marketcap_weight_verified(marketcap_verified)
portfolio_0_1 = portfolio_convert(portfolio_verified)


#########
weight = marketcap_weight_verified
weight2 = get_weight(weight_file_name)
# weight를 주고 싶다면 marketcap_weight_verified 대신에 원하는 weight를 get_weight()를 통해 대체
#########


ret = backTest(portfolio_0_1, marketcap_weight_verified, adj_price, BM_index, seedmoney, \
     weight, frequency, equally_weighted, marketcap_weighted, account)
ret_summary(ret, portfolio_0_1)

#
#equally_weighted = False
#
#ret2 = backTest(portfolio_0_1, marketcap_weight_verified, adj_price, BM_index, seedmoney, \
#     weight2, frequency, equally_weighted, marketcap_weighted, account)
#ret_summary(ret2, portfolio_0_1)
#
#
#marketcap_weighted = True
#
#ret3 = backTest(portfolio_0_1, marketcap_weight_verified, adj_price, BM_index, seedmoney, \
#     weight2, frequency, equally_weighted, marketcap_weighted, account)
#ret_summary(ret3, portfolio_0_1)




















