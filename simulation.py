from model.spatial_model import EpidemicModel
import numpy as np


class EpidemicSimulation:

    def __init__(self):
        self.print_realtime = False
        self.ABMmodel = None
        self.max_steps = 0
        self.final_step = 0
        pass

    def initialize(self, N_tot, N_inf, inf_radius, inf_chance, inf_duration, mortality_rate, population_params,
                 grid_params, sim_steps, max_move_dst=None, print_realtime = False):

        self.ABMmodel = EpidemicModel(N_tot, N_inf, inf_radius, inf_chance, inf_duration, mortality_rate, population_params,
                 grid_params)
        self.max_steps = sim_steps
        self.print_realtime = print_realtime

    def simulate(self):
        for i in range(self.max_steps):
            self.ABMmodel.step()
            if self.print_realtime:
                print(f"STEP: {i}, Susceptible: {self.ABMmodel.n_susceptible}, Infected: {self.ABMmodel.n_infected}, "
                      f"Deceased: {self.ABMmodel.n_dead}, Recovered: {self.ABMmodel.n_recovered}")
            if self.ABMmodel.n_infected == 0:
                self.final_step = i
            if self.ABMmodel.n_susceptible == 0:
                self.final_step = i
                break

    def compute_rt_value(self, aggregation = 24):
        model_data = self.ABMmodel.get_model_data()
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
            print(f"day {day}: I: start: {I[(day-1)*aggregation]}, end: {I[day*aggregation]}")
            print("newI: ", newI)
            rt[day] = newI/I[(day-1)*aggregation]
            day += 1
        return rt

    def get_timeseries(self, series_name):
        # series_name can be: "Deceased", "Recovered", "Infected", "Susceptible"
        model_data = self.ABMmodel.get_model_data()
        return model_data[series_name]

    def store_results(self):
        # TODO: implement
        pass


if __name__ == "__main__":
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
    test = EpidemicSimulation()
    test.initialize(N_tot=3000, N_inf=10, inf_radius=0.1, inf_chance=0.0001, inf_duration=10 * 24, mortality_rate=0.001,
                    max_move_dst=10, population_params=pop_params, grid_params=grid_params, sim_steps=2000,
                    print_realtime=True)
    test.simulate()
    # GETTING RT VALUES, NOTE: RT[0] = 0 (Rt of day 0)
    rt_list = test.compute_rt_value()
    print(rt_list)
    # GETTING DECEASED TIMESERIES, NOTE: it's hour by hour
    deceased = test.get_timeseries("Deceased")
