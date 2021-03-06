from datetime import datetime
import pandas as pd
from abm.abmpandemic import ABMPandemic
from sko.GA import GA
from sklearn.metrics import mean_squared_error as mse
from logs.config import log_config
from sko.tools import set_run_mode
import os

proj_path=os.path.abspath('.')
log = log_config('result', proj_path+r'/logs/result.txt')

begin_date = '2020-02-22'
end_date = '2020-05-31'
agents_df = pd.read_csv(proj_path+r"/data/agents.csv",
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
space_df = pd.read_csv(proj_path+r"/data/business point.csv",
                       index_col=0,
                       dtype={'type': int,
                              'acreage': float},
                       converters={
                           # 'susceptible_inside': eval,
                           # 'infector_inside': eval,
                           'staffs_idx': eval})

policy_df = pd.read_excel(
    proj_path+r"/data/policy constraint.xlsx",
    sheet_name=0,
    index_col='date',
    date_parser=lambda x: pd.datetime.strptime(x, '%Y-%m-%d'))
holiday_df = pd.read_csv(proj_path+r"/data/holiday.csv",
                         index_col='date',
                         date_parser=lambda x: datetime.strptime(x, '%Y/%m/%d'))
covid_data_df = pd.read_excel(
    proj_path+r"/data/covid data torino province.xlsx",
    sheet_name=0,
    index_col='Date',
    date_parser=lambda x: datetime.strptime(x, '%Y-%m-%d'))
daily_positive_series = covid_data_df['Daily New']


def loss_func(p):
    assert len(p) == 11
    infect_p, transport_infect_p, leisure_p, \
    p_latent_2infectious, p_infectious_2severe, p_severe_2dead, \
    leisure_p_constraint, sickbed_buff, \
    severe_dur, infectious_dur, origin_infected_num = p
    print(list(p))
    if leisure_p < leisure_p_constraint:
        return 999999999
    # log.info(f'params:\n {list(p)}')
    agents_df_copy = agents_df.copy()
    space_df_copy = space_df.copy()
    abm = ABMPandemic(begin_date=begin_date,
                      end_date=end_date,
                      agents_df=agents_df_copy,
                      space_df=space_df_copy,
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
    result, _ = abm.run()
    train_value = list(result['dead'])
    real_value = covid_data_df.loc[begin_date:end_date, 'Total Death']
    if (residual_num := len(real_value) - len(train_value)) > 0:
        train_value.extend([0] * residual_num)
    else:
        train_value = train_value[:len(real_value)]

    error = mse(train_value, real_value)
    log.info(f'params:\n {list(p)}')
    log.info(f'error:\n {error}')
    return error


set_run_mode(loss_func, 'multiprocessing')
constraint_ueq = lambda p: p[6] - p[2]
ga = GA(func=loss_func,
        n_dim=11,
        size_pop=50,
        max_iter=100,
        prob_mut=0.05,
        lb=[0, 0, 0, 0.1, 0, 0, 0, 0.1, 24, 24, 1],
        ub=[1, 0.5, 0.1, 0.9, 0.5, 0.9, 0.1, 0.9, 240, 240, 200],
        precision=[1e-4, 1e-4, 1e-4, 1e-4, 1e-4, 1e-4, 1e-4, 1e-4, 1, 1, 1],
        constraint_eq=[constraint_ueq])
best_param, best_loss = ga.run()
log.info(f'best param of epoch: {best_param}')
log.info(f'best loss of epoch: {best_loss}\n\n')

# best_result_log.info(f'param: {best_param} \n loss: {best_loss}')
