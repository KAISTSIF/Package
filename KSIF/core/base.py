"""
Base and utility classes for KSIF objects.

Contents
--------
implementation power와 범용성을 높이기 위해 전략을 객체화합니다.
객체화된 전략은 크게 두가지 데이터구조가 필요합니다.

1. 전략들의 parameter 정보가 담긴 데이터
2. 포트폴리오를 만드는 방법

보통 python based algorithm trading 모듈들은 위와 같은 데이터구조를 위해서
전략을 Class로 지정합니다.
저는 특히 1번 데이터 구조를 위해 Dictionary 클래스를 이용했습니다.
Dictionary를 상속하여 Strategy 클래스를 만들었기 때문에 Indexing, Sorting,
데이터의 In and Out이 가능합니다.
2번 방법 구조를 만들기 위해서는 메서드를 사용했습니다.
buildport라고 하는 고정된 메서드를 만들어 default로 filtering하는 방법을 사용할수도,
사용자가 필요에 따라서 buildport 메서드를 새롭게 정의할 수 있습니다.

Strategy를 처음 만들때에는 반드시 Dictionary 정보와 BuildPort 메서드를 정의해야합니다.
보통의 경우에는 전략마다 새로운 클래스에 Strategy 클래스를 상속하여 사용합니다.


Examples : SPP 전략 클래스를 만들때
-----------------------------------

>>> class SPP(Strategy):
...
>>>    def buildport(self, input):
...
>>>       return port

Notes
-----

이 떄 input에 꼭 필요한 column에는 DATE FNSECTCODE FIRMCO RETM NAME FNSECTNAME 이 있습니다.
"""
__author__ = 'Seung Hyeon Yu'
__email__  = 'rambor12@business.kaist.ac.kr'

import random

from KSIF.core import io
from KSIF.util import math, operation


class Strategy(dict):
    """
    전략 클래스

    dictionary를 상속받아 필요한 parameter 저장
    buildport 메소드로 portfolio 생성
    """

    # TODO: 필요한 수정사항이 생기면 이렇게 노트해놓아야 합니다.

    def __init__(self, *args, **kwargs):
        super(Strategy, self).__init__(*args, **kwargs)
        self.keylist = super(Strategy, self).keys()
        self.freq = 'Month'
        self.type = 'Screening'
        self.name = 'Basic'
        self.part = 0.25

    def __setitem__(self, key, value):
        super(Strategy, self).__setitem__(key, value)

    def __getitem__(self, idx):
        return dict.__getitem__(self, idx)

    def __iter__(self):
        return iter(self.keylist)

    def __str__(self):
        return " Strategy\t: " + self.name + "\n Type\t: " + self.type

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return False

    def __nq__(self, other):
        return not self.__eq__(other)

    def keys(self):
        return self.keylist

    def values(self):
        return [self[key] for key in self]

    def copy(self):
        return Strategy(dict.copy(self))

    def sortedKeys(self):
        sortedItems = self.items()
        compare = lambda x, y: math.sign(y[1] - x[1])
        sortedItems.sort(cmp=compare)
        return [x[0] for x in sortedItems]

    def totalCount(self):
        return sum(self.values())

    def incrementAll(self, keys, count):
        for key in keys:
            self[key] += count

    def argMax(self):
        if len(self.keys()) == 0: return None
        all = self.items()
        values = [x[1] for x in all]
        maxIndex = values.index(max(values))
        return all[maxIndex][0]

    def divideAll(self, divisor):
        divisor = float(divisor)
        for key in self:
            self[key] /= divisor

    def __radd__(self, y):
        for key, value in y.items():
            self[key] += value

    def buildport(self, input):
        port = input
        for key, value in self.items():
            port = port[(port[key] >= value - self.part) & (port[key] < value)]

        return port


def backtest(port, start_date='1700-01-01', end_date='2200-01-01', dates=None):
    if dates is None:
        port = port[(port.DATE > start_date) & (port.DATE <= end_date)]
    else:
        port = port[port['DATE'].isin(dates)]
    port_retm = port.groupby(['DATE'])['RETM'].mean().to_frame()
    port_retm['CUMRET'] = (1 + port_retm['RETM']).cumprod()

    return port_retm


def scoring(x):
    selector = {'소재': ['NI2_Incr', 'OANCF_Incr', 'OANCF2_Incr', 'OIBDP_Incr', 'OIBDP2_Incr', 'SALE_Incr', 'SALE2_Incr'],
                '산업재': ['NI2_Incr', 'OANCF_Incr', 'OIBDP2_Incr', 'SALE2_Incr'],
                '경기소비재': ['AT_Incr', 'OANCF_Incr', 'OANCF2_Incr', 'OIBDP_Incr', 'SALE2_Incr'],
                '필수소비재': ['AT2_incr', 'OANCF_Incr', 'OANCF2_Incr', 'SALE2_Incr'],
                '의료': ['OANCF_Incr', 'OIBDP_Incr', 'OIBDP2_Incr', 'SALE2_Incr'],
                'IT': ['AT_Incr', 'AT2_incr', 'NI_Incr', 'NI2_Incr', 'OANCF_Incr', 'OANCF2_Incr', 'OIBDP_Incr',
                       'OIBDP2_Incr', 'SALE_Incr', 'SALE2_Incr']}
    score = 0
    for key, growth_list in selector.items():
        if x['FNSECTNAME'] == key:
            for growth in growth_list:
                if x[growth] > 2 / 3:
                    score += 2
                elif x[growth] > 1 / 3:
                    score += 1

    return score


class strategy_PERr(Strategy):
    """
    예제 1 : PER ranking 전략
    """

    # 초기 설정
    def __init__(self, *args, **kwargs):
        super(strategy_PERr, self).__init__(*args, **kwargs)
        self.name = 'PER percentile'
        self.part = 0.1

    # port 만들기
    def buildport(self, input):
        return input[(input.PERr > self['PERr'] - self.part) & (input.PERr <= self['PERr'])]


class strategy_rand(Strategy):
    """
    예제 2 : 랜덤 전략
    """

    def __init__(self, prob=0.1):
        self.name = 'random'
        self.prob = prob

    def buildport(self, input):
        # 랜덤하게 prob의 확률로 뽑음
        data = input
        data['random'] = data['MVm'].apply(lambda x: random.random())
        return data[data.random < self.prob]


class strategy_growth(Strategy):
    """
    예제 3 : 섹터별로 Growth 랭크를 점수 매겨서 Portfolio로 만듦
    """

    def __init__(self, *args, **kwargs):
        super(strategy_growth, self).__init__(*args, **kwargs)
        self.name = 'Growth Scoring'
        self.part = 0.33
        self.scorer = 2 / 3

    def buildport(self, input):
        port = input
        port = port[(port.MVmr <= self['MVmr']) & (port.PERr <= self['PERr']) & (port.PBRr <= self['PBRr'])]
        growth_list = ['AT_Inc', 'AT2_inc', 'NI_Inc', 'NI2_Inc', 'OANCF_Inc', 'OANCF2_Inc',
                       'OIBDP_Inc', 'OIBDP2_Inc', 'SALE_Inc', 'SALE2_Inc']
        original_list = ['MVmr', 'PERr', 'PBRr']
        for growth in growth_list:
            port[growth + 'r'] = operation.ranking(port, group=['DATE', 'FNSECTCODE'], key=growth)
        port['score'] = port.apply(scoring, axis=1)
        port['scorer'] = operation.ranking(port, group=['DATE', 'FNSECTCODE'], key='score')
        return port[port.scorer > self.scorer]


class strategy_value(Strategy):
    """
    예제 4 : 가치투자 전략 : SPP sum < 0.5 & ROE OPR > 1.0
    """

    def __init__(self, SPP=0.5, Profit=1.0):
        self.name = 'value'
        self.SPP = SPP
        self.Profit = Profit

    def buildport(self, input):
        return input[(input.MVmr + input.PERr + input.PBRr < self.SPP) & (input.ROE4Qr + input.OPR4Qr > self.Profit)]


def _test():
    """
    예제 3 : 성장성 전략
    """
    print("\t TEST : 성장성 Scoring 전략")
    # 1. Data를 불러옵니다.
    path = operation.curpath() + '\..\\tests\\data\\input'
    data = io.load(path)

    # 2. 꼭 사용할 데이터 list를 만듭니다.
    sector_list = ['FGSC.15', 'FGSC.20', 'FGSC.25', 'FGSC.30', 'FGSC.35', 'FGSC.45']
    growth_list = ['AT_Inc', 'AT2_inc', 'NI_Inc', 'NI2_Inc', 'OANCF_Inc', 'OANCF2_Inc',
                   'OIBDP_Inc', 'OIBDP2_Inc', 'SALE_Inc', 'SALE2_Inc']
    original_list = ['MVmr', 'PERr', 'PBRr']
    selector = {key: 1 for key in original_list + growth_list}

    # 3. inputCleansing을 이용해 필요한 데이터 외에는 없앱니다.
    data = io.cleanse(data, selector=selector)
    data = data[data.FNSECTCODE.isin(sector_list)]

    # 4. 전략 클래스를 생성합니다. (이 때 전략 parameter 값도 정합니다.)
    strategy = strategy_growth({'MVmr': 1 / 2, 'PERr': 1 / 3, 'PBRr': 1 / 3})
    strategy.scorer = 2 / 3

    # 5. 포트폴리오를 생성합니다.
    port = strategy.buildport(data)

    # 6. 백테스트를 실행합니다.
    port_retm = backtest(port, '2010-01-01', '2016-10-10')

    # 7. graph 를 그려 누적수익률을 확인합니다.
    io.graph(port_retm, label="성장성 scoring")


if __name__ == '__main__':
    _test()
