from matplotlib import pyplot as plt
import pandas as pd
from datetime import datetime
import os
import numpy as np

proj_path=os.path.abspath(r'../..')
begin_date='2020-02-22'
end_date = '2020-05-31'

baseline_df=pd.read_csv(proj_path + r"/data/result/abm result.csv",
                          index_col='date',
                          date_parser=lambda x: datetime.strptime(x, '%Y-%m-%d'))

for i in range(3,5):
    data_path=proj_path+r'/data/result/sickbed/'+f'{i}.csv'
    data_df=pd.read_csv(data_path,
                        index_col='date',
                        date_parser=lambda x: datetime.strptime(x, '%Y-%m-%d'))
    plt.plot(data_df['dead'],label=f'{i}')
plt.legend()
plt.xlabel('Date')
plt.ylabel('Mortality')
plt.title('Mortality on Different Sickbed Number')
x_ticks=[baseline_df.index[i] for i in range(len(baseline_df)) if (i + 2) % 7 == 0]
plt.xticks(x_ticks, [x.strftime("%m-%d") for x in x_ticks], rotation=45)
plt.tight_layout()
plt.savefig("sickbed.png", dpi=600)
plt.show()