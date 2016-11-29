"""
CSCV module

 CSCV(Combinatorially Symmetric Cross Valdiation)란?

 어떤 전략을 backtesting하면서 좋은 전략을 찾으려고 할 때 과거 데이터는 고정되어있기 때문에
 언제나 backtest overfitting할 가능성이 있다.
 overfitting 문제를 피하기 위해서 사용하는 방법이 CSCV이다.
 Time Series Data를 일정한 등분으로 쪼개서 In Sample(IS)과 Out of Sample(OOS)로 나눠
 모든 조합에 대해 IS에서 가장 좋은 전략이 OOS에서 여전히 좋은지 체크한다.
 그 때 IS에서 제일 좋은 전략이 OOS에서 median 이하의 performance를 보여줄 경우를
 모두 카운트하여 Probability of Backtest Overfitting이라 정의한다.
 이를 통해 전략 선택 과정이 얼마나 overfit 되었는지 확인할 수 있다.

 (David H. Bailey et al, Journal of Computational Finance, 2015)

"""
__author__ = 'Seung Hyeon Yu'
__email__ = 'rambor12@business.kaist.ac.kr'

from KSIF.core.io import *
from KSIF.core.base import *
import itertools


class CSCV:
    """
    How to use

    ----------

     먼저 strategy set과 input data를 만든다::

       >>> strategy_set = [Strategy({'keys':i}) for i in range(10)]

     그리고 result 객체를 CSCV를 통해 생성한다::

       >>> result = CSCV(strategy_set, input)

      result 객체는 CSCV 클래스로 필요에 따라 summary, histogram, performace data를 추출할 수 있다::

       >>> print(result)

    """

    def __init__(self, strategy_set, data, part=16, measure='AVG RETM'):
        """

        :type strategy_set: list of strategies
        """
        self.part = part
        self.strategy_set = strategy_set
        self.PBO = None
        self.stability = []
        self.ranks = []
        self.performance = {'IS': [], 'OOS': []}
        self.strategies = []
        self.combination = 0
        self.log = "IS Combination\tIndex\tIS Best perf\t    OOSperf / OOS bestperf\trank\n"
        self.start = str(np.array(data['DATE'])[0])[:10]
        self.end = str(np.array(data['DATE'])[-1])[:10]
        self.measure = measure

        # Setting
        data = data
        port_set = []
        for strategy in strategy_set:
            port_set.append(strategy.buildport(data))

        date = np.array_split(list(data['DATE'].drop_duplicates()), self.part)

        # Do Validation with all combinations
        combination = list(itertools.combinations(range(self.part), int(self.part / 2)))
        self.combination = len(combination)
        print(self.log)
        for IS in combination:
            OOS = list(set(range(self.part)) - set(IS))
            # select best strategy
            perf = []
            for port in port_set:
                ret = backtest(port, dates=np.concatenate([date[i] for i in IS], axis=0))
                if self.measure == 'AVG RETM':
                    perf.append(ret['RETM'].mean())
                elif self.measure == 'CUMRET':
                    perf.append(ret['CUMRET'][-1])
                elif self.measure == 'SR':
                    perf.append(ret['RETM'].mean() / ret['RETM'].std())
                elif self.measure == 'AVG RETM and CNT > 20':
                    avg_retm = ret['RETM'].mean()
                    firm_cnt = port.groupby(['DATE'])['FIRMCO'].count().mean()
                    if firm_cnt > 20:
                        perf.append(avg_retm)
                    else:
                        perf.append(-999999999)
                else:
                    perf.append(None)
                    # for i in perf:
                    # print(i)
            self.performance['IS'].append(np.nanmax(perf))
            best_ind = perf.index(np.nanmax(perf))
            IS_ranks = np.array(perf).argsort().argsort()

            perf = []
            for port in port_set:
                ret = backtest(port, dates=np.concatenate([date[i] for i in OOS], axis=0))
                if self.measure == 'AVG RETM':
                    perf.append(ret['RETM'].mean())
                elif self.measure == 'CUMRET':
                    perf.append(ret['CUMRET'][-1])
                elif self.measure == 'SR':
                    perf.append(ret['RETM'].mean() / ret['RETM'].std())
                elif self.measure == 'AVG RETM and CNT > 20':
                    avg_retm = ret['RETM'].mean()
                    firm_cnt = port.groupby(['DATE'])['FIRMCO'].count().mean()
                    if firm_cnt > 20:
                        perf.append(avg_retm)
                    else:
                        perf.append(-999999999)
                else:
                    perf.append(None)
                    # print(" -----")
                    # for i in perf:
                    # print(i)
            self.performance['OOS'].append(perf[best_ind])
            OOS_ranks = np.array(perf).argsort().argsort()

            # get rank
            rank = np.array(perf).argsort().argsort()[best_ind]
            self.ranks.append(rank)
            self.strategies.append(strategy_set[best_ind])
            IS_perf = format.prettyfloat(self.performance['IS'][-1] * 100) + " %"
            OOS_perf = format.prettyfloat(self.performance['OOS'][-1] * 100) + " % /" + format.prettyfloat(
                np.nanmax(perf) * 100) + " % "
            log = str(IS) + "\t" + str(best_ind) + "\t" + IS_perf + "\t" + OOS_perf + "\t" + str(rank)
            print(log)
            self.log += log + "\n"
            self.PBO = (np.array(self.ranks) < len(self.strategy_set) / 2).sum() / self.combination
            '''
            Stability란?
             IS rank vector r(IS)와 OOS rank vector r(OOS)가 있을 때 다음과 같은 Norm을 정의한다.

             |r(IS) - r(OOS)|_(stab) := ( (N-1)N(N+1)/6 - Sum(r(IS)_i - r(OOS)_i)^2 ) / ( (N-1)N(N+1)/6 )

             이는 rank가 얼마나 변하는지 알려주는 -1 ~ 1의 척도로써
             1 : 100% Consistent, rank가 변하지 않는다.
             0 : Fully Random, rank가 랜덤하게 움직인다.
             -1: OOS의 rank가 IS의 rank와 정반대로 움직인다.
            '''
            N = len(self.strategy_set)
            SSE = np.vectorize(lambda x: x ** 2)(np.array(IS_ranks) - np.array(OOS_ranks)).sum()
            stab_rand = (N - 1) * N * (N + 1) / 6
            self.stability.append((stab_rand - SSE) / stab_rand)

    def print(self, option='Summary'):
        result = ""
        if option == 'Summary':
            result = "\n------------------ CSCV SUMMARY ------------------"
            result += "\n DATE\t\t\t: " + self.start + " ~ " + self.end
            result += "\n Strategy Name\t\t: " + self.strategy_set[0].name
            result += "\n # of Strategties\t: " + str(len(self.strategy_set))
            result += "\n # of Time Partition\t: " + str(self.part)
            result += "\n # of Combinations\t: " + str(self.combination)
            result += "\n Performance Measure\t: " + str(self.measure)
            result += "\n\n                     [RESULT]                    "
            result += "\n IS  performance AVG\t: " + format.prettyfloat(np.mean(self.performance['IS']) * 100) + " %"
            result += "\n OOS performance AVG\t: " + format.prettyfloat(np.mean(self.performance['OOS']) * 100) + " %"
            result += "\n PBO \t\t\t: " + format.prettyfloat(self.PBO * 100) + " %"
            result += "\n Rank Stability  \t: " + format.prettyfloat(np.array(self.stability).mean() * 100) + " %"
            result += "\n--------------------------------------------------"
        elif option == 'Histogram':
            pass
        elif option == 'Scatter':
            pass
        elif option == 'Stochastic Dominance':
            pass
        else:
            pass
        return result

    def __repr__(self):
        return "CSCV (Combinatorially Symmetric Cross Validation)"

    def __str__(self):
        return self.print()


def _test():
    data = load(operation.curpath() + '\..\\tests\\data\\data')
original_list = ['MVmr', 'PERr', 'PBRr']
new_list = ['ROE4Qr', 'OPR4Qr']
sector_list = ['FGSC.15', 'FGSC.20', 'FGSC.25', 'FGSC.30', 'FGSC.35', 'FGSC.45']
strategy = Strategy({key: 1 for key in original_list + new_list})
data = cleanse(data, selector=strategy)
data = data[data.FNSECTCODE.isin(sector_list)]
start = '2006-01-01'
end = '2016-01-02'
data = data[(data.DATE >= start) & (data.DATE <= end)]

    '''
    예제 1
    '''
    N = 200
    strategy_set = [strategy_PERr({'PERr': (1 + i) / N}) for i in range(N)]
    result = CSCV(strategy_set, data, part=10)
    print(result)

    '''
    예제 2
    '''
N = 200
strategy_set = [strategy_rand(prob=0.01) for _ in range(N)]
result = CSCV(strategy_set, data, part=10)
    print(result)

    '''
    예제 3
    '''
    strategy_set = []
    for i in range(20):
        for j in range(10):
            strategy_set.append(strategy_value(SPP=j / 10, Profit=i / 10))

    result = CSCV(strategy_set, data, part=10)
    print(result)


if __name__ == '__main__':
    _test()
