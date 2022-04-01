import json
from data_preprocessor_utils import *
import time

# pt: public transportation

RANGE = 5000
worker_outdoor_num = 10000
company_staff_num_upper = 100
company_staff_num_lower = 5
PT_rate = 0.34
student_num_per_room = 25

with open("../data/bussiness point.geojson", 'r') as f:
    data_json = json.load(f)

# type of the business point
# -1: unknown type
# 0: auto machine, without direct contact, won't be included in this simulation
# 1: eatery, in which people will take off the mask and stay for a relatively long time
# 2: shops where sell necessities, eg: supermarket, pharmacy
# 3: special shops, where people will infrequently access but not necessary, eg: clothing and book stores
# 4: shops that people will access infrequently, eg: jewelry shop and barber shop
business_type_dict = {
    'Negozio con apparecchi automatici': 0,

    'Gastronomia': 1,
    'Cialde caffè': 1,
    'Salumeria': 1,
    'Pizza al taglio': 1,
    'Spaccio alimentare e non alimentare': 1,
    'Alimentari': 1,
    'Alimenti biologici': 1,
    'Alimenti per animali': 1,
    'Extralimentari': 1,

    'Supermercato': 2,
    'Tabacchi': 2,
    'Carburanti': 2,
    'Casalinghi - Igiene casa e persona': 2,
    'Farmacia': 2,
    'Parafarmacia': 2,
    'Frutta e verdura': 2,
    'Latteria': 2,
    'Macelleria': 2,
    'Non alimentari generici': 2,
    'Ipermercato': 2,
    'Minimercato': 2,

    'Pasticceria': 3,
    'Panetteria': 3,
    'Alimentari annessi ad altra attività': 3,
    'Panificio': 3,
    'Drogheria': 3,
    'Pescheria': 3,
    'Sexy shop': 3,
    'Macelleria equina': 3,
    'Vendita non esclusiva di giornali': 3,
    'Intimo': 3,
    'Cosmetici': 3,
    'Enoteca': 3,
    'Giocattoli': 3,
    'Erboristeria': 3,
    'Articoli sportivi': 3,
    'Librerie': 3,
    'Calzature': 3,
    'Non alimentari annessi ad altre attività': 3,
    'Articoli pr la casa': 3,
    'Bibite': 3,
    'Quotidiani e periodici': 3,
    'Vendita al dettaglio di cose antiche ed usate': 3,
    'Abbigliamento': 3,
    'Nessuna': 3,
    'Cartolerie': 3,
    'Periodici': 3,
    'Quotidiani': 3,
    'Prodotti accessori a quotidiani e periodici': 3,
    'Quotidiani e periodici in struttura Serv Pubbl': 3,

    'Oggetti preziosi': 4,
    'Bigiotteria': 4,
    'Telefonia': 4,
    'Elettronica': 4,
    'Numismatica e filatelia': 4,
    'Ricambi elettrodomestici': 4,
    'Strumenti musicali': 4,
    'Tappeti': 4,
    'Pelletteria': 4,
    'Accessori abbigliamento': 4,
    'Edilizia/Sanitari': 4,
    'Biciclette': 4,
    "Opere d'arte": 4,
    'Fotografia': 4,
    'Colorificio': 4,
    'Tessuti': 4,
    'Oggettistica': 4,
    'Phone center': 4,
    'Serramenti': 4,
    'Audiovisivi': 4,
    "Complementi d'arredo": 4,
    'Informatica': 4,
    'Pastigliaggi': 4,
    'Articoli per animali': 4,
    'Ricambi auto e accessori': 4,
    'Ottica': 4,
    'Fiori e piante': 4,
    'Acconciatore/Estetista': 4,
    'Mobili': 4,
    'Profumeria': 4,
    'Autoveicoli e motoveicoli': 4,
    'Commercio equo e solidale': 4,
}

restricted_biz_pt = {'Gastronomia': 1,
                     'Cialde caffè': 1,
                     'Salumeria': 1,
                     'Pizza al taglio': 1,
                     'Spaccio alimentare e non alimentare': 1,
                     'Alimentari': 1,
                     'Alimenti biologici': 1,
                     'Alimenti per animali': 1,
                     'Extralimentari': 1,
                     'Casalinghi - Igiene casa e persona': 1,
                     'Pasticceria': 1,
                     'Panetteria': 1,
                     'Alimentari annessi ad altra attività': 1,
                     'Panificio': 1,
                     'Cartolerie': 1,
                     'Periodici': 1,
                     'Quotidiani': 1,
                     'Prodotti accessori a quotidiani e periodici': 1,
                     'Quotidiani e periodici in struttura Serv Pubbl': 1,
                     'Negozio con apparecchi automatici': -1,
                     }

# transfer the data format from json to dataframe
# use native list to add the rows instead of directing adding the df, to speeding up
data_list = []
for point in data_json['features']:
    point['properties']['home_x'], point['properties']['home_y'] = point['geometry']['coordinates']
    point['properties']['desc_categoria_merceologica'] = restricted_biz_pt.get(
        point['properties']['desc_categoria_merceologica'], 0)
    data_list.append(point['properties'])

# rename the column
business_point_df = pd.DataFrame(data_list)
business_point_df.rename(columns={'desc_categoria_merceologica': 'type'}, inplace=True)

# remove the business point without the acreage
business_point_df.drop(business_point_df[(business_point_df['mq_tot_vendita'].isnull()) & (
    business_point_df['mq_tot_locale'].isnull())].index, inplace=True)

# remove the business points which are the auto machine
business_point_df.drop(business_point_df.query("type==-1 | mq_tot_locale == '0' | mq_tot_vendita == '0'").index,
                       inplace=True)

# use business acreage to decide the number of staff in a business point, if the business acerage is none
# then choose half of the total acreage
print(business_point_df.columns)
business_point_df['acreage'] = business_point_df.apply(
    lambda row: choose_acerage(row['mq_tot_vendita'], row['mq_tot_locale']), axis=1)
business_point_df['staff_num'] = business_point_df.apply(lambda row: decide_staff_num(row['acreage']), axis=1)

# %%
agents_df = pd.read_csv("../data/agents.csv")
agents_df["employer"] = None

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% process the agent identity %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# identity = -1 is all the worker under assignment to the following job index
# 2: indoor worker (business point)
# 3: indoor worker (company)
# 4: outdoor workers

agents_df.rename(columns={'coord_x': 'home_x', 'coord_y': 'home_y'}, inplace=True)
labors_df = (agents_df.query('identity==-1'))[['home_x', 'home_y']]

# assertion: the total number of staffs can not exceed the number of labors in Torino
print(f'total number of staff of business point in Torino is {business_point_df["staff_num"].sum()}')
print(f'difference between business point staff num and total labor is '
      f'{labors_df.shape[0] - business_point_df["staff_num"].sum()}')

# make sure that the staff num of business point is less than the total num of labors in Torino
assert business_point_df["staff_num"].sum() <= len(labors_df)

# assert that the index is not redone
assert len(labors_df) != labors_df.index[-1]

# initial the staff and the people inside the business point
business_point_df['staffs_idx'] = None
business_point_df['people_inside'] = None

start = time.time()
# for each business point, find its potential staffs, based on people's living address
for biz_idx, row in business_point_df.iterrows():
    candidate_agents_df = labors_df.query(
        f"{row['home_x'] - RANGE} <= home_x <= {row['home_x'] + RANGE} & {row['home_y'] - RANGE} <= home_y <= {row['home_y'] + RANGE}")
    staffs_idx = list(candidate_agents_df.sample(row['staff_num'], replace=False).index)

    agents_df.loc[staffs_idx, 'employer'] = biz_idx
    agents_df.loc[staffs_idx, 'identity'] = 2  # 2 means indoor workers

    # remove people with jobs
    labors_df.drop(staffs_idx, axis='rows', inplace=True)

    # store the staffs' indexes into the business point database
    row['staffs_idx'] = staffs_idx
    business_point_df.loc[biz_idx] = row

print(f'it takes {time.time() - start}s')

staffs_idx = []
acreage_lst = []
# employer_idx =[]
if len(labors_df) > 0:
    if len(labors_df) >= worker_outdoor_num:
        workers_outdoor_idx = labors_df.sample(worker_outdoor_num).index
        agents_df.loc[workers_outdoor_idx, 'identity'] = 4  # 4 means outdoor workers
        # remove people with jobs
        labors_df.drop(workers_outdoor_idx, inplace=True)
    else:
        workers_outdoor_idx = labors_df.index
        agents_df.loc[workers_outdoor_idx, 'identity'] = 4  # 4 means outdoor workers
# if there are still some labors,
# then assign them all to the company (containing the university students)
if len(labors_df) > 0:
    total_company_staff_num = len(labors_df)
    company_staffs_idx = np.array(labors_df.index)
    np.random.shuffle(company_staffs_idx)
    company_staff_num_range = range(company_staff_num_lower, company_staff_num_upper)

    # the rest the labor will all work in a company
    while True:
        # get a random staff num of a company
        staff_num = np.random.choice(company_staff_num_range)

        if staff_num > len(company_staffs_idx):
            staffs_idx.append(list(company_staffs_idx))
            acreage_lst.append(len(company_staffs_idx) * 2)
            break
        else:
            staffs_idx.append(list(company_staffs_idx[:staff_num]))
            acreage_lst.append(staff_num * 2)
            # employer_idx.append()
            company_staffs_idx = np.delete(company_staffs_idx, range(staff_num))
    agents_df.loc[agents_df['identity'] == -1, 'identity'] = 3

# remove useless columns
biz_pt_useful_cols = [
                      # 'susceptible_inside',
                      # 'infector_inside',
                      'staffs_idx',
                      'type',
                      'acreage']
# make a empty list inside cells of the two columns
# business_point_df = reset_col_2empty_list(business_point_df, 'susceptible_inside', 'infector_inside')
business_point_df = business_point_df[biz_pt_useful_cols]

# company df contains the company staffs and university students
company_df = pd.DataFrame(columns=biz_pt_useful_cols)
company_df['staffs_idx'] = staffs_idx
company_df['type'] = 9
# company_df = reset_col_2empty_list(company_df, 'susceptible_inside', 'infector_inside')
company_df['acreage'] = acreage_lst
company_df.index = range(len(business_point_df), len(business_point_df) + len(company_df))
for company_idx, staff_idx in company_df['staffs_idx'].items():
    agents_df.at[staff_idx, 'employer'] = company_idx
business_point_df = business_point_df.append(company_df)

school_df = pd.DataFrame(columns=biz_pt_useful_cols)
student_idx = list(agents_df.query('identity==1').index)
student_idx_distribute = [student_idx[i:i + student_num_per_room] for i in
                          range(0, len(student_idx), student_num_per_room)]
school_df['staffs_idx'] = student_idx_distribute
school_df['type'] = 8
# school_df = reset_col_2empty_list(school_df, 'susceptible_inside', 'infector_inside')
school_df['acreage'] = 50
school_df.index = range(len(business_point_df), len(business_point_df) + len(school_df))
for school_idx, student_idx in school_df['staffs_idx'].items():
    agents_df.at[student_idx, 'employer'] = school_idx
business_point_df = business_point_df.append(school_df)

agents_df_useful_cols = ['home_x',
                         'home_y',
                         'family_idx',
                         # 'covid_state',
                         'age',
                         'identity',
                         'employer',
                         # 'position_index',
                         # 'leisure_timer',
                         # 'covid_state_timer',
                         'use_pt',
                         # 'is_positive',  # maybe unnecessary
                         'quarantine',
                         'infect_buff'
                         ]
# agents_df['leisure_timer'] = -1
# agents_df['covid_state_timer'] = None
agents_df['use_pt'] = np.random.choice([1, 0],
                                       len(agents_df),
                                       p=[PT_rate, 1 - PT_rate])

# agents_df['is_positive'] = 0
# agents_df['quarantine'] = 0
agents_df['infect_buff']=1
agents_df.loc[pd.isna(agents_df['employer']),'employer']=-1
agents_df = agents_df[agents_df_useful_cols]
assert len(agents_df.query('identity==-1')) == 0
# print(business_point_df)
business_point_df.to_csv('../data/business point.csv')
agents_df.to_csv('../data/agents.csv')
