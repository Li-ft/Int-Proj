import pandas as pd
import numpy as np
from itertools import chain
from typing import Iterable, Collection
import datetime
from logs.config import log_config

# tp: transport
# p: probability
log = log_config('abm', r'.\logs\log.txt')
mask_buff = 0.85
mandatory_mask_begin_date = '2020-05-18'
optional_mask_begin_date = '2020-06-02'
seed = 2019


class ABMPandemic:
    def __init__(self,
                 begin_date: str,
                 end_date: str,

                 agents_df: pd.DataFrame,
                 space_df: pd.DataFrame,
                 policy_df: pd.DataFrame,
                 holiday_df: pd.DataFrame,
                 daily_positive_series: pd.Series,

                 infect_p: float,
                 transport_infect_p: float,
                 leisure_p: float,
                 p_latent_2infectious: float,
                 p_infectious_2severe: float,
                 p_severe_2dead: float,
                 leisure_p_constraint: float,
                 sickbed_buff: float,

                 severe_dur: int,
                 infectious_dur: int,
                 # immune_dur: int,
                 # immune_infect_p: float,

                 origin_infected_num: int = 1,
                 step_per_hour: int = 1):
        # self.agents_df = agents_df
        self.begin_date = begin_date
        self.end_date = end_date
        assert len(agents_df) == 858052
        # self.infected_df = agents_df.sample(origin_infected_num)
        # assert max(list(agents_df.index)) == agents_df.index[-1]
        agents_df.loc[:, 'position_index'] = -1
        agents_df.loc[:, 'covid_state'] = 0
        agents_df.loc[:, 'leisure_timer'] = -1
        agents_df.loc[:, 'covid_state_timer'] = -1
        agents_df.loc[:, 'quarantine'] = 0
        agents_df.loc[:, 'space_acreage'] = 0
        agents_df[['position_index', 'covid_state', 'leisure_timer', 'covid_state_timer', 'quarantine']] = \
            agents_df[['position_index', 'covid_state', 'leisure_timer', 'covid_state_timer', 'quarantine']].astype(int)
        # agents_df['infect_buff'] = 1
        # assert len(agents_df.index) == len(set(agents_df.index))
        self.susceptible_df = agents_df
        self.infected_df = pd.DataFrame(columns=agents_df.columns)
        self.step_per_hour = step_per_hour
        self.step_per_day = step_per_hour * 24
        self.handle_new_infected(agents_df.sample(origin_infected_num, random_state=seed).index)

        # all_staff_idx = list(chain.from_iterable(space_df['staffs_idx']))
        # assert len(all_staff_idx) == len(set(all_staff_idx))
        self.space_df = space_df
        self.space_df['susceptible_inside'] = np.empty((len(self.space_df), 0)).tolist()
        self.space_df['infector_inside'] = np.empty((len(self.space_df), 0)).tolist()
        # self.leisure_points_df = space_df.query('type==3')
        # log.debug(f'{self.space_df.info()}')

        self.holiday_df = holiday_df
        self.infect_p = infect_p
        # self.drive_chance = ts_chances_df['drive']
        # self.metro_chance = ts_chances_df['metro']
        # self.bus_chance = ts_chances_df['bus']
        self.result_df = pd.DataFrame(columns=['date',
                                               'total cases',
                                               'positive cases',
                                               'infected',
                                               # 'recovered cases',
                                               'real recovered cases',
                                               'dead'])
        self.tp_infect_p = transport_infect_p
        self.leisure_p = leisure_p
        self.leisure_p_normal = leisure_p
        self.leisure_place = space_df.query('type >= 3')
        self.biz_pt_idx_with_infector = []

        self.p_latent_2infectious = p_latent_2infectious
        assert p_infectious_2severe <= 1
        self.p_infectious_2severe = p_infectious_2severe
        self.severe_2deceased = p_severe_2dead
        self.severe_dur = severe_dur
        # self.recovered_dur = recovered_dur
        self.infectious_dur = infectious_dur
        self.dead_df = pd.DataFrame(columns=self.infected_df.columns)
        # self.immune_dur = immune_dur
        # self.immune_infect_rate = immune_infect_p
        self.policy_df = policy_df
        self.space_type_limit = None
        self.limit_hour = None
        self.leisure_p_constraint = leisure_p_constraint
        self.daily_positive_series = daily_positive_series

        self.sickbed_num = int(len(agents_df) / 1000 * 3.16 / 5)
        self.sickbed_occupy_list = []

        self.dead_idx = []
        self.total_case_num = 0
        self.new_case = 0
        self.has_normal_bed = True
        self.has_severe_bed = True
        self.sickbed_buff = sickbed_buff * 0.2

        self.space_constraint_df = pd.DataFrame()
        self.recovery_df = pd.DataFrame()

        self.infect_proportion = 0
        self.date = pd.to_datetime(begin_date)
        self.step_count = 0

        self.not_work_workers_idx = []
        self.not_work_workers_identity = []

    def step(self, day_type: str, hour: int):
        # log.info(f'step: {self.step_count}, hour: {hour}')
        is_rest_time = False
        if day_type == 'workday':
            if hour < 8:
                is_rest_time = True
            if hour == 8:
                self.commute_infect(hour)
            if 9 <= hour < 13:
                self.work_learn()
                self.leisure(all_ppl=False)
            if hour == 13:
                self.leisure(all_ppl=False)
            if 14 <= hour < 18:
                self.work_learn()
                self.leisure(all_ppl=False)
            if hour == 18:
                self.commute_infect(hour)
                self.leisure(all_ppl=False)
            if 19 <= hour < 23:
                self.leisure()
            if hour == 23:
                is_rest_time = True
        if day_type == 'holiday':
            if 9 <= hour < 23:
                self.leisure()
            else:
                is_rest_time = True
        self.before_step_end(is_rest_time)

    def infection_balance(self):
        """calculate the statistical pandemic data for each day"""

        # total_case_num = self.agents_df
        positive_case_num = len(self.infected_df.query('quarantine==1'))
        infected_num = len(self.infected_df)
        # recovered_case_num = 0
        real_recovered_case_num = len(self.recovery_df)
        dead_num = len(self.dead_df)
        self.result_df = self.result_df.append({'date': self.date.strftime("%Y-%m-%d"),
                                                'total cases': self.total_case_num,
                                                'positive cases': positive_case_num,
                                                'infected': infected_num,
                                                # 'recovered cases': recovered_case_num,
                                                'real recovered cases': real_recovered_case_num,
                                                'dead': dead_num}, ignore_index=True)

    def run(self) -> tuple[pd.DataFrame, pd.DataFrame]:
        while True:
            log.info(self.date)
            daily_positive_num = self.daily_positive_series.loc[self.date]
            is_holiday = self.holiday_df.loc[self.date, 'is_holiday']
            if is_holiday:
                self.holiday(daily_positive_num)
            else:
                self.workday(daily_positive_num)
            # stopping condition
            if len(self.infected_df) == 0 or pd.to_datetime(self.date) == pd.to_datetime(self.end_date):
                break
            self.date = self.date + datetime.timedelta(1)
        log.info(f"dead data: {self.result_df['dead']}")

        return (self.result_df, self.recovery_df)

    def holiday(self, today_positive_num):
        for hour in range(24):
            step_count = 0
            while (step_count := step_count + 1) <= self.step_per_hour:
                self.policy_ctrl(self.date, hour)
                self.step('holiday', hour)
                # if the time slot in a day is larger than 24, then another loop can be added under this loop
                if 9 <= hour < 23:
                    self.leisure()
        self.end_of_day(today_positive_num)

    def workday(self, today_positive_num):
        for hour in range(24):
            step_count = 0
            while (step_count := step_count + 1) <= self.step_per_hour:
                self.policy_ctrl(self.date, hour)
                self.step('workday', hour)
        self.end_of_day(today_positive_num)

    def commute_infect(self, hour):
        # only the students, workers indoor will commute now
        # 0: walk or drive or ride to the working place
        # 1: use the public transport
        if hour == 18:
            log.debug('leave work/study place')
            susceptible_leave_idx = self.susceptible_df.query('1<=identity<4').index
            # log.debug(f'off work: {susceptible_leave_idx}')
            self.leave_space(susceptible_leave_idx)

        commute_people_df = self.susceptible_df.query('1<=identity<4 & use_pt==1')
        # commute_people_df = self.agents_df.loc[commute_people_idx]
        np.random.seed(seed)
        commute_people_df.loc[:, 'covid_state'] = np.random.choice([0, 1],
                                                                   len(commute_people_df),
                                                                   p=[1 - (self.tp_infect_p * self.infect_proportion),
                                                                      self.tp_infect_p * self.infect_proportion])
        new_infected_idx = commute_people_df.query('covid_state==1').index
        self.handle_new_infected(new_infected_idx)
        if hour == 8:
            log.debug('enter work/study place')
            susceptible_work_df = self.susceptible_df.query('1<=identity<4')

            self.enter_space(susceptible_work_df.index,
                             susceptible_work_df['employer'],
                             'susceptible_inside')

    def leisure(self, all_ppl: bool = True):
        leisure_space_df = self.space_df.query('type<8')
        if not all_ppl:
            # only people who are not in a leisure place already can choose a leisure place
            susceptible_can_leisure_df = self.susceptible_df.query('leisure_timer<1 & identity in [5,6]')
        else:
            susceptible_can_leisure_df = self.susceptible_df.query('leisure_timer<1')

        # susceptible_leisure_df = \
        self.assign_leisure_place(susceptible_can_leisure_df, leisure_space_df.index,
                                  'susceptible_inside')
        # update the "position_index" and the "leisure_timer"
        # self.susceptible_df.loc[susceptible_leisure_df.index] = susceptible_leisure_df

        # # we only care about the infected people who can infect others, ie: covid state 2
        # # for the severe symptom agents, they cannot go to the leisure place for physical reason
        # if not all_ppl:
        #     infected_people_can_leisure_df = self.infected_df.query('''quarantine==0
        #                                                              & covid_state==2
        #                                                              & leisure_timer<1
        #                                                              & identity in [4,5]''')
        # else:
        #     infected_people_can_leisure_df = self.infected_df.query('''quarantine==0
        #                                                              & covid_state==2
        #                                                              & leisure_timer<1''')
        #
        # infector_leisure_df = self.assign_leisure_place(infected_people_can_leisure_df, leisure_df.index,
        #                                                 'infector_inside')
        # self.infected_df.loc[infector_leisure_df.index] = infector_leisure_df

        # self.biz_pt_idx_with_infector.extend(infector_leisure_df['position_index'])

    def work_learn(self):
        # # get the infected students and the infected indoor workers
        # work_school_infected_df = self.infected_df.query('identity==1 | identity==3')
        # # collect the indoor spaces which have infector inside
        # self.biz_pt_idx_with_infector.extend(work_school_infected_df['employer'])
        #
        # # this infect p is the p of getting infected if there are average 1 infector for every 1 m2
        # infect_p = self.infect_p
        # # get the number of infectors inside the business point
        # biz_pt_with_infector_count = pd.value_counts(self.biz_pt_idx_with_infector)
        # # get all the exposed people's index and make a list
        # people_exposed_idx = list(
        #     chain.from_iterable(self.space_df.loc[biz_pt_with_infector_count.index, 'susceptible_inside']))
        #
        # #
        # # agents_df = pd.concat([self.susceptible_df, self.infected_df])
        # people_exposed_idx = set(people_exposed_idx).intersection(set(self.susceptible_df.index))
        # people_exposed_df = self.susceptible_df.loc[people_exposed_idx]
        #
        # infect_p_list = []
        # # use local variable to speed up the access
        # biz_pt_df_copy = self.space_df.copy()
        #
        # # # generate the infect rate for each exposed people
        # for biz_idx, infector_num in biz_pt_with_infector_count:
        #     # infect rate is linearly correlated with the number of infector inside the space
        #     p = infect_p * infector_num
        #     # p = 1 if p > 1 else p
        #     # p = 1 - (1 - p) ** 8
        #     # todo: here only the staff will be concerned
        #     infect_p_list.extend([p] * len(biz_pt_df_copy.at[biz_idx, 'staffs_idx']))
        #
        # assert len(infect_p_list) == len(people_exposed_df)
        #
        # # decide which agents is infected by the individually infected rate given by the code above
        # people_exposed_df['is_infected'] = np.random.binomial(1, infect_p_list, len(people_exposed_df))
        # new_infected_idx = people_exposed_df.query('is_infected==1').index
        # self.handle_new_infected(new_infected_idx)
        pass

    def end_of_day(self, today_positive_num):  # reset
        self.biz_pt_idx_with_infector = []
        self.space_df['susceptible_inside'] = np.empty((len(self.space_df), 0)).tolist()
        self.space_df['infector_inside'] = np.empty((len(self.space_df), 0)).tolist()
        self.susceptible_df['position_index'] = -1
        self.infected_df['position_index'] = -1
        self.infected_df['leisure_timer'] = 0
        self.susceptible_df['leisure_timer'] = 0

        # reset the policy control
        # self.space_df = pd.concat([self.space_df, self.space_constraint_df])
        # self.leisure_p = self.leisure_p_normal

        self.covid_test(today_positive_num)
        self.infection_balance()

        # self.restore_policy_ctrl()

    def before_step_end(self, is_rest_time: bool):
        self.covid_state_timer_decrease()
        if is_rest_time:
            pass
        else:
            self.leisure_time_decrease()
            self.infect()
            susceptible_num = len(self.susceptible_df)
            infected_num = len(self.infected_df)
            infectious_num = len(self.infected_df.query('covid_state>1 & quarantine==0'))
            recovery_num = len(self.recovery_df)
            self.infect_proportion = round(infectious_num / (infected_num + susceptible_num + recovery_num), 6)
            log.debug(f'infect proportion: {self.infect_proportion}')
            log.debug(f'total infected: {len(self.infected_df)}')
            log.debug(f'total recover: {len(self.recovery_df)}')

        self.step_count += 1

    def infect(self):
        # old code
        # get the number of infectors inside the leisure places
        # biz_pt_idx_count = pd.value_counts(self.biz_pt_idx_with_infector)
        # susceptible_exposed_idx = []
        # infects_p = []
        #
        # biz_pt_df_copy = self.space_df
        # # todo: make code concurrent here
        # for biz_pt_idx in biz_pt_idx_count.index:
        #     # get all the susceptible indexes inside the leisure places
        #     susceptible_idx = biz_pt_df_copy.at[biz_pt_idx, 'susceptible_inside']
        #     # infect chance is proportionate to the infector number in the space,
        #     # and it's also inversely proportional to the acreage of the space
        #
        #     # infect_p = round(biz_pt_idx_count[biz_pt_idx]/biz_pt_df_copy.at[biz_pt_idx, 'acreage']*self.infect_p, 4)
        #     infect_p = round(1 / biz_pt_df_copy.at[biz_pt_idx, 'acreage'] * self.infect_p, 4)
        #     susceptible_exposed_idx.extend(susceptible_idx)
        #     # make a list that contains all the exposed susceptible and their infect chance
        #     infects_p.extend([infect_p] * len(susceptible_idx))
        #
        # assert len(susceptible_exposed_idx) == len(infects_p)
        # df = pd.DataFrame()
        # df['infect_chance'] = infects_p
        # df.index = susceptible_exposed_idx
        # # randomly decide who will be infected
        # df['is_infected'] = np.random.binomial(1, df['infect_chance'], len(df))
        # new_infected_idx = df.query('is_infected == 1').index
        #
        # self.handle_new_infected(new_infected_idx)
        # old code ends
        # space_df_copy = self.space_df
        #
        # infects_p = []
        # infect_p = self.infect_p
        # infect_proportion = self.infect_proportion
        # for _, row in space_df_copy[['susceptible_inside', 'acreage']].iterrows():
        #     susceptible_lst, acreage = row
        #     if (num := len(susceptible_lst)) > 0:
        #         p = 1 if (a := round(1 / acreage * infect_p * infect_proportion, 6)) > 0 else a
        #         infects_p.extend([p] * num)
        #     else:
        #         continue
        #
        # all_ppl_inside = list(chain.from_iterable(space_df_copy['susceptible_inside']))
        # # print(len(all_ppl_inside))
        # exposed_idx = set(all_ppl_inside).intersection(set(self.susceptible_df.index))
        # # print(len(exposed_idx))
        #
        # # print(len(exposed_idx), len(infects_p))
        # # assert len(exposed_idx) == len(infects_p)
        #
        # df = pd.DataFrame()
        # df['infect_chance'] = infects_p
        # df.index = all_ppl_inside
        # df = df.loc[exposed_idx]
        # # df.index = exposed_idx
        # # randomly decide who will be infected
        # df.loc[:, 'is_infected'] = np.random.binomial(1, df['infect_chance'], len(df))
        #
        # new_infected_idx = df.query('is_infected == 1').index
        susceptible_df_copy = self.susceptible_df.copy()
        # col_len = len(susceptible_df_copy.columns)
        infect_p = self.infect_p
        infect_proportion = self.infect_proportion
        # get the exposed people's index
        exposed_idx = susceptible_df_copy.query('space_acreage>0').index
        # susceptible_df_copy.loc[susceptible_df_copy['space_acreage'] > 1, 'space_acreage'] = 1
        # compute the infect chance based on the average number of infected people on 1 m2 space
        susceptible_df_copy.loc[exposed_idx, 'infect_chance'] = infect_p * infect_proportion
        # decide if the exposed people are infected based on the infect chance
        np.random.seed(seed)
        susceptible_df_copy.loc[exposed_idx, 'is_infected'] = np.random.binomial(1, susceptible_df_copy.loc[
            exposed_idx, 'infect_chance'], len(exposed_idx))
        # get the new infected people's index
        new_infected_idx = susceptible_df_copy.query('is_infected == 1').index
        self.handle_new_infected(new_infected_idx)

    def covid_state_timer_decrease(self):
        infected_df_copy = self.infected_df.copy()
        infected_df_copy['covid_state_timer'] -= 1

        # latent
        latents_end_df = infected_df_copy.query('covid_state==1 & covid_state_timer==0')
        np.random.seed(seed)
        latents_end_df.loc[:, 'get_worse'] = np.random.binomial(1,
                                                                self.p_latent_2infectious * latents_end_df[
                                                                    'infect_buff'],
                                                                len(latents_end_df))
        # latent -> recovered
        recovered_idx = latents_end_df.query('get_worse==0').index
        # log.debug(f'{len(recovered_idx)} patients recovered from latent')
        if len(recovered_idx) > 0:
            self.recovery(recovered_idx)

        # latent -> infectious
        infected_df_copy.loc[latents_end_df.index, 'covid_state'] = 2
        infected_df_copy.loc[latents_end_df.index, 'covid_state_timer'] = self.infectious_dur

        # infectious
        infectious_end_df = infected_df_copy.query('covid_state==2 & covid_state_timer==0')
        np.random.seed(seed)
        infectious_end_df.loc[:, 'get_worse'] = np.random.binomial(1,
                                                                   self.p_infectious_2severe * infectious_end_df[
                                                                       'infect_buff'],
                                                                   len(infectious_end_df))
        # infectious -> recovered
        infectious_2recovered_idx = infectious_end_df.query('get_worse==0').index
        # log.debug(f'{len(infectious_2recovered_idx)} patients recovered from infectious')
        if len(infectious_2recovered_idx) > 0:
            self.recovery(infectious_2recovered_idx)
        # infected_df_copy.loc[infectious_2recovered_idx, 'covid_state'] = 5
        # infected_df_copy.loc[infectious_2recovered_idx, 'covid_state_timer'] = self.recovered_dur
        # infectious -> severe
        infectious_2severe_idx = infectious_end_df.query('get_worse==1').index
        infected_df_copy.loc[infectious_2severe_idx, 'covid_state'] = 3
        infected_df_copy.loc[infectious_2severe_idx, 'quarantine'] = 1
        self.leave_space(infectious_2severe_idx)
        self.assign_sickbed(list(infectious_2severe_idx))
        infected_df_copy.loc[infectious_2severe_idx, 'covid_state_timer'] = self.severe_dur

        # severe
        severe_end_df = infected_df_copy.query('covid_state==3 & covid_state_timer==0')
        np.random.seed(seed)
        severe_end_df.loc[:, 'get_worse'] = np.random.binomial(1,
                                                               self.severe_2deceased * severe_end_df['infect_buff'],
                                                               len(severe_end_df))
        # severe -> recovered
        severe_2recovered_idx = severe_end_df.query('get_worse==0').index
        log.debug(
            f'{len(recovered_idx), len(infectious_2recovered_idx), len(severe_2recovered_idx)} patients recovered')
        if len(severe_2recovered_idx) > 0:
            self.recovery(severe_2recovered_idx)
        # infected_df_copy.loc[severe_2recovered_idx, 'covid_state'] = 5
        # infected_df_copy.loc[severe_2recovered_idx, 'covid_state_timer'] = self.recovered_dur
        # severe -> deceased
        severe_2dead_df = severe_end_df.query('get_worse==1')
        # self.infected_agents_df.loc[severe_2deceased_indexes, 'covid_state'] = 4
        infected_df_copy.drop(severe_2dead_df.index, inplace=True)
        # self.dead_df.loc[severe_2dead_df.index] = severe_2dead_df
        self.dead_df = pd.concat([self.dead_df, severe_2dead_df])

        # # recovered
        # recovered_df = infected_df_copy.query('covid_state==5')
        # infected_df_copy.drop(recovered_df.index, inplace=True)
        # recovered_df['covid_state'] = 0
        # recovered_df['immune_infect_rate'] = self.immune_infect_rate
        # self.susceptible_df.loc[recovered_df.index] = recovered_df

        self.infected_df = infected_df_copy.loc[set(self.infected_df.index).intersection(set(infected_df_copy.index))]

    def leisure_time_decrease(self):
        """when a step ends, the leisure timer(time that agents will stay in current leisure place) decrease"""

        # # at the end of a step, the timer decrease
        # # infector_leisure_df = self.infected_df.query('timer > 0')
        # infected_df_copy = self.infected_df.copy()
        # infected_df_copy['leisure_timer'] = infected_df_copy['leisure_timer'] - 1
        #
        # # when a timer is 0, people will leave the business point
        # ppl_leave_biz_pt_df = infected_df_copy.query('leisure_timer == 0')
        # # remove people's index from the business point's indoor people's list
        # # the infector's presence is only stored in the "business_points_indexes_with_infector" and
        # # the infectors' 'position_index'
        # # for idx in ppl_leave_biz_pt_df['position_index']:
        # #     self.biz_pt_idx_with_infector.remove(idx)
        # self.leave_space(ppl_leave_biz_pt_df.index)
        # ppl_leave_biz_pt_df['position_index'] = None
        # infected_df_copy.loc[ppl_leave_biz_pt_df.index] = ppl_leave_biz_pt_df
        #
        # self.infected_df = infected_df_copy
        self.susceptible_df['leisure_timer'] -= 1
        susceptible_leave_idx = self.susceptible_df.query('leisure_timer==0').index
        self.leave_space(susceptible_leave_idx)

    def handle_new_infected(self, new_infected_agent_idx: Collection[int]):
        """define the infected parameters such as the time for the next stage"""
        log.debug(f'new infected: {len(new_infected_agent_idx)}')
        # assert len(new_infected_agent_idx) == len(set(new_infected_agent_idx))
        # print(f'new infected: {new_infected_agent_idx}')
        new_infected_df = self.susceptible_df.loc[new_infected_agent_idx]
        new_infected_df.loc[:, 'covid_state'] = 1
        # the transition time from latent to normal symptom is a gamma distribution
        np.random.seed(seed)
        new_infected_df.loc[:, 'covid_state_timer'] = np.random.gamma(3.8, 0.66, len(new_infected_df))
        new_infected_df.loc[:, 'covid_state_timer'] = new_infected_df['covid_state_timer'].apply(
            lambda x: int(x * self.step_per_day))
        # log.debug(f'新增感染前: {len(self.infected_df)}')
        self.infected_df = pd.concat([self.infected_df, new_infected_df])
        # log.debug(f'新增感染后: {len(self.infected_df)}')

        # delete the new infected people from the healthy dataset
        self.susceptible_df.drop(new_infected_agent_idx, inplace=True)

    # def add_2normal_bed(self, agent_idx):
    #     self.normal_sickbed_list = self.assign_sickbed(agent_idx, self.normal_sickbed_list, self.normal_sickbed_num)
    #     return 1
    #
    # def add_2severe_bed(self, agent_idx):
    #     self.severe_sickbed_list = self.assign_sickbed(agent_idx, self.severe_sickbed_list, self.severe_sickbed_num)
    #     return 1

    def assign_sickbed(self, agent_idx: Collection[int]):
        # assert len(agent_idx) == len(set(agent_idx))
        agent_idx = list(set(agent_idx).difference(set(self.sickbed_occupy_list)))
        # no action if the hospital is full
        if len(self.sickbed_occupy_list) == self.sickbed_num:
            return agent_idx
        # sent the infectors to the hospital if there are some empty beds
        elif len(self.sickbed_occupy_list) < self.sickbed_num:
            rest_sickbed_num = self.sickbed_num - len(self.sickbed_occupy_list)
            # if the bed is adequate for all the infectors today
            if len(agent_idx) <= rest_sickbed_num:
                # log.debug(f'assign sickbed: {agent_idx}')
                self.sickbed_occupy_list.extend(agent_idx)
                self.infected_df.loc[agent_idx, 'infect_buff'] *= self.sickbed_buff
                return []
            # send the infectors until the hospital is full
            else:
                people_sickbed_idx, people_no_sickbed_idx = agent_idx[:rest_sickbed_num], agent_idx[rest_sickbed_num:]
                # log.debug(f'assign sickbed: {people_sickbed_idx}')
                self.sickbed_occupy_list.extend(people_sickbed_idx)
                self.infected_df.loc[agent_idx, 'infect_buff'] *= self.sickbed_buff
                return people_no_sickbed_idx
        # if the num of beds exceed the beds we have, then raise an error
        else:
            raise RuntimeError('sickbed exceeded')

    def release_sickbed(self, agent_idx: Collection[int]):
        agent_idx_set = set(agent_idx)
        # assert len(agent_idx_set) == len(agent_idx)
        sickbed_occupy_set = set(self.sickbed_occupy_list)
        # assert len(sickbed_occupy_set) == len(self.sickbed_occupy_list)
        # log.debug(f'release sickbed: {agent_idx_set}')
        people_sickbed_idx = agent_idx_set.intersection(sickbed_occupy_set, set(self.infected_df.index))
        self.sickbed_occupy_list = list(sickbed_occupy_set.difference(agent_idx_set))
        self.infected_df.loc[people_sickbed_idx, 'infect_buff'] /= self.sickbed_buff

    def covid_test(self, test_positive_num: int):
        """only consider the positive cases, because the negative cases doesn't have any influence"""
        # if test_positive_num>len(self.infected_df):
        #     test_positive_num=len(self.infected_df)
        # log.info(f'{self.date} new positive {test_positive_num}')

        if test_positive_num > len(self.infected_df):
            test_positive_num = len(self.infected_df)
        tested_agents = self.infected_df['covid_state'].sample(test_positive_num, random_state=seed)
        positive_idx = tested_agents[tested_agents > 0].index
        normal_idx = tested_agents[tested_agents == 2].index
        # severe_idx = tested_agents[tested_agents == 3].index

        # store today's covid test result
        self.new_case = len(positive_idx)
        self.total_case_num += len(positive_idx)
        self.infected_df.loc[positive_idx, 'quarantine'] = 1

        # send the positive cases to the hospital
        # infectors who has severe symptom will go directly to the hospital
        # infectors who has normal symptom will get positive result and then are sent to the hospital
        # infectors who doesn't have any symptom will be quarantine and don't go to the hospital
        # self.assign_sickbed(severe_idx)
        self.assign_sickbed(list(normal_idx))
        # self.add_2normal_bed(normal_idx)
        # self.add_2severe_bed(severe_idx)

    def policy_ctrl(self, date, hour: int):
        if date == pd.to_datetime(mandatory_mask_begin_date) and hour == 0:
            self.mandatory_mask()
        if date == pd.to_datetime(optional_mask_begin_date) and hour == 0:
            self.optional_mask()

        """realize the influence of the policy"""
        cur_limit_hour = self.policy_df.loc[date, 'from']
        cur_limit_type = self.policy_df.loc[date, 'type']
        # log.warning(f'{cur_limit_type} {cur_limit_hour}')
        # log.warning(f'{self.space_type_limit} {self.limit_hour}')
        cur_limit_type = None if pd.isna(cur_limit_type) else cur_limit_type
        cur_limit_hour = None if pd.isna(cur_limit_hour) else cur_limit_hour
        last_limit_type = None if pd.isna(a := self.space_type_limit) else a
        last_limit_hour = None if pd.isna(a := self.limit_hour) else a
        if cur_limit_type == last_limit_type and cur_limit_hour == last_limit_hour:
            return
        else:
            self.space_type_limit = cur_limit_type
            self.limit_hour = cur_limit_hour
            self.restore_policy_ctrl()
        space_type_limit = cur_limit_type
        limit_hour = cur_limit_hour

        if not pd.isna(space_type_limit):

            if not pd.isna(limit_hour):
                if hour == limit_hour:
                    # get spaces with constraint
                    self.space_constraint_df = self.space_df.query(f'type=={space_type_limit}')
                    # when the constraint space is closed, all clients leave the space
                    ppl_leave_idx = list(chain.from_iterable(self.space_constraint_df['susceptible_inside']))
                    self.leave_space(ppl_leave_idx)
                    # remove them from the business point list
                    self.space_df.drop(self.space_constraint_df.index, inplace=True)
                    # the leisure desire of people will decrease accordingly
                    self.leisure_p = self.leisure_p_constraint
                    log.debug('leisure limited with hour')
            else:
                if hour == 0:
                    log.debug('leisure limited')
                    # get spaces with constraint
                    self.space_constraint_df = self.space_df.query(f'type=={space_type_limit}')

                    # when the constraint space is closed, all clients leave the space
                    ppl_leave_idx = list(chain.from_iterable(self.space_constraint_df['susceptible_inside']))
                    self.leave_space(ppl_leave_idx)
                    # remove them from the business point list
                    self.space_df.drop(self.space_constraint_df.index, inplace=True)
                    # the leisure desire of people will decrease accordingly
                    self.leisure_p = self.leisure_p_constraint

            if len(self.space_constraint_df) > 0:
                not_work_workers = set(chain.from_iterable(self.space_constraint_df['staffs_idx'])) \
                    .intersection(set(self.susceptible_df.index))
                self.not_work_workers_idx = not_work_workers
                self.not_work_workers_identity = self.susceptible_df.loc[not_work_workers, 'identity']
                self.susceptible_df.loc[not_work_workers, 'identity'] = 5

        # # restricted_type =
        # if hour == limit_hour:
        #     log.debug('leisure limited')
        #     space_type_limit = self.policy_df.loc[date, 'type']
        #     # the constraint business type should be a int
        #     if not pd.isna(space_type_limit):
        #         # get the restricted business points
        #         self.space_constraint_df = self.space_df.query(f'type=={space_type_limit}')
        #         ppl_leave_idx = list(chain.from_iterable(self.space_constraint_df['susceptible_inside']))
        #         self.leave_space(ppl_leave_idx)
        #         # remove them from the business point list
        #         self.space_df.drop(self.space_constraint_df.index, inplace=True)
        #         # the leisure desire of people will decrease accordingly
        #         self.leisure_p = self.leisure_p_constraint

    def assign_leisure_place(self,
                             people_can_leisure_df: pd.DataFrame,
                             leisure_space_idx: Iterable[int],
                             col_name: str):
        np.random.seed(seed)
        people_can_leisure_df.loc[:, 'if_leisure'] = np.random.choice([0, 1],
                                                                      len(people_can_leisure_df),
                                                                      p=[1 - self.leisure_p, self.leisure_p])
        # get people who decide to have leisure
        ppl_leisure_df = people_can_leisure_df.query('if_leisure == 1')
        # randomly choose the leisure place for each person who decided to take leisure
        np.random.seed(seed)
        biz_pt_with_susceptible_idx = np.random.choice(leisure_space_idx, len(ppl_leisure_df))

        self.enter_space(ppl_leisure_df.index, biz_pt_with_susceptible_idx, col_name)
        # set a time that the agent will leave the business point
        # ppl_leisure_df['leisure_timer'] = np.random.randint(low=1, high=3 * self.step_per_hour,
        #                                                        size=len(ppl_leisure_df))
        np.random.seed(seed)
        self.susceptible_df.loc[ppl_leisure_df.index, 'leisure_timer'] = np.random.randint(low=1,
                                                                                           high=3 * self.step_per_hour,
                                                                                           size=len(ppl_leisure_df))
        # ppl_leisure_df.drop(columns='if_leisure', inplace=True)
        # self.susceptible_df.loc[ppl_leisure_df.index] = ppl_leisure_df
        # return ppl_leisure_df

    def recovery(self, recovery_index: Collection[int]):
        recovery_df = self.infected_df.loc[recovery_index]

        self.infected_df.drop(recovery_index, inplace=True)

        recovery_df.loc[:, 'covid_state'] = 0
        recovery_df.loc[:, 'quarantine'] = 0
        self.release_sickbed(recovery_index)
        # the recovery people is no more a susceptible
        self.recovery_df = pd.concat([self.recovery_df, recovery_df])

    def infect_family(self):
        infector_family_idx = set(self.infected_df['family_idx'])
        new_infected_idx = self.susceptible_df.query(f'family_idx in {infector_family_idx}').idx
        self.handle_new_infected(new_infected_idx)

    def dead(self, dead_idx: Collection[int]):
        dead_df = self.infected_df.loc[dead_idx]
        self.infected_df.drop(dead_idx, inplace=True)

        # dead_df['covid_state'] = 4
        self.dead_df = pd.concat([self.dead_df, dead_df])
        self.release_sickbed(dead_idx)

    def restore_policy_ctrl(self):
        log.warning('restore policy control')
        self.leisure_p = self.leisure_p_normal
        # self.space_df = pd.concat([self.space_df, self.space_constraint_df])
        self.space_df = self.space_df.append(self.space_constraint_df)
        # self.space_df.loc[self.space_constraint_df.index]=self.space_constraint_df
        self.space_constraint_df = pd.DataFrame(columns=self.space_df.columns)

        if len(self.not_work_workers_idx) > 0 and len(self.not_work_workers_identity) > 0:
            df = pd.DataFrame()
            df['identity'] = self.not_work_workers_identity
            df.index = self.not_work_workers_idx
            susceptible_idx = set(df.index).intersection(set(self.susceptible_df.index))
            infected_idx = set(df.index).intersection(set(self.infected_df.index))
            # assert len(susceptible_idx) + len(infected_idx) == len(df)
            self.susceptible_df.loc[susceptible_idx, 'identity'] = df.loc[susceptible_idx, 'identity']
            self.infected_df.loc[infected_idx, 'identity'] = df.loc[infected_idx, 'identity']

    def leave_space(self, agent_idx: Collection[int]):
        # log.debug('leave space')
        # space_df_copy = self.space_df.copy()
        # susceptible_df_copy = self.susceptible_df.copy()

        susceptible_idx = set(self.susceptible_df.index).intersection(set(agent_idx))
        self.susceptible_df.loc[susceptible_idx, 'space_acreage'] = 0
        # infected_idx=set(self.infected_df.index).intersection(set(agent_idx))
        # leaving_series = self.susceptible_df.loc[susceptible_idx, 'position_index']
        # # print(leaving_series)
        #
        # for ppl_idx, space_idx in leaving_series.items():
        #     # log.debug(f'{ppl_idx} leave {space_idx}')
        #     if space_idx == -1:
        #         continue
        #     space_df_copy.at[space_idx, 'susceptible_inside'].remove(ppl_idx)
        # try:
        #     susceptible_df_copy.loc[leaving_series.index, 'position_index'] = -1
        # finally:
        #     pass
        #     # print(self.infected_df.index)
        # self.space_df = space_df_copy
        # self.susceptible_df = susceptible_df_copy

    def enter_space(self,
                    agent_idx: Collection[int],
                    space_idx: Collection[int],
                    col_name: str):
        # log.info('enter space')
        # assert len(agent_idx) == len(set(agent_idx))
        # assert len(agent_idx) == len(space_idx)

        df = pd.DataFrame()
        df.loc[:, 'space_idx'] = space_idx
        df.index = agent_idx

        susceptible_idx = set(agent_idx).intersection(set(self.susceptible_df.index))
        # agent_idx = df.loc[susceptible_idx, 'space_idx']

        # space_df_copy = self.space_df.copy()
        # for agent, space in df['space_idx'].items():
        #     # if type(space_df_copy.at[space, col_name]) is not list:
        #     #     log.error(type(space_df_copy.at[space, col_name]))
        #     #     log.error(space_df_copy.at[space, col_name])
        #     #     # log.error(space_df_copy[col_name].dtype)
        #     #     # space_df_copy[col_name]=space_df_copy[col_name].astype(object)
        #     #     print(space, col_name)
        #     #
        #     #     space_df_copy.at[28825, 'susceptible_inside']= [1,2,3]
        #     #     print(space_df_copy.at[28825, 'susceptible_inside'])
        #     #     space_df_copy.at[space, col_name]=space_df_copy.at[space, col_name].values.tolist()
        #     #     log.warning(type(space_df_copy.at[space, col_name]))
        #     # space_df_copy.at[space, col_name]
        #     space_df_copy.at[space, col_name].append(agent)
        #
        # # for agent, space in zip(agent_idx, space_idx):
        # #     # log.debug(f'{agent} enter {space}')
        # #     try:
        # #         space_df_copy.at[space, col_name].append(agent)
        # #     except KeyError:
        # #         print(agent, space)
        # #         print(space_idx)
        # #         print(agent_idx)
        # self.space_df = space_df_copy
        # # try:
        # self.susceptible_df.loc[agent_idx, 'position_index'] = space_idx
        # finally:
        #     log.debug(f'infected: {self.susceptible_df.index}')
        self.susceptible_df.loc[susceptible_idx, 'space_acreage'] = self.space_df.loc[space_idx, 'acreage'].tolist()

    def mandatory_mask(self):
        log.warning('mandatory mask')
        # only the staffs in the stores and shops are mandatory to wear the mask
        mandatory_mask_ppl_idx = chain.from_iterable((self.space_df.query('type<2'))['staffs_idx'])
        mandatory_mask_ppl_idx = set(mandatory_mask_ppl_idx).intersection(set(self.susceptible_df.index))
        self.susceptible_df.loc[mandatory_mask_ppl_idx, 'infect_buff'] *= mask_buff

    def optional_mask(self):
        log.warning('optional mask')
        # only the staffs in the stores and shops are mandatory to wear the mask
        mandatory_mask_ppl_idx = chain.from_iterable((self.space_df.query('type<2'))['staffs_idx'])
        mandatory_mask_ppl_idx = set(mandatory_mask_ppl_idx).intersection(set(self.susceptible_df.index))
        self.susceptible_df.loc[mandatory_mask_ppl_idx, 'infect_buff'] /= mask_buff
