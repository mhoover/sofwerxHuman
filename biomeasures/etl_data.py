#!/usr/bin/python
import argparse
import json
import numpy as np
import pandas as pd
import random


SLEEP = [
    28800,
    6480,
]

STEPS = [
    10000,
    7620,
]


def create_dict_values(x, time):
    return {
        key: value for key, value in zip(
            ['2017-12-0{}'.format(i+1) if len(str(i))==1 else
             '2017-12-{}'.format(i+1) for i in xrange(time)], x
        )
    }


def run(args_dict):
    results = {}
    for i in xrange(args_dict['nsize']):
        rid = 'a{}'.format(i)

        # sleep data
        sleep = [np.random.normal(SLEEP[0], .125*SLEEP[0]) for i in
                 xrange(args_dict['time'])]
        rem = [np.random.normal(SLEEP[1], .25*SLEEP[1]) for i in
               xrange(args_dict['time'])]
        non_rem = [x-y for x, y in zip(sleep, rem)]
        assert all([x>=0 for x in non_rem])
        awake = [24*60**2 - x for x in sleep]

        # steps
        steps = [np.random.normal(STEPS[0], .35*STEPS[0]) for i in
                 xrange(args_dict['time'])]
        walkm = [np.random.normal(STEPS[1], .15*STEPS[1]) for i in
                 xrange(args_dict['time'])]

        # expand to dictionary
        awake = create_dict_values(awake, args_dict['time'])
        rem = create_dict_values(rem, args_dict['time'])
        non_rem = create_dict_values(non_rem, args_dict['time'])
        steps = create_dict_values(steps, args_dict['time'])
        walked_meters = create_dict_values(walkm, args_dict['time'])

        # update data
        results.update(
            {
                rid: {
                    'awake': awake,
                    'rem': rem,
                    'non_rem': non_rem,
                    'steps': steps,
                    'walked_meters': walked_meters,
                }
            }
        )

    # output results
    with open('{}.json'.format(args_dict['output']), 'w') as f:
        json.dump(results, f)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Mock biometric data.')
    parser.add_argument('-n', '--nsize', required=True, type=int, help='The '
                        'number of people to generate.')
    parser.add_argument('-t', '--time', required=True, type=int, help='Number '
                        'of days to generate.')
    parser.add_argument('-o', '--output', required=True, help='Name of output '
                        'file.')
    args_dict = vars(parser.parse_args())

    run(args_dict)
