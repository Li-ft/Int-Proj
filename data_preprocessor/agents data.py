import json
import pandas as pd
import numpy as np
from utils import *

# %%
unemployment_rate = 0.102
# worker_in_office_rate = 0.33
retire_age = 67
# inf_coeff = 0.1  # todo: use genetic algorithm to decide this parameter


household_df = pd.read_json('../data/household distribution revised.geojson')
age_df = pd.read_csv('../data/age distribution revised.csv')

agents_df = ini_agents_states(household_df, unemployment_rate, retire_age, age_df)

# agents_df['index'] = agents_df.index
# agents_df.to_csv('../data/agents.csv', index=False)
agents_df.to_csv('../data/agents.csv')