from datetime import datetime
import pandas as pd
from abm.abmpandemic import ABMPandemic
from sklearn.metrics import mean_squared_error as mse


# p=[0.17831502 ,0.05362637, 0.05929412, 0.23462736, 0.35295733, 0.11124336,
#  0.04258824, 0.42601636, 90, 60, 30]
# p=[0.3318073612891412, 0.4995727017458186, 0.09296187683284457, 0.13203516054205836, 0.0804541570015871, 0.24242812671671854, 0.04447702834799609, 0.7659992674887072, 33.0, 206.0, 75.0]
# p=[0.2915216993224684, 0.389757050421194, 0.0852394916911046, 0.15537785374191188, 0.0572579660603101, 0.32268815235304893, 0.043010752688172046, 0.22774996947869613, 38.0, 207.0, 79.0]
# p=[0.3697735457486419, 0.04688072274447565, 0.06871945259042032, 0.13174215602490538, 0.06519350506653644, 0.3475737044497345, 0.05591397849462365, 0.8814430472469784, 96.0, 215.0, 158.0]
# [0.2942074101202466, 0.07831766573068001, 0.07067448680351907, 0.18116225125137347, 0.05231351483335368, 0.24270280168467318, 0.05552297165200391, 0.6742888536198266, 73.0, 190.0, 49.0]
# p=[0.1515216993224684, 0.20055060432181665, 0.0852394916911046, 0.15537785374191188, 0.1572579660603101, 0.3203259476286395, 0.056989247311827966, 0.22774996947869613, 38.0, 200.0, 79.0]
# [0.29048403833241776, 0.3889024539128312, 0.07663734115347019, 0.1687583933585643, 0.05206934440239287, 0.24297747665262773, 0.05630498533724341, 0.6709681357587596, 41.0, 209.0, 47.0]
# p=[0.30177623145943966, 0.024417043096081066, 0.08680351906158358, 0.2559760712977659, 0.0780734952997192, 0.10695843252151621, 0.04320625610948192, 0.43910389451837384, 40.0, 91.0, 200.0]
# p=[0.30177623145943966, 0.024417043096081066, 0.08680351906158358, 0.24396288609449396, 0.0780734952997192, 0.10695843252151621, 0.04115347018572826, 0.4640092784763765, 40.0, 92.0, 200.0]
p=[0.30177623145943966, 0.024417043096081066, 0.08680351906158358, 0.2559760712977659, 0.0780734952997192, 0.10695843252151621, 0.04320625610948192, 0.43910389451837384, 40.0, 91.0, 200.0]





begin_date = '2020-02-22'
end_date = '2020-05-31'
agents_df = pd.read_csv(r"data\agents.csv",
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
space_df = pd.read_csv(r"data\business point.csv",
                       index_col=0,
                       dtype={'type': int,
                              'acreage': float},
                       converters={
                           # 'susceptible_inside': eval,
                           # 'infector_inside': eval,
                           'staffs_idx': eval})

policy_df = pd.read_excel(
    r"data\policy constraint.xlsx",
    sheet_name=0,
    index_col='date',
    date_parser=lambda x: pd.datetime.strptime(x, '%Y-%m-%d'))
holiday_df = pd.read_csv(r"data\holiday.csv",
                         index_col='date',
                         date_parser=lambda x: datetime.strptime(x, '%Y/%m/%d'))
covid_data_df = pd.read_excel(
    r"data\covid data torino province.xlsx",
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

result, infect_map_df=abm.run()
result.to_csv('data/result/abm result.csv')
infect_map_df.to_csv('data/result/infect map.csv')
train_value = list(result['dead'])
real_value = covid_data_df.loc[begin_date:end_date, 'Total Death']
for v1,v2 in zip(train_value,real_value):
    print(v1,v2)
if (residual_num := len(real_value) - len(train_value)) > 0:
    train_value.extend([0] * residual_num)
else:
    train_value = train_value[:len(real_value)]
error=mse(train_value, real_value)
print(error)