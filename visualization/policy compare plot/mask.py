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

mortality_changes=[]
for i in range(14):
    pred_df_path=proj_path+r'/data/result/mask/'+f'mask{i}.csv'
    pred_df=pd.read_csv(pred_df_path,
                        index_col='date',
                        date_parser=lambda x: datetime.strptime(x, '%Y-%m-%d'))

    mortality_changes.append(baseline_df['dead'][-1] - pred_df['dead'][-1])



# pred_dead=pred_df.loc[begin_date:end_date,'dead']
baseline_dead= baseline_df.loc[begin_date: end_date, 'dead']

plt.figure()
# plt.plot(pred_dead, label='predict')
plt.plot(baseline_dead, label='baseline mortality')
# for mortality in mortality_changes:
plt.bar([baseline_df.index[i] for i in range(len(baseline_df)) if (i + 2) % 7 == 0],
        mortality_changes,
        color='green',
        label='people saved',
        width=2)
x_ticks=[baseline_df.index[i] for i in range(len(baseline_df)) if (i + 2) % 7 == 0]
plt.xticks(x_ticks, [x.strftime("%m-%d") for x in x_ticks], rotation=45)
plt.legend()
plt.title("Different Start Time for Mandatory Mask")
plt.xlabel("Date")
plt.ylabel("Mortality")
plt.tight_layout()
plt.savefig("mask.png",dpi=600)
plt.show()


# plt.figure()
# plt.plot

