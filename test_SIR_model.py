from mesa import Agent, Model
from mesa.time import RandomActivation, StagedActivation
import matplotlib.pyplot as plt
from mesa.space import ContinuousSpace, MultiGrid
from mesa.datacollection import DataCollector
import numpy as np
from mesa.batchrunner import BatchRunner
import random
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import ChartModule
import time

# TO-DO: improve handling of death outcome (remove agent when it dies instead of setting its state as dead)
# note: just using the built-in remove_agent() method will cause a bug

# very simple test model
# implements a basic ABM for epidemics (SIR states)

# action is done through the StagedActivation scheduler
# 3 stages:
# 1) movement->all agents move in random directions
# 2) infection-> all infected agents roll a chance to infect susceptible neighbours
# 3) disease course-> all infected agents roll to die or recover


# NOTE: mesa has no built-in visualization tools for continuous spaces (only for grids)
# NOTE 2: current continuous space implementation is substantially slower than the one with the grid
# further optimization is required
# NOTE: time for recovering is fixed rather than random

# create an agent as a child of the Agent class
class EpidemicModelAgent(Agent):

    def __init__(self, unique_id, model, init_state):
        super().__init__(unique_id, model)
        self.state = init_state
        # states: 0=susceptible, 1=infected, -1=recovered
        self.t_inf = 0  # time infected, used to determine recovery chance
        self.new_infected = False  # used to prevent agents to transmit during the same step they have been infected

    # STEPS
    # step 1
    def move(self):
        if self.state == self.model.states["Deceased"]:
            return
        new_pos = self.get_new_agent_pos()
        self.model.grid.move_agent(self, new_pos)

    # step 2
    def contact(self):
        if self.state == self.model.states["Deceased"]:
            return
        if self.state == self.model.states["Infected"] and not self.new_infected:
            # this step has an execution time of the order of 10^-4 for continuous space and it is the
            # step that slows down the model
            # agents infected
            for neighbour in self.get_neighbouring_agents():
                if neighbour.state == self.model.states["Susceptible"]:
                    # infection chance
                    # get a random number between between 0 and 1, compare with transmission rate
                    if random.random() <= self.model.inf_chance:
                        # neighbour is infected
                        self.infect(neighbour)
        if self.new_infected:
            self.new_infected = False

    # step 3
    def disease(self):
        if self.state == self.model.states["Deceased"]:
            return
        if self.state == self.model.states["Infected"]:
            self.t_inf += 1
            if not self.recover():
                if random.random() <= self.model.mortality_rate:
                    # death chance
                    # get a random number between between 0 and 1, compare with mortality rate
                    self.die()

    # other methods
    def recover(self):
        # fixed number of days needed to recover
        if self.t_inf >= self.model.inf_duration:
            # update statistics
            self.model.n_recovered += 1
            self.model.n_infected -= 1

            # recover and become Recovered (immune)
            self.state = self.model.states["Recovered"]
            return True
        else:
            return False

    def infect(self, agent):
        # update statistics
        self.model.n_infected += 1
        self.model.n_susceptible -= 1
        # infect another agent
        agent.state = self.model.states["Infected"]
        agent.new_infected = True
        # TO-DO: compute statistics

    def die(self):
        # update statistics
        self.model.n_dead += 1
        self.model.n_infected -= 1

        # set state to dead
        self.state = self.model.states["Deceased"]

        # REMOVING AGENT FROM SIMULATION WOULD BE IDEAL
        # self.model.grid.remove_agent(self) # THIS CAUSES A BUG

    # SPACE DEPENDENT METHODS, THEY MUST BE OVERRIDDEN BY CHILD CLASSES
    def get_new_agent_pos(self):
        # TO BE OVERWRITTEN BY CHILD CLASSES
        pass

    def get_neighbouring_agents(self):
        # TO BE OVERWRITTEN BY CHILD CLASSES
        pass


class EpidemicModelAgentContinous(EpidemicModelAgent):

    def get_new_agent_pos(self):
        # execution time is on the order of 10^-6

        # select a random number between max and min dst and add to both
        # x and y
        tmp = random.getrandbits(1)
        x_sign = 1*tmp-1*(1-tmp)
        tmp = random.getrandbits(1)
        y_sign = 1*tmp-1*(1-tmp)
        rand_x = x_sign*random.uniform(self.model.min_d, self.model.max_d)
        rand_y = y_sign*random.uniform(self.model.min_d, self.model.max_d)
        return self.pos[0]+rand_x, self.pos[1]+rand_y

    def get_neighbouring_agents(self):
        # get agents in a radius
        # WARNING: this function has an execution time of the order of 10^-4 and slows down the computation
        # significantly
        return self.model.grid.get_neighbors([self.pos], radius=self.model.inf_radius)


class EpidemicModelAgentGrid(EpidemicModelAgent):

    def get_new_agent_pos(self):
        # select a random neighbouring square
        possible_steps = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False)
        return self.random.choice(possible_steps)


    def get_neighbouring_agents(self):
        # all agents in the same cell
        return self.model.grid.get_cell_list_contents([self.pos])


# create a model as a child of the Model class
class EpidemicModel(Model):
    states = {"Susceptible": 0, "Infected": 1, "Recovered": -1, "Deceased": -2}

    def __init__(self, N_tot, N_inf, width, height, inf_radius, inf_chance, inf_duration, mortality_rate, grid_space=True,
                 cont_move_max_d=None, cont_move_min_d=None):
        if not grid_space and (cont_move_max_d is None or cont_move_min_d is None):
            raise ValueError("max and min move distance are not specified")

        # model parameters
        self.num_agents = N_tot
        self.inf_radius = inf_radius
        self.inf_chance = inf_chance
        self.inf_duration = inf_duration
        self.mortality_rate = mortality_rate

        # continous movement
        self.max_d = cont_move_max_d
        self.min_d = cont_move_min_d

        # TO-DO: try simultaneous activation
        self.schedule = StagedActivation(self, ["move", "contact", "disease"])
        # instantiate the grid
        if grid_space:
            self.grid = MultiGrid(width, height, torus=True)
        else:
            self.grid = ContinuousSpace(width, height, torus=True)
        self.running = True  # for batch run API
        # instantiate agents
        n_infected = 0
        for i in range(self.num_agents):
            # instantiate agents
            if n_infected < N_inf:
                init_state = self.states["Infected"]
                n_infected += 1
            else:
                init_state = self.states["Susceptible"]

            if grid_space:
                a = EpidemicModelAgentGrid(i, self, init_state=init_state)
            else:
                a = EpidemicModelAgentContinous(i, self, init_state=init_state)
            self.schedule.add(a)  # add the agent to the schedule

            # add the agent to the grid
            # random starting position
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))

        # Statistics
        self.n_dead = 0
        self.n_infected = n_infected
        self.n_susceptible = N_tot-n_infected
        self.n_recovered = 0

        self.datacollector = DataCollector(model_reporters={"Deceased": "n_dead",
                                                            "Recovered": "n_recovered",
                                                            "Susceptible": "n_susceptible",
                                                            "Infected": "n_infected"},
                                           agent_reporters={"Position": "pos",
                                                            "State": "state"})

        print("model initialized")

    # models moves in steps (ticks), at each tick each active agent perform and action
    # the scheduler controls the order in which the agents act
    def step(self):
        # performs 1 simulation step
        self.datacollector.collect(self)
        self.schedule.step()

def agent_portrayal(agent):
    portrayal = {"Shape": "circle",
                 "Color": "red",
                 "Filled": "true",
                 "Layer": 0,
                 "r": 0.5}
    if agent.state == 0:  # susc
        portrayal["Color"] = "green"
        portrayal["Layer"] = 1
        portrayal["r"] = 0.5
    if agent.state == -1:  # inf
        portrayal["Color"] = "red"
        portrayal["Layer"] = 1
        portrayal["r"] = 0.3
    if agent.state == -1:  # rec
        portrayal["Color"] = "blue"
        portrayal["Layer"] = 2
        portrayal["r"] = 0.2
    if agent.state == -2:  # ded
        portrayal["Color"] = "black"
        portrayal["Layer"] = 4
        portrayal["r"] = 0.1
    return portrayal


if __name__ == "__main__":
    testM = EpidemicModel(N_tot=1000, N_inf=5, width=500, height=500, inf_chance=0.7, inf_radius=5,
                              inf_duration=30, mortality_rate=0.001, grid_space=False, cont_move_max_d=1, cont_move_min_d=10)
    start_t = time.process_time()
    for i in range(100):
        testM.step()
        print(f"STEP: {i}, Susceptible: {testM.n_susceptible}, Infected: {testM.n_infected}, "
              f"Deceased: {testM.n_dead}, Recovered: {testM.n_recovered}")
        if testM.n_infected == 0:
            break
    stop_t = time.process_time()
    print("SIMULATION TOOK ", stop_t-start_t, "SECONDS")

    # # get a pandas Multindex object containing all data collected from agents
    agent_positions = testM.datacollector.get_agent_vars_dataframe()
    #
    # step = 9  # step for which data is retrieved
    # # retrieve a pandas Dataframe object containing all specified agent variable for each agent at a particular step
    agent_data = agent_positions.xs(1, level="Step")
    #
    # # retrieve a pandas Timeseries object containing all agent positions at a particular step
    # positions = agent_data["Position"]
    # states = agent_data["State"]
    # positions[10]  # position of tenth agent, tuple (x, y)


    # VISUALIZATION
    # grid = CanvasGrid(agent_portrayal, 10, 10, 1000, 1000)
    # chart = ChartModule([{"Label": "Deceased",
    #                       "Color": "Black"}],
    #                     data_collector_name='datacollector')
    #
    # server = ModularServer(EpidemicModelTest,
    #                        [grid, chart],
    #                        "Epidemic Test",
    #                        {"N_tot": 100,
    #                         "N_inf":10,
    #                         "width":10,
    #                         "height": 10,
    #                         "inf_radius":1,
    #                         "inf_chance":0.5,
    #                         "inf_duration":10,
    #                         "mortality_rate": 0.1,
    #                         "grid": True})
    # server.port = 8521
    # server.launch()

    # run model and plot the wealth distribution
    # batch runs
    # fixed_params = {
    #     "width": 10,
    #     "height": 10
    # }
    # variable_params = {"N": range(10, 500, 10)}
    #
    # batch_run = BatchRunner(EpidemicModelTest,
    #                         variable_params,
    #                         fixed_params,
    #                         iterations=5,
    #                         max_steps=100,
    #                         model_reporters={"Gini": compute_gini})
    # batch_run.run_all()
    # run_data = batch_run.get_model_vars_dataframe()
    # plt.scatter(run_data.N, run_data.Gini)
    # plt.show()
    # gini = model.datacollector.get_model_vars_dataframe()
    # gini.plot()
    # agent_wealth = model.datacollector.get_agent_vars_dataframe()
    # end_wealth = agent_wealth.xs(99, level="Step")["Wealth"]
    # end_wealth.hist(bins=range(agent_wealth.Wealth.max() + 1))
    # plt.show()

