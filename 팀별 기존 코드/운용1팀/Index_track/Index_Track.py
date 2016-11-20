import pandas as pd
import numpy as np


def get_data(file_name = '/Users/Sejoon/Documents/KSIF/data/input/Passive/Passive_data.xlsx'):
    xls = pd.ExcelFile(file_name)
    data = xls.parse(0, header = 8, index_col = 0)
    data = data.reindex(index = data.index[5:])        
    
    return data
    
    
def get_BM_data(file_name = '/Users/Sejoon/Documents/KSIF/data/input/Passive/Passive_data.xlsx'):
    xls = pd.ExcelFile(file_name)
    data = xls.parse(1, header = 8, index_col = 0)
    data = data.reindex(index = data.index[5:])   
    del data['Unnamed: 2']     
    data = data.rename(columns = {'FI00.MLA' : 'MKF500_LargeMid'})
    
    return data
 
   
def get_FreeFloat(file_name = '/Users/Sejoon/Documents/KSIF/data/input/Passive/Passive_data.xlsx'):
    xls = pd.ExcelFile(file_name)
    data = xls.parse(2, index_col = 0)
    del data['Name']
    data = data.T
    
    # get index size
    data_temp = xls.parse(1, header = 8, index_col = 0)
    data_temp = data_temp.reindex(index = data_temp.index[5:])
    index_size = data_temp.index.size
    
    temp = data
    for i in range(index_size - 1):
        data = data.append(temp)
    
    data.index = data_temp.index
    
    return data


def get_market_cap(data):
    for i in range(data.columns.size // 2):
        if i == 0:
            data_temp = data[data.columns[2 * i + 1]]
            data_temp.name = data.columns[2 * i]
            market_cap = pd.DataFrame(data_temp)
        market_cap[data.columns[2 * i]] = data[data.columns[2 * i + 1]]
        
    return market_cap
   
   
def get_price(data):
    for i in range(data.columns.size // 2):
        if i == 0:
            price_temp = data[data.columns[2 * i]]
            price = pd.DataFrame(price_temp)
        price[data.columns[2 * i]] = data[data.columns[2 * i]]
        
    return price

    
def get_total_market_cap(market_cap):
    return market_cap.sum(axis = 1)

    
def get_FFAdj_weight(marketcap, freefloat):
    marketCap_FFAdj = marketcap * freefloat
    total_market_cap = get_total_market_cap(marketCap_FFAdj)
    
    weight_FFAdj = marketCap_FFAdj / total_market_cap
    
    for i in range(marketCap_FFAdj.index.size):
        marketCap_FFAdj.ix[i, :] = marketCap_FFAdj.ix[i, :] / total_market_cap.ix[i]
    
    return marketCap_FFAdj
 
 
def get_portfolio(cap_weight_FFAdj, price, budget = 1.12105e+08):
    # 뽑히는 날짜 기준
    target_value_tohold = cap_weight_FFAdj * budget
    target_num_tohold = target_value_tohold / price
    f = lambda x: np.round(x)    
    
    target_num_tohold = target_num_tohold.applymap(f)
    
    return target_num_tohold

    
def port_to_excel(portfolio):
    xls = pd.ExcelFile('/Users/Sejoon/Documents/KSIF/data/input/Passive/Passive_data.xlsx')
    data = xls.parse(2, index_col = 0)
    del data['FreeFloat']
    
    port = pd.DataFrame(portfolio.ix[portfolio.index.size - 1, :])
    port['Name'] = data['Name']
    
    port.to_excel('/Users/Sejoon/Documents/KSIF/data/Return/Passive/Passive_portfolio.xlsx')

        
def get_returns(MKF500_largemid_ret, portfolio_ret):
    ret_copied = pd.DataFrame(index = portfolio_ret.index)
    ret_copied['MKF500_largemid'] = MKF500_largemid_ret
    ret_copied = ret_copied.fillna(0) 
    
    ret_copied['Tracking portfolio'] = portfolio_ret
    ret_copied = ret_copied.dropna()
    
    #ret_copied = ret_copied.reindex(index = ret_copied.index[11:])
    
    ret_copied = (ret_copied + 1).cumprod()
    ret_copied = ret_copied / ret_copied.ix[0, :]
    ret_copied = ret_copied * 100    
    
    del ret_copied.index.name
    return ret_copied



data = get_data()
data_BM = get_BM_data()
freefloat = get_FreeFloat()

marketCap = get_market_cap(data)
price = get_price(data)

weight_FFAdj = get_FFAdj_weight(marketCap, freefloat)

#port_to_excel(portfolio)

# 1025 hold -> 106154670
current_budget = 103958746
budget = 103958746
i = 1
while True: 
    portfolio = get_portfolio(weight_FFAdj, price, budget)
    test = (portfolio * price).sum(axis = 1)
    
    if test.ix[test.index.size - 1] <= current_budget - 50000:
        budget += 500
    elif test.ix[test.index.size - 1] >= current_budget:
        budget -= 1000
    else:
        break
    print(i, budget)
    i += 1


new_port = portfolio.ix[portfolio.index.size - 1, :]
new_port.to_csv('/Users/Sejoon/Desktop/passive_port.csv')


