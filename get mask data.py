from datetime import datetime
import pandas as pd
from abm.abmpandemic import ABMPandemic
from sklearn.metrics import mean_squared_error as mse
import os

proj_path = os.path.abspath('.')
p = [0.30177623145943966, 0.024417043096081066, 0.08680351906158358, 0.2559760712977659, 0.0780734952997192,
     0.10695843252151621, 0.04320625610948192, 0.43910389451837384, 40.0, 91.0, 200.0]

begin_date = '2020-02-22'
end_date = '2020-05-31'
agents_df = pd.read_csv(proj_path + r"\data\agents.csv",
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
space_df = pd.read_csv(proj_path + r"\data\business point.csv",
                       index_col=0,
                       dtype={'type': int,
                              'acreage': float},
                       converters={
                           # 'susceptible_inside': eval,
                           # 'infector_inside': eval,
                           'staffs_idx': eval})

policy_df = pd.read_excel(
    proj_path + r"\data\policy constraint.xlsx",
    sheet_name=0,
    index_col='date',
    date_parser=lambda x: pd.datetime.strptime(x, '%Y-%m-%d'))
holiday_df = pd.read_csv(proj_path + r"\data\holiday.csv",
                         index_col='date',
                         date_parser=lambda x: datetime.strptime(x, '%Y/%m/%d'))
covid_data_df = pd.read_excel(
    proj_path + r"\data\covid data torino province.xlsx",
    sheet_name=0,
    index_col='Date',
    date_parser=lambda x: datetime.strptime(x, '%Y-%m-%d'))
daily_positive_series = covid_data_df['Daily New']

infect_p, transport_infect_p, leisure_p, \
p_latent_2infectious, p_infectious_2severe, p_severe_2dead, \
leisure_p_constraint, sickbed_buff, \
severe_dur, infectious_dur, origin_infected_num = p
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

result_df, _ = abm.run()
result_df.to_csv(proj_path + r"/data/result/mask/mask13.csv", index=False)
train_value = list(result_df['dead'])
real_value = covid_data_df.loc[begin_date:end_date, 'Total Death']
for v1, v2 in zip(train_value, real_value):
    print(v1, v2)
if (residual_num := len(real_value) - len(train_value)) > 0:
    train_value.extend([0] * residual_num)
else:
    train_value = train_value[:len(real_value)]
error = mse(train_value, real_value)
print(error)
