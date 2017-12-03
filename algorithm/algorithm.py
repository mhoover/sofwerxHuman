#!/usr/bin/python
import argparse
import json
import pandas as pd
import random

def create_flat_df(x):
    tmp = pd.DataFrame.from_dict({
        (i, j): x[i][j] for i in x.keys() for j in x[i].keys()
    }, orient='index').transpose().unstack().reset_index()
    tmp = tmp.pivot_table(index=['level_0', 'level_2'], columns='level_1',
                          values=0).reset_index()
    tmp.rename(columns={
        'level_0': 'id',
        'level_2': 'date',
    }, inplace=True)

    return tmp


def load_data(file):
    with open(file, 'r') as f:
        tmp = json.load(f)

    return tmp


def run(args_dict):
    # load data sources
    instr = load_data(args_dict['instruments'])
    mock = load_data(args_dict['mock_data'])
    bio = load_data(args_dict['biomeasures'])

    # reshape data
    mock = create_flat_df(mock)
    bio = create_flat_df(bio)
    instr = pd.DataFrame({
        'id': [x for x in instr.keys()],
        'tipi_extraversion':
            [instr[x]['tipi']['extraversion'] for x in instr.keys()],
        'tipi_agreeableness':
            [instr[x]['tipi']['agreeableness'] for x in instr.keys()],
        'tipi_conscientiousness':
            [instr[x]['tipi']['conscientiousness'] for x in instr.keys()],
        'tipi_emotional_stability':
            [instr[x]['tipi']['emotional_stability'] for x in instr.keys()],
        'tipi_openness_to_experiences':
            [instr[x]['tipi']['openness_to_experiences'] for x in
             instr.keys()],
        'tci_vision':
            [instr[x]['tci']['vision'] for x in instr.keys()],
        'tci_task_orientation':
            [instr[x]['tci']['task_orientation'] for x in instr.keys()],
        'tci_support_for_innovation':
            [instr[x]['tci']['support_for_innovation'] for x in instr.keys()],
        'tci_participative_safety':
            [instr[x]['tci']['participative_safety'] for x in instr.keys()],
        'date': '2017-12-07',
    })

    # calculations
    rem_sleep = bio.groupby('id').rem.sum() / 60**2
    rem_sleep_div = rem_sleep / (1.8*7)
    tot_sleep_div = bio.groupby('id').non_rem.sum() / 60**2 / 7**2 + rem_sleep_div
    sleep_score = (pd.concat([rem_sleep_div, tot_sleep_div], axis=1).
                   apply(lambda x: x.mean(), axis=1) * 4/5 * 100)

    bio['activity'] = bio.apply(lambda x: .2 * (x.steps/10000) + .8 *
                                (x.walked_meters/7620), axis=1)
    activity_score = bio.groupby('id').activity.mean() * 3/5 * 100

    instr['tipi'] = instr.filter(regex='tipi_').apply(lambda x: x.mean(), axis=1)
    tipi_score = instr.groupby('id').tipi.sum() / 7 * 100

    instr['tci'] = (((instr.tci_support_for_innovation +
                      instr.tci_task_orientation) / 2 * .8) +
                    ((instr.tci_participative_safety +
                            instr.tci_vision) / 2 * .2))
    tci_score = instr.groupby('id').tci.sum() / 5 * 100

    hrv_mean = mock.groupby('id').hrv.mean()
    hrv_ratio = hrv_mean / mock.groupby('id').hrv.std() / 10
    hrv_score = (((hrv_mean/64.48) * 100) * (1-hrv_ratio)) * 2/5

    skin_score = mock.groupby('id').skin_temp.sum() / 7 * 1/5 * 100

    hydration_score = mock.groupby('id').hydration_tag.sum() / 7 * 4/5 * 100

    nutrition_score = mock.groupby('id').nutrition_tag.sum() / 7 * 4/5 * 100

    medical_score = mock.groupby('id').medical_risk.sum() / 70 * 4/5 * 100

    life_event_score = mock.groupby('id').life_event_risk.sum() / 70 * 3/5 * 100

    psych_df = pd.DataFrame({
        'id': ['a{}'.format(i) for i in xrange(5)],
        'psych_eval': [random.uniform(1, 3) for x in xrange(5)],
    })
    psych_score = psych_df.groupby('id').psych_eval.sum() / 3 * 100

    # combine data
    df = pd.concat([
        sleep_score,
        activity_score,
        tipi_score,
        tci_score,
        hrv_score,
        skin_score,
        hydration_score,
        nutrition_score,
        medical_score,
        life_event_score,
        psych_score,
    ], axis=1)
    df.rename(columns={
        0: 'sleep',
    }, inplace=True)

    # calculate buddy score
    df['buddy_score'] = df.apply(lambda x: x.mean(), axis=1)

    df.rename(columns={
        'tipi': 'tipi_score',
        'tci': 'tci_score',
        'hrv': 'heart_rate_var',
        'life_event': 'life_event_risk',
    }, inplace=True)

    # create json and output
    data_json = df.transpose().to_dict()
    with open(args_dict['output'], 'w') as f:
        json.dump(data_json, f)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Combine notional data and '
                                     'generate buddy score.')
    parser.add_argument('-b', '--biomeasures', required=True, help='Name of '
                        'JSON object with biomeasures.')
    parser.add_argument('-i', '--instruments', required=True, help='Name of '
                        'JSON object with instrument scores.')
    parser.add_argument('-m', '--mock_data', required=True, help='Name of '
                        'JSON object with mock data scores.')
    parser.add_argument('-o', '--output', required=True, help='Name of output '
                        'file for buddy score.')
    args_dict = vars(parser.parse_args())

    run(args_dict)
