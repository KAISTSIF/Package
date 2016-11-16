"""
Format Transformation

Author: Seung Hyeon Yu, November 2016
"""

import datetime
import time

import numpy as np
import pandas as pd

DECIMAL = 2


def prettyfloat(number):
    return "{:9.2f}".format(number)


def to_numeric(string):
    """
    numeric if parsing succeeded. Otherwise, str itself.
        Return type depends on input.
    :type string: str
    """

    if pd.isnull(string) or isinstance(string, float):
        return string
    else:
        try:
            return float(string.replace(',', ''))
        except:
            return string


def get_form(date):
    """
    Get Form from the date

    :param date:
    :return: form
    """
    if isinstance(date, str):
        if len(date) == 8:
            form = "%Y%m%d"
        elif '-' in date:
            form = "%Y-%m-%d"
        elif '/' in date:
            form = "%Y/%m/%d"
        elif '.' in date:
            form = "%Y.%m.%d"
        else:
            raise NotImplementedError

    return form


def date_to_numeric(date):
    """
    Return Unix Time which is total elapsed nanoseconds from 1970-01-01

    :param date: any time format
    :return: int total elapsed nanoseconds from 1970-01-01
    """
    if isinstance(date, pd.tslib.Timestamp):
        return date.value
    elif isinstance(date, (pd.datetime, np.datetime64)):
        return pd.Timestamp(date).value
    elif isinstance(date, str):
        return int(time.mktime(str_to_date(date).timestamp()))


def date_to_str(date, form="%Y-%m-%d"):
    """
    Return Date String

    :param date: date
    :param form: format of return
    :return: str formatted date time
    """
    if isinstance(date, str):
        return date
    elif isinstance(date, (pd.tslib.Timestamp, pd.datetime)):
        return date.strftime(form)


def str_to_date(date, form=None):
    """
    Return Date with datetime format

    :param form:
    :param date: str date
    :return: datetime date
    """
    if form is None:
        form = get_form(date)
    return datetime.datetime.strptime(date, form)


def to_list(*args):
    """
    Return arbitrary values to list

    :return: list of listed values
    """
    result = []
    for arg in args:
        if isinstance(arg, (str, int, float)):
            result.append([arg])
        elif isinstance(arg, (list, pd.Series, np.ndarray)):
            result.append(list(arg))
        elif arg is None:
            result.append(arg)
        else:
            raise NotImplementedError
    return result
