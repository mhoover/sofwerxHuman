#!/usr/bin/python
import argparse
import json
import numpy as np
import pandas as pd
import random

from string import ascii_lowercase, digits


TCI = [
    (0, 11),
    (11, 18),
    (18, 26),
    (26, 38),
]
TIPI = [
    (0, 5),
    (1, 6),
    (2, 7),
    (3, 8),
    (4, 9),
]


def calc_probs(scale):
    if 'high' in scale:
        return [
            .1,
            .3,
        ]
    elif 'medium' in scale:
        return [
            .2,
            .8,
        ]
    else:
        return [
            .7,
            .9,
        ]


def get_survey_values(nbr, probs, i=None):
    if not i:
        if (nbr>=0) & (nbr<probs[0]):
            return random.choice([1, 2])
        elif (nbr>=probs[0]) & (nbr<probs[1]):
            return 3
        else:
            return random.choice([4, 5])
    else:
        if i%2 == 1:
            if (nbr>=0) & (nbr<probs[0]):
                return random.choice([6, 7])
            elif (nbr>=probs[0]) & (nbr<probs[1]):
                return random.choice([3, 4, 5])
            else:
                return random.choice([1, 2])
        else:
            if (nbr>=0) & (nbr<probs[0]):
                return random.choice([1, 2])
            elif (nbr>=probs[0]) & (nbr<probs[1]):
                return random.choice([3, 4, 5])
            else:
                return random.choice([6, 7])


def tipi_reversing(x):
    return abs(x - 7) + 1


def calculate_scores(values, scale=['tci', 'tipi']):
    if 'tci' in scale:
        return [np.mean(values[x[0]:x[1]]) for x in TCI]
    else:
        return [np.mean([values[x[0]], tipi_reversing(values[x[1]])]) for x in
                TIPI]


def run(args_dict):
    results = {}
    for i in xrange(args_dict['nsize']):
        rid = 'a{}'.format(i)
        # identify the ranges to sample
        tipi_probs = calc_probs(args_dict['tipi_type'])
        tci_probs = calc_probs(args_dict['tci_type'])

        # generate values
        tci_values = [get_survey_values(random.random(), tci_probs) for x in
                      xrange(38)]
        tipi_values = [get_survey_values(random.random(), tipi_probs, x) for x in
                       xrange(10)]

        # calculate survey scores
        tci_scores = calculate_scores(tci_values, 'tci')
        tipi_scores = calculate_scores(tipi_values, 'tipi')

        # update data
        results.update(
            {
                rid: {
                    'tipi': {name: value for name, value in zip(
                             ['extraversion', 'agreeableness',
                             'conscientiousness', 'emotional_stability',
                             'openness_to_experiences'], tipi_scores)},
                    'tci': {name: value for name, value in zip(
                            ['vision', 'task_orientation',
                            'support_for_innovation', 'participative_safety'],
                            tci_scores)},
                }
            }
        )

    # output results
    df = pd.DataFrame({
        'id': [x for x in results.keys()],
        'tipi_extraversion':
            [results[x]['tipi']['extraversion'] for x in results.keys()],
        'tipi_agreeableness':
            [results[x]['tipi']['agreeableness'] for x in results.keys()],
        'tipi_conscientiousness':
            [results[x]['tipi']['conscientiousness'] for x in results.keys()],
        'tipi_emotional_stability':
            [results[x]['tipi']['emotional_stability'] for x in results.keys()],
        'tipi_openness_to_experiences':
            [results[x]['tipi']['openness_to_experiences'] for x in
             results.keys()],
        'tci_vision':
            [results[x]['tci']['vision'] for x in results.keys()],
        'tci_task_orientation':
            [results[x]['tci']['task_orientation'] for x in results.keys()],
        'tci_support_for_innovation':
            [results[x]['tci']['support_for_innovation'] for x in results.keys()],
        'tci_participative_safety':
            [results[x]['tci']['participative_safety'] for x in results.keys()],
    })
    df.to_csv('{}.csv'.format(args_dict['output']), index=False)
    with open('{}.json'.format(args_dict['output']), 'w') as f:
        json.dump(results, f)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Data generator for '
                                     'psychological scales.')
    parser.add_argument('-n', '--nsize', required=True, type=int, help='The '
                        'number of people to generate.')
    parser.add_argument('-t', '--tipi_type', required=True, choices=['high',
                        'medium', 'low'], help='Types of tipi scores to '
                        'generate.')
    parser.add_argument('-c', '--tci_type', required=True, choices=['high',
                        'medium', 'low'], help='Types of tci scores to '
                        'generate.')
    parser.add_argument('-o', '--output', required=True, help='Name of output '
                        'file.')
    args_dict = vars(parser.parse_args())

    run(args_dict)
