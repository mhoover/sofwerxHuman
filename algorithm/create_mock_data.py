#!/usr/bin/python
import argparse
import json
import numpy as np
import random


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
        hrv = [random.randint(20, 100) for i in xrange(args_dict['time'])]
        skin = [np.random.binomial(1, .79) for x in xrange(args_dict['time'])]
        hyd = [np.random.binomial(1, .86) for x in xrange(args_dict['time'])]
        nut = [np.random.binomial(1, .75) for x in xrange(args_dict['time'])]
        med = [random.choice(xrange(10))+1 for x in xrange(args_dict['time'])]
        life = [random.choice(xrange(10))+1 for x in xrange(args_dict['time'])]

        # expand to dictionary
        hrv = create_dict_values(hrv, args_dict['time'])
        skin = create_dict_values(skin, args_dict['time'])
        hyd = create_dict_values(hyd, args_dict['time'])
        nut = create_dict_values(nut, args_dict['time'])
        med = create_dict_values(med, args_dict['time'])
        life = create_dict_values(life, args_dict['time'])

        # update data
        results.update(
            {
                rid: {
                    'hrv': hrv,
                    'skin_temp': skin,
                    'hydration_tag': hyd,
                    'nutrition_tag': nut,
                    'medical_risk': med,
                    'life_event_risk': life,
                }
            }
        )

    # output results
    with open('{}.json'.format(args_dict['output']), 'w') as f:
        json.dump(results, f)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create mock data.')
    parser.add_argument('-n', '--nsize', required=True, type=int, help='The '
                        'number of people to generate.')
    parser.add_argument('-t', '--time', required=True, type=int, help='Number '
                        'of days to generate.')
    parser.add_argument('-o', '--output', required=True, help='Name of output '
                        'file.')
    args_dict = vars(parser.parse_args())

    run(args_dict)
