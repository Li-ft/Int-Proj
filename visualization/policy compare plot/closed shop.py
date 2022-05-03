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

no_close_shop_df=pd.read_csv(proj_path + r'/data/result/closed shop/0.csv',
                             index_col='date',
                             date_parser=lambda x: datetime.strptime(x, '%Y-%m-%d'))

plt.figure()
plt.plot(no_close_shop_df['dead'],label='no constraint on shops')
plt.plot(baseline_df['dead'], label='baseline')
plt.fill_between(baseline_df.index,
                 no_close_shop_df['dead'],
                 baseline_df['dead'],
                 facecolor='red',
                 alpha=0.1)
plt.legend()
plt.xlabel('date')
plt.ylabel('mortality')
plt.title('Mortality comparison with no constraint on shops')
x_ticks=[baseline_df.index[i] for i in range(len(baseline_df)) if (i + 2) % 7 == 0]
plt.xticks(x_ticks, [x.strftime("%m-%d") for x in x_ticks], rotation=45)
plt.tight_layout()
plt.savefig("close shop.png",dpi=600)
plt.show()
