from mesa import Agent, Model
from mesa.time import StagedActivation
from mesa.datacollection import DataCollector
import random
from tools.shapely_func import random_points_in_polygon_rejection, random_rectangle, \
    load_building_shapes_from_file, save_building_shapes_to_file, random_point_in_polygon
from shapely.geometry import Polygon, MultiPolygon
from mesa_geo import GeoAgent
import math
from numpy.random import randint
import time


def point_dst(coord_p1, coord_p2):
    return math.sqrt((coord_p1[0]-coord_p2[0])**2 + (coord_p1[1]-coord_p2[1])**2)

# FOR INTERFACE:
# programmable parameters:
# n agents, n areas and their positions, agent role %, family size distr, age distr, occupation distr, sim duration
# advanced: schedule with respect to age, occupation

#
# POSSIBLE GENOME: [inf_radius, inf_chance]

# features:
# 2 types of agents:
# 1) areas(homes, workplaces, schools, leisure areas); polygon shape, static position
# 2) "people", assigned to a home and possibly to a workplace; point shape, variable position

# sim steps
# -generate areas
# -assign each agent to a home and possibly work zone
# -simulate

# agents behave according to a schedule which depends on their "role" (worker, student, unemployed etc.)


# TO-DO: improve handling of death outcome (remove agent when it dies instead of setting its state as dead)
# note: just using the built-in remove_agent() method will cause a bug

# IDEA FOR BETTER PERFORMANCE(!)
# in stage 2: only agents in leisure will compute inf chance of nearby agents
# -> AreaAgents in stage two will get all agents inside and process infection phase of all of them (TO DEFINE)

# NOTE: mesa has no built-in visualization tools for continous spaces (only for grids)
# NOTE 2: current continous space implementation is substantially slower than the one with the grid
# further optimization is required

# IMPLEMENTATION NOTES
# 2 lists of agents:
# areas (GeoAgents) -> spatial coordinates and extension defined by shapely object
# active agents (normal Agents) -> spatial coordinates defined by pair of values

# STAGES

# 1) MOVEMENT
# done by normal Agents
# DEPENDING ON SCHEDULE WE HAVE 2 TYPES OF MOVEMENT
# - INTRA-ZONE MOVEMENT
# agent new position can only be within the boundaries of the area they are in
# - INTER-ZONE MOVEMENT
# agents will remove themselves from list of the areaAgent they were in and insert themselves
# in the list of the areaAgent they will move to, they will also update their currzone attribute, their new coordinates
# will be within the boundaries of the new areaAgent

# 2) CONTACT
# managed by areaAgent which will have a list of agents that are currently inside them
# they will take infected agents in their list and roll a chance to infect neighbouring agents that are in the same area
# TO-DO: find a way to implement this

# 3) DISEASE COURSE
# at the end of the day (every 24 h) normal Agents will gain disease progress and could recover or die
# probability is dependent on agent attributes and time infected

# create an agent as a child of the Agent class
class EpidemicModelAgent(Agent):
    def __init__(self, unique_id, model, init_state, homeAgent, workAgent, startArea, agentAttr):
        super().__init__(unique_id, model)
        # agent attributes
        self.age = agentAttr["age"]  # determines disease severity, duration
        self.role = agentAttr["role"]  # 0:worker, 1:student, 2:unemployed; determines schedule
        # simulation attributes
        self.state = init_state  # states: 0=susceptible, 1=infected, -1=recovered
        self.t_inf = 0  # time infected, used to determine recovery chance
        self.new_infected = False  # used to prevent agents to transmit during the same step they have been infected

        # spatial model attributes
        # these are all # unique ids of an EpidemicModelAreaAgent
        if self.role == 1:  # student
            self.agent_areas = {"school": workAgent, "home": homeAgent}
        if self.role == 0:  # worker
            self.agent_areas = {"work": workAgent, "home": homeAgent}
        if self.role == 2:  # enemployed
            self.agent_areas = {"home": homeAgent}
        self.currArea_type = startArea  # string= "home", "work", "school" or "leisure"

    # STEPS
    # step 1
    def move(self):
        if self.state == self.model.states["Deceased"]:
            return
        if self.new_infected:
            self.new_infected = False
        arrival_area_type = self.model.get_move_type(self)
        if arrival_area_type == 0:
            # intra-area movement
            if self.model.DEBUG:
                start_t = time.time()
            self.intra_area_move()

            # DEBUG
            # ------------------
            if self.model.DEBUG:
                end_t = time.time()
                computation_time = end_t - start_t
                self.model.timings["cumulative_stats"]["intra_area_move"]["n"] += 1
                self.model.timings["cumulative_stats"]["intra_area_move"]["cum_sum"] += computation_time
                if computation_time > self.model.timings["values"]["intra_area_move"]["max"]:
                    self.model.timings["values"]["intra_area_move"]["max"] = computation_time
        else:
            # inter-area movement
            if arrival_area_type == "home":
                dst_area_id = self.agent_areas["home"]
            elif arrival_area_type == "work":
                dst_area_id = self.agent_areas["work"]
            elif arrival_area_type == "school":
                dst_area_id = self.agent_areas["school"]
            elif arrival_area_type == "leisure":
                dst_area_id = self.model.leisure_area_id
            else:
                raise ValueError(f"Unrecognized area type: {arrival_area_type}")

            if self.model.DEBUG:
                start_t = time.time()

            self.inter_area_move(dst_area_id)

            if self.model.DEBUG:
                end_t = time.time()
                computation_time = end_t - start_t
                self.model.timings["cumulative_stats"]["inter_area_move"]["n"] += 1
                self.model.timings["cumulative_stats"]["inter_area_move"]["cum_sum"] += computation_time
                if computation_time > self.model.timings["values"]["inter_area_move"]["max"]:
                    self.model.timings["values"]["inter_area_move"]["max"] = computation_time

            self.currArea_type = arrival_area_type

    def intra_area_move(self):
        # FOR NOW IT WILL BE A RANDOM POINT INSIDE THE BOUNDARY (same func as inter area move)
        if self.currArea_type == "leisure":
            self.pos = self.model.agent_dst_coords(self, self.model.leisure_area_id)
        else:
            self.pos = self.model.agent_dst_coords(self, self.agent_areas[self.currArea_type])
        # TODO: add functionality to take into account movement distance

    def inter_area_move(self, dst_id):
        if self.currArea_type == "leisure":
            self.model.remove_from_area(self, self.model.leisure_area_id)
        else:
            self.model.remove_from_area(self, self.agent_areas[self.currArea_type])
        self.model.add_to_area(self, dst_id)
        self.pos = self.model.agent_dst_coords(self, dst_id)

    # step 2
    def contact(self):  # handled by areaAgent
        pass

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
        # TODO: compute statistics

    def die(self):
        # update statistics
        self.model.n_dead += 1
        self.model.n_infected -= 1

        # set state to dead
        self.state = self.model.states["Deceased"]
        if self.currArea_type == "leisure":
            self.model.remove_from_area(self, self.model.leisure_area_id)
        else:
            self.model.remove_from_area(self, self.agent_areas[self.currArea_type])
        # TODO: remove agent from simulation
        # self.model.grid.remove_agent(self) # THIS CAUSES A BUG


class EpidemicModelAreaAgent(GeoAgent):
    # shape is a shapely Polygon object which defines the agent's spatial extension, it has an immutable position
    def __init__(self, unique_id, model, shape, type, initial_agents):
        super().__init__(unique_id, model, shape)
        # dynamic list of Agents inside the area
        self.agents_contained = initial_agents
        # type of zone
        self.type = type  # workplace, school, house, leisure
        self.pos = (0, 0)  # NEEDED FOR THE DATA COLLECTION
        self.state = self.model.states["Deceased"]

    def get_agents_inside(self):  # returns list of agents inside the area
        return self.agents_contained

    # step 1
    def move(self):  # areas do not move
        pass

    # step 2
    def contact(self):
        for agent in self.agents_contained:
            if agent.state != self.model.states["Deceased"]:
                if agent.state == self.model.states["Infected"] and not agent.new_infected:
                    self.agent_infect(agent)

    def agent_infect(self, center_agent):
        if self.model.DEBUG:
            start_t = time.time()
        # roll a chance to infect nearby agents of the same area
        for agent in self.agents_contained:
            if agent.state == self.model.states["Susceptible"]:
                # check if in range, function in model class -> depends on model params
                if self.model.in_range(center_agent, agent):
                    # if in range and susceptible roll chance to infect
                    if self.model.infection_chance():
                        center_agent.infect(agent)
        if self.model.DEBUG:
            end_t = time.time()
            computation_time = end_t - start_t
            self.model.timings["cumulative_stats"]["contact"]["n"] += 1
            self.model.timings["cumulative_stats"]["contact"]["cum_sum"] += computation_time
            if computation_time > self.model.timings["values"]["contact"]["max"]:
                self.model.timings["values"]["contact"]["max"] = computation_time

    # step 3
    def disease(self):
        pass


# create a model as a child of the Model class
class EpidemicModel(Model):
    role_list = ["Worker", "Student", "Unemployed"]
    states = {"Susceptible": 0, "Infected": 1, "Recovered": -1, "Deceased": -2}
    role_id = {"Worker": 0, "Student": 1, "Unemployed": 2}
    area_location_schedule = {}  # WORK, HOME, LEISURE
    age_dict = {0: "kid", 1: "adult", 2: "old"}

    # INITIALIZATION ATTRIBUTES
    curr_a_id = 0
    area_id = 0
    max_workers_in_workplace = 60
    curr_work_areaAgent = None
    curr_school_areaAgent = None
    workers_to_assign_in_curr_area = 0
    workers_employed_in_curr_area = 0
    students_employed_in_curr_area = 0
    students_to_assign_in_curr_area = 0
    max_students_per_school = 200

    leisure_areaAgent = None

    def __init__(self, N_tot, N_inf, inf_radius, inf_chance, inf_duration, mortality_rate, population_params,
                 grid_params, max_move_dst=None, buildings_file=None, DEBUG = False):

        self.DEBUG = DEBUG
        if self.DEBUG:
            self.timings = dict()
            self.timings["values"] = {"inter_area_move": {"avg": 0, "max": 0}, "intra_area_move": {"avg": 0, "max": 0},
                                      "contact": {"avg": 0, "max": 0}}
            self.timings["cumulative_stats"] = {"inter_area_move": {"n": 0, "cum_sum": 0},
                                                "intra_area_move": {"n": 0, "cum_sum": 0},
                                                "contact": {"n": 0, "cum_sum": 0}}
        print("Initializing ABM model....")
        # simulation parameters
        self.num_agents = N_tot
        self.inf_radius = inf_radius
        self.inf_chance = inf_chance
        self.inf_duration = inf_duration
        self.mortality_rate = mortality_rate
        self.curr_step = 0

        # model data
        self.schedule = StagedActivation(self, ["move", "contact", "disease"])
        self.running = True  # for batch run API
        self.current_id = 0

        # agent_lists
        self.areaAgents = {}  # dict of areaAgents, scheme: "id": areaAgent obj
        self.agents = []
        # generate Agents
        # 1st) HOME GENERATION:
        # 1) aggregate population in families
        # 2) generate spatial polygons
        # 3) iterate over families: generate agents instance of the family then, agents would need suitable ages
        # 4) generate 1 home areaAgent for each family and assign it
        # NOTE: several areaAgents can have the same area and position

        # 2nd) WORKPLACE AND SCHOOL GENERATION
        # 1) generate n spatial polygons depending on number of workers
        # 2) assign each polygon to ONE work areaAgent
        # 3) generate n spatial polygons depending on number of students
        # 4) assign each polygon to ONE school areaAgent
        # 5) randomly assign each worker and student agent to a respective work or school areaAgent

        # 3rd) LEISURE SPACE
        # TODO: IMPROVE THIS
        # generate 1
        # build a polygon with all the area in the bounding box that isn't work,school or home and generate
        # an areaAgent with that polygon as shape
        family_size_avg = population_params["f_size_avg"]
        family_size_std = population_params["f_size_std"]
        move_schedule = population_params["loc_per_hour"]
        self.movement_schedule_setup(move_schedule)

        # bounding box
        # TODO: grid_params
        bbox_vertices = grid_params["bbox"] # should be the 4 vertices of a square (ex: [(x1,y1),(x2,y2),(x3,y3),(x4,y4)]
        # x1,y1------------------------x2,y2 RECTANGLE
        #   I                            I
        #  x4,y4-----------------------x3,y3
        self.x_max = bbox_vertices[1][0]
        self.x_min = bbox_vertices[0][0]
        self.y_max = bbox_vertices[0][1]
        self.y_min = bbox_vertices[2][1]
        bbox_height = point_dst(bbox_vertices[0], bbox_vertices[3])
        bbox_base = point_dst(bbox_vertices[0], bbox_vertices[2])
        bbox_area = bbox_base*bbox_height
        self.home_ratio = grid_params["home_ratio"]  # N_house_buildings/N_families
        house_area_max = grid_params["house_a_max"]
        house_area_min = grid_params["house_a_min"]
        self.work_area_max = grid_params["work_a_max"]
        self.work_area_min = grid_params["work_a_min"]
        self.school_area_max = grid_params["school_a_max"]
        self.school_area_min = grid_params["school_a_min"]
        # aggregate population in families
        if family_size_std == 0:  # all families have same size
            N_families = int(self.num_agents/family_size_avg) + self.num_agents % family_size_avg
        else:
            # TODO: implement this, families described by a list of values (number of family members), ex: f = [4,3,1,2]
            raise ValueError("family_size_std != from 0 not yet implemented")

        house_polygons, workplaces = (None, None)
        if buildings_file is not None:
            house_polygons, workplaces = self.load_building_shapes(buildings_file)
        if house_polygons is None:  # houses are not loaded
            # generate spatial polygons
            n_house_polygons = self.home_ratio * N_families
            n_polygons = 0
            house_polygons = []
            print("Building houses....")
            # TODO: ADD FUNCTIONALITY TO LOAD SIM SPACE FROM FILE
            n = 0
            while n_polygons < n_house_polygons:
                # polygon shape will be a rectangle with random area an base/height ratio
                # r = b/h, a=h*b; b^2 = r*a
                # (tentative) sampling method
                # -1 define area and ratio randomly->get height and base length
                # -2 from 2 randomly selected points in the bbox generate a rectangle
                # -3 if its area overlaps with that of another polygon discard and go back to -1, otherwise insert in list
                area = random.uniform(house_area_min, house_area_max)
                ratio = random.uniform(0.2, 0.8)
                base_l = math.sqrt(ratio*area)
                height_l = area/base_l
                # RANDOM SAMPLING
                stop = False
                max_iter = 1000000
                iteration = 0
                while not stop:
                    # TODO: improve random_rectangle so that they are not always parallel to x and y axis
                    # TODO: improve n_families distribution
                    house_polygon = {"shape": random_rectangle(self.x_min, self.y_min, self.x_max, self.y_max,
                                                               base_l, height_l), "n_families": self.home_ratio}
                    intersects = False
                    # FIXME: reaches max iterations very easily
                    # check if it overlaps another polygon
                    for p in house_polygons:
                        shape = p["shape"]
                        if shape.intersects(house_polygon["shape"]):
                            intersects = True
                            break
                    if not intersects:
                        # if it doesn't accept it
                        stop = True
                        house_polygons.append(house_polygon)
                    iteration += 1
                    if iteration == max_iter:
                        raise RuntimeError("random sampling for house polygon reached max iterations")
                n_polygons += 1
        self.workplaces_in_file = False
        if workplaces is not None:
            self.workplaces_in_file = True
            self.workplace_polygons = workplaces
        # iterate over families: generate agents instance of the family then, agents would need suitable ages
        # then generate and assign them a home areaAgent
        n_families = 0
        # counters to generate work and school areas
        n_workers = 0
        n_students = 0
        print("Generating families....")
        if family_size_std == 0:  # const number of members
            family_size = family_size_avg
            while n_families <= N_families:
                # GENERATE FAMILY MEMBERS
                # TODO: improve with better random variations and derived limit values
                # families will have 1-2 adults, possibly old people, possibly kids
                n_adults = randint(1, 3)  # 1 or 2
                n_old = randint(0, family_size-n_adults+1)
                n_kids = family_size-n_old

                # GENERATE HOME
                # iterate through home_polygons until one with available slot is found
                home_id = None
                for h_polygon in house_polygons:
                    if h_polygon["n_families"] != 0:
                        home_id = "a"+str(self.curr_a_id)
                        new_areaAgent = EpidemicModelAreaAgent(unique_id=home_id, initial_agents=[],
                                                               shape=h_polygon["shape"], model=self, type="Home")
                        self.schedule.add(new_areaAgent)  # add to scheduler
                        self.areaAgents[home_id] = new_areaAgent
                        self.curr_a_id += 1
                        h_polygon["n_families"] -= 1
                        break
                if home_id is None:
                    raise ValueError("No house could be found")
                # TODO: make employement chance depend on unemployement rate and policies (such as lockdown)
                # INSTANTIATE FAMILY MEMBERS AGENTS AND ASSIGN HOMES

                for a in range(0, n_adults):
                    n_workers += 1
                    agent_attr = {"role": self.role_id["Worker"], "age": 1}  # look at age_dict attribute
                    new_agent = EpidemicModelAgent(unique_id=self.current_id, model=self, homeAgent=home_id,
                                                   workAgent=self.get_workplace(self.work_area_min, self.work_area_max),
                                                   init_state=self.states["Susceptible"],  startArea="home",
                                                   agentAttr=agent_attr)
                    self.current_id += 1
                    self.schedule.add(new_agent)
                    self.agents.append(new_agent)
                    self.areaAgents[home_id].agents_contained.append(new_agent)
                    self.add_to_area(new_agent, home_id)  # set initial position in their home
                    new_agent.pos = self.agent_dst_coords(self, home_id)
                for a in range(0, n_old):
                    agent_attr = {"role": self.role_id["Unemployed"], "age": 2}  # look at age_dict attribute
                    new_agent = EpidemicModelAgent(unique_id=self.current_id, model=self, homeAgent=home_id, workAgent=None,
                                                   init_state=self.states["Susceptible"],  startArea="home",
                                                   agentAttr=agent_attr)
                    self.current_id += 1
                    self.schedule.add(new_agent)
                    self.agents.append(new_agent)
                    self.add_to_area(new_agent, home_id)  # set initial position in their home
                    new_agent.pos = self.agent_dst_coords(self, home_id)
                for a in range(0, n_kids):
                    n_students += 1
                    agent_attr = {"role": self.role_id["Student"], "age": 0}  # look at age_dict attribute
                    new_agent = EpidemicModelAgent(unique_id=self.current_id, model=self, homeAgent=home_id,
                                                   workAgent=self.get_school(self.school_area_min, self.school_area_max),
                                                   init_state=self.states["Susceptible"], startArea="home",
                                                   agentAttr=agent_attr)
                    self.current_id += 1
                    self.schedule.add(new_agent)
                    self.agents.append(new_agent)
                    self.add_to_area(new_agent, home_id)  # set initial position in their home
                    new_agent.pos = self.agent_dst_coords(self, home_id)

                n_families += 1

        # GENERATE LEISURE SPACES
        # (tentative) define a single areaAgent with a shape that contains all the area that isn't used
        polygon_list = []
        for areaAgent in self.areaAgents.values():
            polygon_list.append(areaAgent.shape)
        aggregate_multi_p = MultiPolygon(polygon_list)
        # draw_multipolygon(aggregate_multi_p) # PREVIEW OF THE AREAS
        bbox_polygon = Polygon([(self.x_min, self.y_min), (self.x_max, self.y_min), (self.x_max, self.y_max),
                                (self.x_min, self.y_max)])
        leisure_area_shape = bbox_polygon.difference(aggregate_multi_p)
        self.leisure_area_id = "a"+str(self.curr_a_id)
        self.curr_a_id += 1
        self.leisure_areaAgent = EpidemicModelAreaAgent(unique_id=self.leisure_area_id, initial_agents=[], shape=leisure_area_shape,
                                                          model=self, type="Leisure")
        self.areaAgents[self.leisure_area_id] = self.leisure_areaAgent

        self.schedule.add(self.leisure_areaAgent)

        if family_size_std != 0:
            # TODO: implement this
            pass

        n_infected = N_inf
        self.n_infected = 0
        while self.n_infected < n_infected:
            random_index = random.randint(0, len(self.agents) - 1)
            self.agents[random_index].state = self.states["Infected"]
            self.n_infected += 1

        # Statistics
        N_tot = len(self.agents)
        self.n_dead = 0
        self.n_susceptible = N_tot-n_infected
        self.n_recovered = 0
        self.datacollector = DataCollector(model_reporters={"Deceased": "n_dead",
                                                            "Recovered": "n_recovered",
                                                            "Susceptible": "n_susceptible",
                                                            "Infected": "n_infected"},
                                           agent_reporters={"Position": "pos",
                                                            "State": "state"})

        print("Model initialized....")

    def get_workplace(self, area_min, area_max):
        if self.workers_employed_in_curr_area == self.workers_to_assign_in_curr_area:
            self.workers_to_assign_in_curr_area = random.uniform(4, self.max_workers_in_workplace)
            work_id = "a"+str(self.curr_a_id)
            work_area = None
            if self.workplaces_in_file:
                for polygon in self.workplace_polygons:
                    if not polygon["used"]:
                        work_area = polygon["shape"]
                        polygon["used"] = True
                        break
                if work_area is None:
                    self.workplaces_in_file = False
            if not self.workplaces_in_file:
                work_area = self.generate_non_overlapping_area(area_min, area_max)

            self.curr_work_areaAgent = new_areaAgent = EpidemicModelAreaAgent(unique_id=work_id, initial_agents=[],
                                                                              shape=work_area, model=self, type="Work")
            self.schedule.add(new_areaAgent)  # add to scheduler
            self.areaAgents[work_id] = new_areaAgent
            self.curr_a_id += 1
            self.workers_employed_in_curr_area = 0
        self.workers_employed_in_curr_area += 1
        return self.curr_work_areaAgent.unique_id

    def get_school(self, area_min, area_max):
        if self.students_employed_in_curr_area == self.students_to_assign_in_curr_area:
            self.students_to_assign_in_curr_area = random.uniform(20, self.max_students_per_school)
            school_id = "a" + str(self.curr_a_id)
            school_area = self.generate_non_overlapping_area(area_min, area_max)
            self.curr_school_areaAgent = new_areaAgent = EpidemicModelAreaAgent(unique_id=school_id, initial_agents=[],
                                                                              shape=school_area, model=self, type="School")
            self.schedule.add(new_areaAgent)  # add to scheduler
            self.areaAgents[school_id] = new_areaAgent
            self.curr_a_id += 1
            self.students_employed_in_curr_area = 0
        self.students_employed_in_curr_area += 1
        return self.curr_school_areaAgent.unique_id

    def generate_non_overlapping_area(self, area_max, area_min):
        # generate a random rectangle that doesn't overlap any area used by existing areaAgent
        area = random.uniform(area_min, area_max)
        ratio = random.uniform(0.2, 0.8)
        base_l = math.sqrt(ratio * area)
        height_l = area / base_l
        # RANDOM SAMPLING
        stop = False
        max_iter = 10000
        iteration = 0
        while not stop:
            # TODO: improve random_rectangle so that they are not always parallel to x and y axis
            # TODO: improve n_families distribution
            generated_polygon = random_rectangle(self.x_min, self.y_min, self.x_max, self.y_max, base_l, height_l)
            intersects = False
            # check if it overlaps another polygon
            for areaAgent in self.areaAgents.values():
                if areaAgent.shape.intersects(generated_polygon):
                    intersects = True
                    break
            if not intersects:
                # if it doesn't accept it
                stop = True
            iteration += 1
            if iteration == max_iter:
                raise RuntimeError("random sampling for house polygon reached max iterations")
        return generated_polygon

    def movement_schedule_setup(self, input_schedule):
        # input schedule: dict in form {role_id : loc_list}, location list: list (size 24) containing loc of each hour
        # loc is a string = "home", "work", "school" or "leisure"
        # check validity
        for scheduled_role in input_schedule.keys():
            if len(input_schedule[scheduled_role]) != 24:
                raise ValueError(f"input schedule for role: {scheduled_role} has length "
                                 f"{len(input_schedule[scheduled_role])}, should be 24")
        for role in self.role_list:
            self.area_location_schedule[self.role_id[role]] = []
            for hour in range(0, 24):
                self.area_location_schedule[self.role_id[role]].append(input_schedule[role][hour])

    # models moves in steps (ticks), at each tick each active agent perform and action (1 tick = 1 hour)
    # the scheduler controls the order in which the agents act
    def step(self):
        # performs 1 simulation step
        self.curr_step += 1
        self.datacollector.collect(self)
        self.schedule.step()

    # AGENT ACTIONS
    # function to decide what type of movement (intra or inter area) and destination area of agent
    def get_move_type(self, agent):
        # depends agent.role
        try:
            curr_hour = self.get_curr_hour()
            new_loc_type = self.area_location_schedule[agent.role][curr_hour]
        except IndexError:
            print(self.area_location_schedule)
            raise IndexError(f"list index ({curr_hour}) out of range, role: {agent.role}")
        if new_loc_type == agent.currArea_type:
            # intra-area movement
            return 0
        else:
            # inter-area movement
            return new_loc_type

    # SIMULATION FUNCTIONS
    # roll a chance to infect
    def infection_chance(self):
        # TODO: improve infection function
        if random.uniform(0, 1) < self.inf_chance:
            return True
        return False

    def get_curr_hour(self):
        return self.curr_step % 24

    # SPATIAL FUNCTIONS
    # finds if agent is in the infection radius of "center_agent"
    def in_range(self, center_agent, agent):
        # TODO: find a faster way to compute dst
        if math.sqrt((center_agent.pos[0]-agent.pos[0])**2+(center_agent.pos[1]-agent.pos[1])**2) > self.inf_radius:
            return 1
        return 0

    def remove_from_area(self, agent_to_remove, agent_area_id):
        # this should work as agent object seems to be assigned to areaAgent list by reference
        self.areaAgents[agent_area_id].agents_contained.remove(agent_to_remove)

    def add_to_area(self, agent_to_add, new_area_id):
        self.areaAgents[new_area_id].agents_contained.append(agent_to_add)

    def agent_dst_coords(self, agent, dst_area_id):
        # TODO: find a better optimized movement function
        # function to set agent coordinates in inter-area movement
        # selects a random point inside the specified area
        # x_arrival, y_arrival = random_points_in_polygon_rejection(self.areaAgents[dst_area_id].shape, 1)[0]
        x, y = self.areaAgents[dst_area_id].shape.representative_point().xy
        x_arrival, y_arrival = x[0], y[0]
        return x_arrival, y_arrival

    def load_building_shapes(self, fileName):
        # load houses, workplaces shapes from file
        # home output should be list of obj {"shape": shapely.polygon, "n_famiilies": int}
        # work output should be list of obj {"shape": shapely.polygon, "used": Bool}->"used" initialized as False
        house_polygons, workplace_polygons = load_building_shapes_from_file(fileName, ["house", "work"])
        house_buildings = []
        work_buildings = []
        if len(house_polygons) == 0:
            house_buildings = None
        else:
            for house_p in house_polygons:
                house_buildings.append({"shape": house_p, "n_families": self.home_ratio})
        if len(workplace_polygons) == 0:
            work_buildings = None
        else:
            for work_p in house_polygons:
                work_buildings.append({"shape": work_p, "used": False})
        return house_buildings, work_buildings

    # DATA COLLECTION FUNCTIONS
    def get_model_data(self):
        return self.datacollector.get_model_vars_dataframe()

    def get_agent_data(self):
        return self.datacollector.get_agent_vars_dataframe()

    # GET BUILDING SHAPES
    def get_polygons(self, b_type):
        output_polygon_list = []
        for area_agent in self.areaAgents.values():
            if area_agent.type == b_type:
                output_polygon_list.append(area_agent.shape)
        return output_polygon_list

    # DEBUG FUNCTIONS
    def get_debug_data(self):
        for agent_action in self.timings["values"].keys():
            self.timings["values"][agent_action]["avg"] = self.timings["cumulative_stats"][agent_action]["cum_sum"]/\
                                                          self.timings["cumulative_stats"][agent_action]["n"]

        return self.timings["values"]


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

    # # retrieve a pandas Timeseries object containing all agent positions at a particular step
    # positions = agent_data["Position"]
    # states = agent_data["State"]
    # positions[10]  # position of tenth agent, tuple (x, y)
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
    model = EpidemicModel(N_tot=100, N_inf=10, inf_radius = 1, inf_chance = 0.05, inf_duration = 10*24, mortality_rate = 0.05,
                          max_move_dst = 10, population_params = pop_params, grid_params = grid_params)
    # testM = EpidemicModel(N_tot=100, N_inf=5, , height=500, inf_chance=0.7, inf_radius=5,
    # inf_duration=30, mortality_rate=0.001, grid_space=False, cont_move_max_d=1, cont_move_min_d=10)
    final_step = 0
    max_steps = 24*30     # number of simulation steps
    print(f"there are: {len(model.agents)} agents")
    print("Starting simulation....")
    for i in range(max_steps):
        model.step()
        print(f"STEP: {i}, Susceptible: {model.n_susceptible}, Infected: {model.n_infected}, "
              f"Deceased: {model.n_dead}, Recovered: {model.n_recovered}")
        if model.n_infected == 0:
            final_step = i
            break
        final_step = i

    # get agent data multIndex
    agent_data = model.get_agent_data()  # pd dataframe with step[i]: agentID: (pos,state)
    model_data = model.get_model_data()
    print(model_data)
    model_space_height = x_max
    model_space_width = y_max

    # animated plot
    # a = AnimatedEpidemicPlot(agent_dataframe=agent_data, height=model_space_height, width=model_space_width,
    #                          state_int_values=model.states, n_steps=final_step, fps=2, agent_size=1)
    # # plt.show()
    # a.save_animation("spatial_model.gif", 2, "gif")

    # Effective daily reproduction number of day t:
    #   Rt[t] = (total number of new infected of day t)/(tot number of infected(at the start of day t))
    # mortality : daily number of deaths
