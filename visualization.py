import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from matplotlib import cm
import matplotlib.colors
from test_SIR_model import EpidemicModel


# tool for visualizing animated plots of continous space epidemic ABM
class AnimatedEpidemicPlot:
    def __init__(self, agent_dataframe, state_int_values, height, width, n_steps, fps, agent_size):
        # the class expects agents to have 4 states (Recovered, Infected, Susceptible and Deceased)
        # agent_dataframe should be a pandas multIndex object with levels defined by "Step" and having columns
        # "Position" and "State"
        self.a_size = agent_size
        self.width = width
        self.height = height
        self.curr_step = 0
        self.max_step = n_steps-1
        self.m_states = state_int_values
        self.agent_dataframe = agent_dataframe

        # generate colormap and normalizer function such that agent state values are mapped to the correct color
        self.color_map = {"Infected": 0.5, "Susceptible": 1.5, "Recovered": 2.5, "Deceased": 3.5}  # values in the middle
        # of the respective range
        states_val = [0, 1, 2, 3, 4]
        colors = ["red", "green", "blue", "black"]
        self.cmap, self.norm = matplotlib.colors.from_levels_and_colors(states_val, colors)

        # Setup the figure and axes...
        self.fig, self.ax = plt.subplots()
        # Then setup FuncAnimation.
        frame_interval = (1/fps)*10**3  # frame interval is in milliseconds
        self.ani = animation.FuncAnimation(self.fig, self.update, interval=frame_interval,
                                          init_func=self.setup_plot, blit=True, repeat=False)

    def setup_plot(self):
        """Initial drawing of the scatter plot."""
        pos, colors = self.next_step()
        x = [c[0] for c in pos]
        y = [c[1] for c in pos]
        self.scat = self.ax.scatter(x, y, c=colors, s=self.a_size, cmap=self.cmap, norm=self.norm)
        # min_x, max_x = -math.ceil(self.height / 2 + 1), math.ceil(self.height / 2 + 1)
        # min_y, max_y = -math.ceil(self.width / 2 + 1), math.ceil(self.width / 2 + 1)
        self.ax.axis([-self.width/100, (self.width+self.width/100), -self.height/100, self.height+self.height/100])
        print("setup successful")
        # For FuncAnimation's sake, we need to return the artist we'll be using
        # Note that it expects a sequence of artists, thus the trailing comma.
        return self.scat,

    def update(self, i):
        """Update the scatter plot."""
        xy, c = self.next_step()

        # Set x and y data...
        self.scat.set_offsets(xy)
        # Set colors..
        self.scat.set_array(c)

        # We need to return the updated artist for FuncAnimation to draw..
        # Note that it expects a sequence of artists, thus the trailing comma.
        return self.scat,

    def next_step(self):
        step_data = self.agent_dataframe.xs(self.curr_step, level="Step")
        if self.curr_step != self.max_step:
            # when last step is reached the function will keep giving the last step data to update()
            # this is a stupid way of stopping the gif without raising exceptions
            self.curr_step += 1
        pos = list(step_data["Position"])
        colors = self.map_states(list(step_data["State"]))
        return np.array(pos).astype(np.float), np.array(colors).astype(np.int)

    def map_states(self, state_array):
        # map an array of states into an array of RGB colors
        output = []
        for agent_state in state_array:
            if agent_state == self.m_states["Susceptible"]:
                # color for susceptible agents
                output.append(self.color_map["Susceptible"])

            elif agent_state == self.m_states["Infected"]:
                # color for infected agents
                output.append(self.color_map["Infected"])

            elif agent_state == self.m_states["Deceased"]:
                # color for deceased agents
                output.append(self.color_map["Deceased"])

            elif agent_state == self.m_states["Recovered"]:
                # color for susceptible agents
                output.append(self.color_map["Recovered"])
            else:
                raise ValueError("Agent has an unrecognizable state value: ", agent_state)
        return output

    def save_animation(self, filename, fps):
        # saves a gif of the animated plot
        print("Saving animated plot to file ", filename)
        writergif = animation.PillowWriter(fps=fps)
        self.ani.save(filename, writer=writergif)
        print("Animated plot saved successfully")


if __name__ == '__main__':
    model_space_height = 500
    model_space_width = 500
    n_steps = 150

    model = EpidemicModel(N_tot=1000, N_inf=5, width=model_space_width, height=model_space_height, inf_chance=0.7,
                          inf_radius=2, inf_duration=30, mortality_rate=0.001, grid_space=False,
                          cont_move_max_d=1, cont_move_min_d=10)
    final_step = 0
    for i in range(n_steps):
        model.step()
        print(f"STEP: {i}, Susceptible: {model.n_susceptible}, Infected: {model.n_infected}, "
              f"Dead: {model.n_dead}, Recovered: {model.n_recovered}")
        if model.n_infected == 0:
            final_step = i
            break
        final_step = i

    agent_data = model.datacollector.get_agent_vars_dataframe()
    # for i in range(n_steps):
    #     step_data = agent_data.xs(i, level="Step")
    # animated plot
    a = AnimatedEpidemicPlot(agent_dataframe=agent_data, height=model_space_height, width=model_space_height,
                             state_int_values=model.states, n_steps=final_step, fps=30, agent_size = 1)
    a.save_animation("10000_inf.gif", 2)
    # plt.show()
