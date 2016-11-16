"""
Input and Output
"""
__author__ = 'Seung Hyeon Yu'
__email__  = 'rambor12@business.kaist.ac.kr'

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager, rc
from KSIF.util import format, operation

# test data : index path
TESTINDPATH = operation.curpath() + '\..\\tests\\data\\index'


def load(file=None, date=1):
    # TODO: Warning 경고 뜨는 이유 해결하기
    if file is None:
        file = operation.curpath() + '\..\\tests\\data\\input'
    if '.csv' in file:
        filetype = 'csv'
    elif '.h5' in file:
        filetype = 'h5'
    else:
        filetype = None

    if (filetype is None and os.path.isfile(file + '.h5')) or filetype == 'h5':
        data = pd.read_hdf(file + '.h5', key='ksif')
    elif filetype == 'csv' or filetype is None:
        data = pd.read_csv(file + '.csv', encoding='euc-kr')
        if date == 1:
            data['DATE'] = pd.to_datetime(data['DATE'])
        mask = list(set(data.columns[data.dtypes == object]))
        data[mask] = data[mask].applymap(format.to_numeric)
        data.to_hdf(file + '.h5', key='ksif')
    return data


def cleanse(data, selector=None):
    # TODO: Warning 경고 뜨는 이유 해결하기
    del data['RETM']
    data['RETM'] = np.where(pd.isnull(data['RETMA']), -1, data['RETMA'])
    '''
    retm = input[['DATE', 'FNSECTCODE', 'FIRMCO', 'RETM']]
    retm = retm.sort_values(['FIRMCO', 'DATE'], ascending=[True, True])
    retm['RETM'] = retm.groupby(['FIRMCO'])['RETM'].transform(lambda x: x.shift(-1))
    '''
    if selector is not None:
        key_array = []
        for key in list(selector.keys()):
            if key[-1] == 'r':
                key_array.append(key[:-1])
            else:
                key_array.append(key)
        data = data[['DATE', 'NAME', 'FNSECTCODE', 'FNSECTNAME', 'FIRMCO', 'RETM'] + key_array]
        for key in list(selector.keys()):
            if key[-1] == 'r':
                filtered = data[data[key[:-1]] > 0]
                data[key] = operation.ranking(filtered, group=['DATE', 'FNSECTCODE'], key=key[:-1])
    '''
    input = pd.concat([input, retm.RETM], axis=1, join_axes=[input.index])
    '''
    return data


def graph(port_retm, label='strategy', index=None):
    plt.plot(port_retm['CUMRET'].apply(lambda x: (x - 1) * 100), 'r-', label=label)
    if index is not None:
        index_set = load(TESTINDPATH)
        index_set = index_set[(index_set.DATE >= port_retm.index[0]) & (index_set.DATE <= port_retm.index[-1])]
        index_set = index_set.set_index(['DATE'])
        INIT = index_set[index_set.index == port_retm.index[0]][index + '_close']

        # Decorate #
        # TODO: x, y축 폰트 깨짐
        font_name = font_manager.FontProperties(fname="c:/Windows/Fonts/윤고딕310_0.ttf").get_name()
        rc('font', family=font_name, size=16)

        plt.plot(index_set[index + '_close'].apply(lambda x: (x / INIT - 1) * 100), 'b--', label=index)

    plt.ylabel('누적 수익률 (%)')
    plt.legend(loc='upper left')
    plt.show()
