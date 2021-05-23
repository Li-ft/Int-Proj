from model.spatial_model import EpidemicModel
import numpy as np
from tools.shapely_func import save_building_shapes_to_file
import pandas as pd
import json
import os
ABSOLUTE_PATH = os.path.dirname(os.path.abspath(__file__))


class EpidemicSimulation:

    def __init__(self, agent_output_file = None, sim_output_file = None):
        # TODO: load from settings file
        self.print_realtime = False
        self.model = None
        self.max_steps = 0
        self.final_step = 0
        self.a_output_file = agent_output_file
        self.s_output_file = sim_output_file
        self.building_data_file = None  # files from where building data will be loaded
        self.building_store_data_file = None  # files where building data will be stored
        self.timings_result_file = None

    def initialize(self, N_tot, N_inf, inf_radius, inf_chance, inf_duration, mortality_rate, population_params,
                 grid_params, sim_steps, max_move_dst=None, print_realtime = False, DEBUG = False):

        self.model = EpidemicModel(N_tot, N_inf, inf_radius, inf_chance, inf_duration, mortality_rate, population_params,
                 grid_params, buildings_file=self.building_data_file, DEBUG=DEBUG)
        self.max_steps = sim_steps
        self.print_realtime = print_realtime

    def simulate(self):
        if self.a_output_file is None:
            print("WARNING: agent data output directory not set, data won't be stored to file")
        if self.s_output_file is None:
            print("WARNING: model data output directory not set, data won't be stored to file")
        for i in range(self.max_steps):
            self.model.step()
            if self.print_realtime:
                print(f"STEP: {i}, Susceptible: {self.model.n_susceptible}, Infected: {self.model.n_infected}, "
                      f"Deceased: {self.model.n_dead}, Recovered: {self.model.n_recovered}")
            if self.model.n_infected == 0:
                self.final_step = i
                break
            if self.model.n_susceptible == 0:
                self.final_step = i
                break
        self.store_results()
        if self.model.DEBUG:
            self.timings_results()

    def compute_rt_value(self, aggregation = 24):
        model_data = self.model.get_model_data()
        I = model_data["Infected"]
        R = model_data["Recovered"]
        D = model_data["Deceased"]
        # rt = number of new infections / total number of infected
        # I[t] infected at the start of day t, I[t+1] infected at the start of day t+1(end of day t)
        # R: recovered, R[t] - R[t+1] = recovered
        # I[t+1] = I[t] + newI - newR - newD  # change of number of infected over time
        # R[t+1] = R[t] + newR -> newR = R[t+1] - R[t] # change in number of recovered over time
        # D[t+1] = D[t] + newD -> newD = D[t+1] - D[t] # change in number of recovered over time
        # newI[t] = I[t+1] - I[t] + newR[t] = I[t+1] - I[t] + R[t+1] - R[t] + D[t+1] - D[t]
        # Rt = newI[t]/I[t]
        sim_n_days = int(self.final_step/aggregation)  # skip the last incomplete day
        day = 1
        rt = np.zeros(sim_n_days)  # Rt = 0 for the first day
        while day < sim_n_days:
            newI = I[day*aggregation] - I[(day-1)*aggregation] + R[day*aggregation] - R[(day-1)*aggregation] + \
                   D[day*aggregation] - D[(day-1)*aggregation]
            rt[day] = newI/I[(day-1)*aggregation]
            day += 1
        return rt

    def get_timeseries(self, series_name):
        # series_name can be: "Deceased", "Recovered", "Infected", "Susceptible"
        model_data = self.model.get_model_data()
        return model_data[series_name]

    def store_results(self):
        if self.a_output_file is None:
            print("WARNING: agent data output directory not set, data won't be stored to file")
        else:
            output_df = self.model.get_model_data()
            output_df.to_csv(self.a_output_file)
        if self.s_output_file is None:
            print("WARNING: model data output directory not set, data won't be stored to file")
        else:
            output_df = self.model.get_agent_data()
            output_df.to_csv(self.s_output_file)

    # MODEL DATA MANAGEMENT
    def set_directories(self, agent_data_output, sim_data_output, buildings_load_file=None, buildings_save_file=None,
                        debug_output = None):
        self.a_output_file = agent_data_output
        self.s_output_file = sim_data_output

        if buildings_load_file is not None:
            self.building_data_file = buildings_load_file
        if buildings_save_file is not None:
            self.building_store_data_file = buildings_save_file
        if debug_output is not None:
            self.timings_result_file = debug_output

    def store_buildings(self):
        if self.building_store_data_file is None:
            print("WARNING: building storage data not set, building cannot be stored")
        else:
            output_dict = {}
            for b_type in ["house", "work"]:
                output_dict[b_type] = self.model.get_polygons(b_type)
            save_building_shapes_to_file(self.building_store_data_file, output_dict)  # save building shapes to file

    def timings_results(self):
        timing_data = self.model.get_debug_data()
        print("computational timings:")
        for agent_action in timing_data.keys():
            print(f"{agent_action}: avg:{timing_data[agent_action]['avg']}, max: {timing_data[agent_action]['max']}")
        if self.timings_result_file is not None:
            self.store_timings(timing_data)

    def store_timings(self, timings_dict):
        with open(self.timings_result_file, "w") as fp:
            json.dump(timings_dict, fp)


if __name__ == "__main__":
    print("starting simulation..")
    x_max = 5000
    x_min = 0
    y_max = 5000
    y_min = 0
    bbox = [(0, y_max), (x_max, y_max), (x_max, 0), (0, 0)]
    # should be the 4 vertices of a square (ex: [(x1,y1),(x2,y2),(x3,y3),(x4,y4)]
    # x1,y1------------------------x2,y2 RECTANGLE
    #   I                            I
    #  x4,y4-----------------------x3,y3
    loc_schedule = {"Worker": [], "Student": [], "Unemployed": []}
    for h in range(0, 8):
        loc_schedule["Worker"].append("home")
    for h in range(8, 18):
        loc_schedule["Worker"].append("work")
    for h in range(18, 21):
        loc_schedule["Worker"].append("leisure")
    for h in range(21, 24):
        loc_schedule["Worker"].append("home")
    for h in range(0, 8):
        loc_schedule["Student"].append("home")
    for h in range(8, 17):
        loc_schedule["Student"].append("school")
    for h in range(17, 22):
        loc_schedule["Student"].append("leisure")
    for h in range(22, 24):
        loc_schedule["Student"].append("home")
    for h in range(0, 17):
        loc_schedule["Unemployed"].append("home")
    for h in range(17, 20):
        loc_schedule["Unemployed"].append("leisure")
    for h in range(20, 24):
        loc_schedule["Unemployed"].append("home")
    pop_params = {"f_size_avg": 4, "f_size_std": 0, "loc_per_hour": loc_schedule}
    grid_params = {"home_ratio": 3, "house_a_max": 500, "house_a_min": 100, "school_a_max": 1000, "school_a_min": 500,
                   "work_a_max": 1000, "work_a_min": 100, "bbox": bbox}
    # 4 area types "home", "work", "school", "leisure"
    agent_output_file = ABSOLUTE_PATH+"/results/agent_data.csv"
    sim_output_file = ABSOLUTE_PATH+"/results/sim_data.csv"
    out_b_file = ABSOLUTE_PATH+"/model_data/buildings.json"
    in_b_file = ABSOLUTE_PATH+"/model_data/buildings.json"
    test = EpidemicSimulation(agent_output_file, sim_output_file)
    test.set_directories(agent_output_file, sim_output_file, None, out_b_file)
    test.initialize(N_tot=1000, N_inf=10, inf_radius=0.1, inf_chance=0.0001, inf_duration=10 * 24, mortality_rate=0.001,
                    max_move_dst=10, population_params=pop_params, grid_params=grid_params, sim_steps=2000,
                    print_realtime=True, DEBUG=True)
    test.simulate()
    print("simulation ended..")
    print("storing buildings..")
    test.store_buildings()
    print("buildings stored")
    # GETTING RT VALUES, NOTE: RT[0] = 0 (Rt of day 0)
    rt_list = test.compute_rt_value()
    # GETTING DECEASED TIMESERIES, NOTE: it's hour by hour
    deceased = test.get_timeseries("Deceased")
