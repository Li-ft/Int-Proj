import os
import pandas as pd
from datetime import datetime
from matplotlib import pyplot as plt


proj_path=os.path.abspath(r'../..')
baseline_df=pd.read_csv(proj_path + r"/data/result/abm result.csv",
                          index_col='date',
                          date_parser=lambda x: datetime.strptime(x, '%Y-%m-%d'))

figure=plt.figure()

for i in range(4):
    data_path=proj_path+r'/data/result/online working/'+f'online{i}.csv'
    data_df=pd.read_csv(data_path,
                        index_col='date',
                        date_parser=lambda x: datetime.strptime(x, '%Y-%m-%d'))
    plt.plot(data_df['dead'], label=f'{(i+1)*20}% from 31, March')
for i in range(4):
    data_path=proj_path+r'/data/result/online working/'+f'online late{i}.csv'
    data_df=pd.read_csv(data_path,
                        index_col='date',
                        date_parser=lambda x: datetime.strptime(x, '%Y-%m-%d'))
    plt.plot(data_df['dead'], label=f'{(i+1)*20}% from 30, April')
plt.plot(baseline_df['dead'],label='baseline')
plt.legend()
plt.xlabel('Date')
plt.ylabel('Mortality')
plt.title("Mortality on Different Online Working Rate and Start Time")
x_ticks=[baseline_df.index[i] for i in range(len(baseline_df)) if (i + 2) % 7 == 0]
plt.xticks(x_ticks, [x.strftime("%m-%d") for x in x_ticks], rotation=45)
plt.tight_layout()
plt.savefig("online work.png",dpi=600)
plt.show()
