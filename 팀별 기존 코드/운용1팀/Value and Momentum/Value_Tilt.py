import numpy as np
import pandas as pd
import math
from scipy.stats import norm
from datetime import date, timedelta
import warnings

warnings.simplefilter(action = 'ignore', category = RuntimeWarning)
#
#def get_data(sheet, file_name = '/Users/Sejoon/Documents/KSIF/data/input/ValMom/Value_data_0804_max.xlsx'):
#    xls = pd.ExcelFile(file_name)
#    data = xls.parse(sheet, header = 8, index_col = 0)
#    data = data.reindex(index = data.index[5:])
#    
#    return data
#    
#    
    
def get_data(sheet, file_name = '/Users/Sejoon/Documents/KSIF/data/input/ValMom/Value_data_0917.xlsx'):
    xls = pd.ExcelFile(file_name)
    data = xls.parse(sheet, header = 8, index_col = 0)
    data = data.reindex(index = data.index[5:])
    
    df = pd.DataFrame()
    index_temp = []
    if sheet != 0:   
        for i in range(data.index.size):
            data_temp = []
            if data.index[i].month == 12:
                date_temp = data.index[i]
                while True:
                    date_temp += timedelta(1)
                    if date_temp.day == 31 and date_temp.month == 3:
                        index_temp.append(date_temp)
                        break
               
            elif data.index[i].month == 3:
                date_temp = data.index[i]
                while True:
                    date_temp += timedelta(1)
                    if date_temp.day == 31:
                        index_temp.append(date_temp)
                        break
                
            elif data.index[i].month == 6:
                date_temp = data.index[i]
                while True:
                    date_temp += timedelta(1)
                    if date_temp.day == 31 and date_temp.month == 8:
                        index_temp.append(date_temp)
                        break
                
            else:
                date_temp = data.index[i]
                while True:
                    date_temp += timedelta(1)
                    if date_temp.day == 30 and date_temp.month == 11:
                        index_temp.append(date_temp)
                        break
         
            data_temp.extend(list(data.ix[i, :]))
            df = df.append([data_temp], ignore_index = True)
        
        df.index = index_temp
        df.columns = data.columns            
                
                
        
        stock_num = xls.parse(6, header = 8, index_col = 0)
        stock_num = stock_num.reindex(index = stock_num.index[5:])
        price_ratio = df / stock_num
        price_ratio = price_ratio.dropna(axis = 1, how = 'all')
        price_ratio = price_ratio.reindex(index = df.index)
       
       # -PER, PCR 처리
        max_priceratio = pd.DataFrame(price_ratio.max()).T
        for i in range(price_ratio.columns.size // 4):
            for j in range(price_ratio.index.size):
                if price_ratio.ix[j, 4 * i] < 0:
                    price_ratio.ix[j, 4 * i] = max_priceratio.ix[0, 4 * i]
                if price_ratio.ix[j, 4 * i + 2] < 0:
                    price_ratio.ix[j, 4 * i + 2] = max_priceratio.ix[0, 4 * i + 2]
                if price_ratio.ix[j, 4 * i + 3] < 0:
                    price_ratio.ix[j, 4 * i + 3] = max_priceratio.ix[0, 4 * i + 3]
                

         
        return price_ratio
    else:
        return data


    
def get_universe(index_data, file_name = '/Users/Sejoon/Documents/KSIF/data/input/MKF500_Largemid_Constituent.xlsx'):
    xls = pd.ExcelFile(file_name)
    data = xls.parse(0)
    return data.reindex(index = index_data.index)
    
def get_historical_value(data_sec, universe):
    f = lambda x: math.nan
    data_sec_his_mean = data_sec.copy()
    data_sec_his_std = data_sec.copy()
    for i in range(len(data_sec)):
        data_sec_his_mean[i] = data_sec_his_mean[i].applymap(f)
        data_sec_his_std[i] = data_sec_his_std[i].applymap(f)
    
    for t in range(universe.index.size):
        nUniverse = universe.ix[t, :].dropna().size
        for i in range(1, nUniverse + 1):
            s = 0
            while True:
                if s == 10:
                    break
                try:
                    date_temp = universe.index[t]
                    loc_temp = data_sec[s].index.get_loc(date_temp)
                    value_temp = data_sec[s].ix[loc_temp - 19 : loc_temp + 1, [universe.ix[t, i], universe.ix[t, i] + ".1", universe.ix[t, i] + ".2", universe.ix[t, i] + ".3"]]
                    value_mean = np.nanmean(value_temp, axis = 0, dtype = 'float')
                    
                    value_std = np.nanstd(value_temp, axis = 0, dtype = 'float')

                    data_sec_his_mean[s].ix[universe.index[t], [universe.ix[t, i], universe.ix[t, i] + ".1", universe.ix[t, i] + ".2", universe.ix[t, i] + ".3"]] = value_mean
                    data_sec_his_std[s].ix[universe.index[t], [universe.ix[t, i], universe.ix[t, i] + ".1", universe.ix[t, i] + ".2", universe.ix[t, i] + ".3"]] = value_std
                    break                    
                    
                except:
                    s += 1
                    continue
                
    return data_sec_his_mean, data_sec_his_std
    
def get_relative_value(data_sec, universe):
    f = lambda x: math.nan
    data_sec_valid = data_sec.copy()
    
    for i in range(len(data_sec)):
        data_sec_valid[i] = data_sec_valid[i].applymap(f)
        
    for t in range(universe.index.size):
        nUniverse = universe.ix[t, :].dropna().size
        for i in range(1, nUniverse + 1):
            s = 0
            while True:
                if s == 10:
                    break
                try:
                    date_temp = universe.index[t]
                    loc_temp = data_sec[s].index.get_loc(date_temp)
                    data_sec_valid[s].ix[loc_temp, [universe.ix[t, i], universe.ix[t, i] + ".1", universe.ix[t, i] + ".2", universe.ix[t, i] + ".3"]] = data_sec[s].ix[loc_temp, [universe.ix[t, i], universe.ix[t, i] + ".1", universe.ix[t, i] + ".2", universe.ix[t, i] + ".3"]]
                    break                    
                    
                except:
                    s += 1
                    continue

#    data_sec_temp = []
#    for i in range(len(data_sec_valid)):
#        data_sec_temp.append([])
#        col_len = data_sec_valid[i].columns.size
#        for j in range(col_len):
#            each_value_temp = pd.DataFrame(index = data_sec_valid[i].index)
#            each_value_temp[data_sec_valid[i].columns[i]] = 
#            data_sec_temp[i].append()
#                            
    temp_list = []
    for i in range(len(data_sec_valid)):
        temp_list.append([])
        col_len = data_sec_valid[i].columns.size
        for j in range(4):
            for k in range(col_len // 4):
                if k == 0:
                    data_each_temp = pd.DataFrame(data_sec_valid[i][data_sec_valid[i].columns[4 * k + j]])
                    continue
                data_each_temp[data_sec_valid[i].columns[4 * k + j]] = data_sec_valid[i][data_sec_valid[i].columns[4 * k + j]]
            temp_list[i].append(data_each_temp)                
            
    
    mean_list, std_list = [], []
    for i in range(len(temp_list)):
        mean_list.append([])
        std_list.append([])
        for j in range(4):
            mean_list[i].append(np.mean(temp_list[i][j], axis = 1))
            std_list[i].append(np.std(temp_list[i][j], axis = 1))
            
    f = lambda x: norm.cdf(x)
    for i in range(len(temp_list)):
        for j in range(4):
            temp_list[i][j] = (temp_list[i][j].sub(mean_list[i][j], axis = 'index')).divide(std_list[i][j], axis = 'index')
            temp_list[i][j] = temp_list[i][j].applymap(f)
        
    for i in range(len(temp_list)):
        df_temp = pd.concat([temp_list[i][0], temp_list[i][1], temp_list[i][2], temp_list[i][3]], axis = 1)
        temp_list[i] = df_temp
            
                
    return temp_list
    
def get_absolute_value(data_sec, universe):
    f = lambda x: math.nan
    data_sec_valid = data_sec.copy()
    
    for i in range(len(data_sec)):
        data_sec_valid[i] = data_sec_valid[i].applymap(f)
        
    for t in range(universe.index.size):
        nUniverse = universe.ix[t, :].dropna().size
        for i in range(1, nUniverse + 1):
            s = 0
            while True:
                if s == 10:
                    break
                try:
                    date_temp = universe.index[t]
                    loc_temp = data_sec[s].index.get_loc(date_temp)
                    data_sec_valid[s].ix[loc_temp, [universe.ix[t, i], universe.ix[t, i] + ".1", universe.ix[t, i] + ".2", universe.ix[t, i] + ".3"]] = data_sec[s].ix[loc_temp, [universe.ix[t, i], universe.ix[t, i] + ".1", universe.ix[t, i] + ".2", universe.ix[t, i] + ".3"]]
                    break                    
                    
                except:
                    s += 1
                    continue
                
    mean_list, std_list = [], []
    for i in range(len(data_sec_valid)):
        mean_list.append([])
        std_list.append([])
        mean_list[i] = np.mean(data_sec_valid[i], axis = 1)
        std_list[i] = np.std(data_sec_valid[i], axis = 1)
            
    f = lambda x: norm.cdf(x)      
    for i in range(len(data_sec_valid)):
        data_sec_valid[i] = (data_sec_valid[i].sub(mean_list[i], axis = 'index')).divide(std_list[i], axis = 'index')
        data_sec_valid[i] = data_sec_valid[i].applymap(f)
    
    return data_sec_valid  
    
    
def get_normalised_value(value, mean, std):
    std_val = []
    f = lambda x: norm.cdf(x)
    for i in range(len(mean)):
        std_val.append((value[i] - mean[i]) / std[i])
        std_val[i] = std_val[i].applymap(f)
        
    return std_val
    
    
def get_triangle_area(nabs, nrel, nhis):
    area_list = []
    for i in range(len(nabs)):
        area_list.append([])
        area_list[i] = (nabs[i] * nrel[i] + nabs[i] * nhis[i] + nrel[i] * nhis[i]) / 2
        
    return area_list

         
def get_tilted_value(area):
    tilt_val_sec = []
    for i in range(len(area)):
        col_len = area[i].columns.size
        tilt_val_sec.append([])
        tilt_val_temp = []
        for j in range(4):
            for k in range(col_len // 4):
                if k == 0:
                    data_each_temp = pd.DataFrame(area[i][area[i].columns[4 * k + j]])
                    data_each_temp.columns = [area[i].columns[4 * k]]
                    continue
                data_each_temp[area[i].columns[4 * k]] = area[i][area[i].columns[4 * k + j]]
            tilt_val_temp.append(data_each_temp)
        tilt_val_sec[i] = tilt_val_temp[0] * tilt_val_temp[1] * tilt_val_temp[2] * tilt_val_temp[3]
        
    return tilt_val_sec

    
def get_tilted_value_onlyPCR(area):
    tilt_val_sec = []
    for i in range(len(area)):
        col_len = area[i].columns.size
        tilt_val_sec.append([])
        tilt_val_temp = []
        for j in range(4):
            for k in range(col_len // 4):
                if k == 0:
                    data_each_temp = pd.DataFrame(area[i][area[i].columns[4 * k + j]])
                    data_each_temp.columns = [area[i].columns[4 * k]]
                    continue
                data_each_temp[area[i].columns[4 * k]] = area[i][area[i].columns[4 * k + j]]
            tilt_val_temp.append(data_each_temp)
        tilt_val_sec[i] =  tilt_val_temp[0] * tilt_val_temp[1] * tilt_val_temp[2] * tilt_val_temp[3]
        
    return tilt_val_sec
   
            
def get_portfolio(tilted_value, n):
    port_df = pd.DataFrame()
    for i in range(tilted_value.index.size):
        date_temp = tilted_value.index[i]
        list_temp = [date_temp]
        port_temp = tilted_value.ix[i, :]
        port_temp = port_temp.sort_values(axis = 0, ascending = False)
        port_temp = port_temp.ix[0 : n]
        port_temp = list(port_temp.index)
        list_temp.extend(port_temp)
        
        port_df = port_df.append([list_temp])
        
    port_df.pop(0)
    port_df.index = tilted_value.index
        
    return port_df
        
        
def get_Nstocks(tilted_value_merged, n):
    tilted_value_copied = tilted_value_merged.copy()
    for i in range(tilted_value_copied.index.size):
        weight_temp = list(tilted_value_copied.ix[i, :].dropna())
        weight_temp.sort(reverse = True)
        cut_off = weight_temp[n]

        for j in range(tilted_value_copied.columns.size):
            if tilted_value_copied.ix[i, j] <= cut_off:
                tilted_value_copied.ix[i, j] = math.nan
    
    return tilted_value_copied
    
            
        
    
data_sector = get_data(0) # 섹터구분
data_M = get_data(1) # 제조업
data_B = get_data(2) # 은행업
data_I = get_data(3) # 보험업
data_S = get_data(4) # 증권업
data_C = get_data(5) # 여신금융업

sector = ['에너지', '소재', '산업재', '경기소비재', '필수소비재', '의료', '금융', 'IT', '통신서비스', '유틸리티']

# 0: 에너지 ~ 9: 유틸리티

data_s6 = pd.concat([data_B, data_I, data_S, data_C], axis = 1) # 금융 섹터

data_sec = []
for s in range(10):
    data_sec.append(pd.DataFrame())
    if s == 6: # 금융 jump
        continue
    
    for i in range(data_sector.columns.size):
        if data_sector.ix[0, i] == sector[s]:
            data_sec[s][data_sector.columns[i]] = data_M[data_sector.columns[i]]
            data_sec[s][data_sector.columns[i] + ".1"] = data_M[data_sector.columns[i] + ".1"]
            data_sec[s][data_sector.columns[i] + ".2"] = data_M[data_sector.columns[i] + ".2"]
            data_sec[s][data_sector.columns[i] + ".3"] = data_M[data_sector.columns[i] + ".3"]

data_sec[6] = data_s6

universe = get_universe(data_M)

value_his_mean, value_his_std = get_historical_value(data_sec, universe)

norm_val_his = get_normalised_value(data_sec, value_his_mean, value_his_std)



norm_val_rel = get_relative_value(data_sec, universe)



norm_val_abs = get_absolute_value(data_sec, universe)

area = get_triangle_area(norm_val_abs, norm_val_his, norm_val_rel)

for i in range(len(area)):
    area[i] = area[i] / 1.5
    area[i] = 1 - area[i]







#tilted_value = get_tilted_value(area)



tilted_value = get_tilted_value_onlyPCR(area)

tilted_value_merged = tilted_value[0]
for i in range(9):
    tilted_value_merged = pd.concat([tilted_value_merged, tilted_value[i + 1]], axis = 1)



tilted_value_merged = tilted_value_merged.dropna(axis = 0, how = 'all')
tilted_value_merged = tilted_value_merged.asfreq('M', method = 'ffill')
tilted_value_merged = get_Nstocks(tilted_value_merged, 20)
        
tilted_value_merged_mean = np.mean(tilted_value_merged, axis = 1)
tilted_value_merged_std = np.std(tilted_value_merged, axis = 1)

tilted_value_merged_norm = (tilted_value_merged.sub(tilted_value_merged_mean, axis = 'index')).div(tilted_value_merged_std, axis = 'index')

tilted_value_merged_norm = tilted_value_merged_norm.applymap(norm.cdf)

portfolio = get_portfolio(tilted_value_merged, 20)
#
#portfolio = portfolio.asfreq('M', method = 'ffill')
#portfolio.to_excel('/Users/Sejoon/Desktop/port_0811_20.xlsx')




tilted_value_merged = 1 - tilted_value_merged

portfolio.to_excel('/Users/Sejoon/Desktop/Backtest/1028port.xlsx')
tilted_value_merged.to_excel('/Users/Sejoon/Desktop/Backtest/1028weight.xlsx')







#tilted_value_merged_norm.to_excel('/Users/Sejoon/Documents/KSIF/Backtest/0917_value_norm.xlsx')
#
#xls = pd.ExcelFile('/Users/Sejoon/Documents/KSIF/Backtest/0830_eps_52max.xlsx')
#eps52 = xls.parse()
#
#xls = pd.ExcelFile('/Users/Sejoon/Documents/KSIF/Backtest/0830_value_norm.xlsx')
#value_norm = xls.parse()
#
#port = eps52 + value_norm
#
#for i in range(port.index.size):
#    port_temp = port.ix[i, :].dropna()
#    port_temp.sort_values(ascending = False, inplace = True)
#    port_temp = port_temp[:40]
#    port.ix[i, :] = port_temp
#
#tickers = pd.DataFrame()
#for i in range(port.index.size):
#    ticker_temp = [port.index[i]]
#    for j in range(port.columns.size):
#        if not math.isnan(port.ix[i, j]):
#            ticker_temp.append(port.columns[j])
#    tickers = tickers.append([ticker_temp])     
#            
#tickers.index = tickers.pop(0)
#            
#            
#tickers.to_excel('/Users/Sejoon/Documents/KSIF/Backtest/0830_tilted.xlsx')
#            
            
            


