from matplotlib import pyplot as plt
import pandas as pd
from datetime import datetime

begin_date='2020-02-22'
end_date = '2020-05-31'
pred_df = pd.read_csv("../data/result/abm result.csv",
                      index_col='date',
                      date_parser=lambda x: datetime.strptime(x, '%Y-%m-%d'))
real_df=pd.read_excel(r"../data\covid data torino province.xlsx",
                      sheet_name=0,
                      index_col='Date',
                      date_parser=lambda x: datetime.strptime(x, '%Y-%m-%d'))

pred_dead=pred_df.loc[begin_date:end_date,'dead']
real_dead=real_df.loc[begin_date: end_date,'Total Death']

plt.figure()
plt.plot(pred_dead, label='predict')
plt.plot(real_dead, label='real')
x_ticks=[pred_df.index[i] for i in range(len(pred_df)) if i%30==0]
plt.xticks(x_ticks, [x.strftime("%m-%d") for x in x_ticks], rotation=45)
plt.legend()
plt.title("Mortality at the beginning of COVID-19")
plt.xlabel("Date")
plt.ylabel("Mortality")
plt.show()

# plt.figure()
# plt.plot

