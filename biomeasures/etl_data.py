#!/usr/bin/python
import argparse
import pandas as pd

from datetime import datetime


def etl_data_source(file):
    # read in data
    tmp = pd.read_csv(file, sep=None, engine='python')

    # convert string timestamp to numeric
    tmp.timestamp = tmp.timestamp.apply(
        lambda x: datetime.strptime(x, '%m/%d/%y %H:%M')
    )

    # calculate day
    tmp['day'] = tmp.timestamp.dt.date

    # get index of (then subset) maximal values collected per person per day
    idx = tmp.groupby(['id', 'day']).timestamp.transform(max) == tmp.timestamp
    tmp = tmp[idx]

    # calculate total time capture for day
    tmp['total_time'] = (
        tmp.timestamp.dt.hour * 60**2 +
        tmp.timestamp.dt.second * 60 +
        tmp.timestamp.dt.minute
    )

    return tmp


def run():
    # work on sleep data
    sleep = etl_data_source(SLEEP)

    # calculate percents of sleep types
    sleep['rem'] = sleep.apply(
        lambda x: x.restful_seconds / float(x.total_time), axis=1
    )
    sleep['non_rem'] = sleep.apply(lambda x:
        (x.sleep_seconds - x.restful_seconds) / float(x.total_time), axis=1
    )
    sleep['awake'] = sleep.apply(lambda x: 1 - (x.rem + x.non_rem), axis=1)

    # calculate total values for 24-hour period
    sleep[['rem', 'non_rem', 'awake']] = (
        sleep[['rem', 'non_rem', 'awake']].apply(lambda x: x*24, axis=1)
    )

    # values for calculation
    sleep = sleep[['id', 'day', 'rem', 'non_rem', 'awake']]

    # work on step measures
    steps = etl_data_source(STEPS)

    # calculate final values to output
    steps.active_seconds = steps.apply(
        lambda x: (x.active_seconds / float(x.total_time)) * 24, axis=1
    )
    steps = steps[['id', 'day', 'step_count', 'active_seconds', 'walked_meters']]

    # output data
    sleep.to_csv('biomeasures/sleep_output.csv', index=False)
    steps.to_csv('biomeasures/steps_output.csv', index=False)


if __name__ == '__main__':
    SLEEP = 'biomeasures/sleep_measures.csv'
    STEPS = 'biomeasures/steps_measures.csv'

    run()
