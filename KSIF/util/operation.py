"""
Utilities

Author: Seung Hyeon Yu, November 2016
"""

import pandas as pd
import os


def ranking(data: pd.DataFrame, group, key, option='relative'):
    filtered = pd.DataFrame({})
    filtered[key + 'r'] = data.groupby(group)[key].rank(ascending=True)
    out = pd.concat([data, filtered[key + 'r']], axis=1)
    temp = out.groupby(group)

    if option == 'absolute':
        return temp[key + 'r']
    elif option == 'relative':
        return temp[key + 'r'].apply(lambda x: x / len(x))
    else:
        print(" Need ranking Option ! Choose {'relative', 'absolute'}")
        return None


def curpath():
    pth, _ = os.path.split(os.path.abspath(__file__))
    return pth
