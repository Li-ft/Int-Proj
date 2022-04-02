from datetime import datetime
import numpy as np
import pandas as pd
from abm.abmpandemic import ABMPandemic
from sko.GA import GA
from sklearn.metrics import mean_squared_error as mse

begin_date = '2020-02-22'
end_date = '2020-03-31'
agents_df = pd.read_csv(r"C:\Users\maqly\Documents\lectures\Project\interdisciplinary_proj\data\agents.csv",
                        dtype={'home_x': float,
                               'home_y': float,
                               'family_idx': int,
                               'covid_state': int,
                               'age': int,
                               'identity': int,
                               'leisure_timer': int,
                               'use_pt': int,
                               'employer': int,
                               'quarantine': int})
space_df = pd.read_csv(r"C:\Users\maqly\Documents\lectures\Project\interdisciplinary_proj\data\business point.csv",
                       index_col=0,
                       dtype={'type': int,
                              'acreage': float},
                       converters={
                                   # 'susceptible_inside': eval,
                                   # 'infector_inside': eval,
                                   'staffs_idx': eval})

policy_df = pd.read_excel(
    r"C:\Users\maqly\Documents\lectures\Project\interdisciplinary_proj\data\policy constraint.xlsx",
    sheet_name=0,
    index_col='date',
    date_parser=lambda x: pd.datetime.strptime(x, '%Y-%m-%d'))
holiday_df = pd.read_csv(r"C:\Users\maqly\Documents\lectures\Project\interdisciplinary_proj\data\holiday.csv",
                         index_col='date',
                         date_parser=lambda x: datetime.strptime(x, '%Y/%m/%d'))
covid_data_df = pd.read_excel(
    r"C:\Users\maqly\Documents\lectures\Project\interdisciplinary_proj\data\covid data torino province.xlsx",
    sheet_name = 0,
    index_col='Date',
    date_parser=lambda x: datetime.strptime(x, '%Y-%m-%d'))
daily_positive_series = covid_data_df['Daily New']


def loss_func(p):
    assert len(p) == 11
    infect_p, transport_infect_p, leisure_p, \
    p_latent_2infectious, p_infectious_2severe, p_severe_2dead, \
    leisure_p_constraint, sickbed_buff, \
    severe_dur, infectious_dur, origin_infected_num = p
    print(p)
    abm = ABMPandemic(begin_date=begin_date,
                      end_date=end_date,
                      agents_df=agents_df,
                      space_df=space_df,
                      policy_df=policy_df,
                      holiday_df=holiday_df,
                      daily_positive_series=daily_positive_series,

                      infect_p=infect_p,
                      transport_infect_p=transport_infect_p,
                      leisure_p=leisure_p,
                      p_latent_2infectious=p_latent_2infectious,
                      p_infectious_2severe=p_infectious_2severe,
                      p_severe_2dead=p_severe_2dead,
                      leisure_p_constraint=leisure_p_constraint,
                      sickbed_buff=sickbed_buff,

                      severe_dur=int(severe_dur),
                      infectious_dur=int(infectious_dur),
                      origin_infected_num=int(origin_infected_num))
    train_value=list(abm.run())
    real_value=covid_data_df.loc[begin_date:end_date,'Daily Death']
    if (residual_num := len(real_value) - len(train_value)) > 0:
        train_value.extend([0] * residual_num)

    return mse(train_value, real_value)


ga = GA(func=loss_func,
        n_dim=11,
        size_pop=50,
        max_iter=800,
        prob_mut=0.001,
        lb=[0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1],
        ub=[0.3, 0.3, 0.001, 0.9, 0.9, 0.9, 0.001, 1, 30, 30, 30],
        precision=[1e-4, 1e-4, 1e-4, 1e-4, 1e-4, 1e-4, 1e-4, 1e-4, 1, 1, 1],
        constraint_ueq=[lambda p: p[2] - p[6]])
best_x, best_y = ga.run()
print('best_x:', best_x, '\n', 'best_y:', best_y)
