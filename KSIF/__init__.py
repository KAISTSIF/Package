"""
KSIF (KAIST Student Investement Fund) Package for Python
========================================================

This package includes modules to help investment activities such as backtest, validation.

Contents
--------
KSIF imports all the functions from the NumPy, Pandas, Matplotlib

Subpackages
-----------
Using any of these subpackages requires an explicit import.  For example,
``import KSIF.backtest``.


::

 core                      --- Build Strategy, backtest
 util                      --- Utilities
 miner                     --- Text Mining from seb
 ML                        --- Machine Learning Algorithms
 core.io                   --- Data input and output


Tutorial
--------
::

First, import KSIF package::

>>> import KSIF

Then, check KSIF version; X:Y:Z,
X means structurual version, Y is major version, Z is minor version::

>>> KSIF.__version__
'0.1.0'

You can see how to use modules by 'help' built-in function::

>>> help(KSIF.core)
Help on package KSIF.core in KSIF:

NAME
    KSIF.core
...

We can make our own strategy, and test it using real stock data.
Let's make purely random strategy; selecting stocks randomly::

>>> strategy = KSIF.core.base.strategy_rand(prob = 0.1)

This means that create strategy_rand class with selecion probability of 10%.
Then we have to get time-series data which has stock prices, and names::

>>> data = KSIF.core.io.load()

Then you create automatically create 'data' using built-in input data.
Now, using 'buildport' Method, you can create portfolio::

>>> port = strategy.buildport(data)
>>> port
...
[35514 rows x 156 columns]

using the portfolio we can get portfolio return by 'backtest'.
And check average return::

>>> port_ret = KSIF.core.base.backtest(port)
>>> port_ret['RETM'].mean()
0.01691531  (it can be different any time you try)

Also, graph it using io module::

>>> KSIF.core.io.graph(port_ret)
...graph out...





For more information visit ::

* KSIF naver cafe : http://cafe.naver.com/kaistsif

Or contact here ::

* 유승현 E-mail : rambor12@business.kaist.ac.kr

"""

__title__ = 'KSIF'
__author__ = 'Seung Hyeon Yu'

__all__ = ['core', 'util', 'team3', 'miner']
# TODO: 새로운 모듈을 만들면 여기에 꼭 등록을 할 것!
from . import core, util, team3, miner
from .core import *
from .core import base, io
from .core.io import *
from .core.base import *
from .util import *
from .util import format, math, operation
from .util.format import *
from .miner import dart
# TODO: 각 팀이 만든 모듈은 꼭 등록할 필요 없음!
from .team3 import *

__all__.extend(core.__all__)
__all__.extend(util.__all__)

from .version import version as __version__
