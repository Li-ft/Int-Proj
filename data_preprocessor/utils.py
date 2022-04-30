import math
import pandas as pd
from math import dist
import random
import numpy as np



def decide_staff_num(business_acreage) -> int:
    if business_acreage < 200:
        return math.ceil(business_acreage / 15)
    if 200 <= business_acreage < 3000:
        return math.ceil(business_acreage / 35)
    if 3000 <= business_acreage < 8000:
        return math.ceil(business_acreage / 50)
    if business_acreage >= 8000:
        return math.ceil(business_acreage / 60)

# def decide_throughput_per_hour(business_type: int) -> int:
#     if business_type == 1

def get_agents_in_range(candidate_agents_df: pd.DataFrame, center_coord: tuple, range, agents_num=1):
    mask = candidate_agents_df.apply(lambda row: dist((row['coord_x'], row['coord_y']), center_coord) <= range, axis=1)
    candidate_agents_df = candidate_agents_df[mask]
    if candidate_agents_df.shape[0] <= 0:
        raise ValueError('the candidate should be more than 0')
    return np.array(candidate_agents_df.sample(agents_num, replace=False)['index'])

def choose_acerage(business_acreage, total_acreage):
    if pd.isna(business_acreage):
        return int(total_acreage) / 2
    else:
        return int(business_acreage)

def convert_null_to_0(input):
    return 0 if pd.isna(input) else input

def decide_identity(agents_df, unemployment_rate, retire_age):
    # identity:
    # 0: kids that not old enough to go to school
    # 1: students
    # 2: workers indoor (business point)
    # 3: workers indoor (company)
    # 4: workers outdoor
    # 5: unemployed people
    # 6: retired people
    assert len(agents_df) == agents_df.index[-1] + 1
    agents_df['identity'] = -1

    children_idx = agents_df.query('age<6').index
    agents_df.loc[children_idx, 'identity'] = 0
    student_idx = agents_df.query('6<=age<=16').index
    agents_df.loc[student_idx, 'identity'] = 1

    # the indoor and outdoor workers will be finished in the business point processor py file

    unemployed_candidate_idx = agents_df.query(f'16<age<={retire_age}').index
    unemployed_idx = np.random.choice(unemployed_candidate_idx, int(len(unemployed_candidate_idx)*unemployment_rate), replace=False)
    assert len(unemployed_idx)==len(set(unemployed_idx))
    agents_df.loc[unemployed_idx, 'identity'] = 5
    retired_idx = agents_df.query(f'age>{retire_age}').index
    agents_df.loc[retired_idx, 'identity'] = 6
    # if age > retire_age:
    #     return 6
    # if 16 < age <= retire_age:
    #
    #     return np.random.choice([2, 4, 5], p=[(1-unemployment_rate)*worker_in_office_rate, (1-unemployment_rate)*(1-worker_in_office_rate), unemployment_rate])
    # if age < 6:
    #     return 0
    # if 6 <= age <= 16:
    #     return 1
    return agents_df

def ini_agents_states(household_df: pd.DataFrame,
                      # inf_coeff,
                      unemployment_rate: float,
                      retire_age: int,
                      age_df: pd.DataFrame) -> pd.DataFrame:
    np.random.seed(2019)
    household_df['family_size'] = np.random.choice(range(1, 7),
                                                   household_df.shape[0],
                                                   p=[0.425, 0.322, 0.136, 0.103, 0.012, 0.002])

    rows_list = []
    for idx, row in household_df.iterrows():
        for _ in range(int(row.family_size)):
            rows_list.append({'coord_x': row.coordinate_x,
                              'coord_y': row.coordinate_y,
                              'family_idx': idx})
    agents_df = pd.DataFrame(rows_list, columns=['coord_x', 'coord_y','family_idx'])
    agents_df.rename(columns={'coord_x': 'home_x', 'coord_y': 'home_y'}, inplace=True)
    # agents_df['curr_coord_x'], agents_df['curr_coord_y'] = agents_df['coord_x'], agents_df['coord_y']
    agents_df['covid_status'] = 0
    agents_df['quarantine'] = 0

    agents_df['age'] = np.random.choice(age_df.age, agents_df.shape[0], p=age_df['proportion'])

    # 0: susceptible
    # 1: latent, unconscious, unable to infect others
    # 2: infectious, with high probability to infect others and going to the next level
    # 3: severe, with high probability to die
    # 4: deceased
    # 5: recovered, with lower probability to be infected again, comparing with the susceptible
    # agents_df['covid_state'] = 0
    # agents_df['covid_coeff'] = agents_df.age.apply(lambda x: inf_coeff * (x ** 2))

    # identity:
    # 0: kids that not old enough to go to school
    # 1: students
    # 2: workers indoor (business point)
    # 3: workers indoor (company)
    # 4: workers outdoor
    # 5: unemployed people
    # 6: retired people
    # agents_df['identity'] = agents_df.age.apply(lambda age: decide_identity(age, unemployment_rate, retire_age, worker_in_office_rate))
    # print(agents_df['identity'].value_counts())
    # agents_df['work place'] = None
    print(agents_df.columns)
    agents_df = decide_identity(agents_df, unemployment_rate, retire_age)
    print(agents_df.columns)
    return agents_df


def reset_col_2empty_list(df: pd.DataFrame, *vars):
    for col_name in vars:
        assert type(col_name)==str
        df[col_name] = np.empty((len(df), 0)).tolist()
    return df