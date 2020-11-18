from mesa import Model, Agent
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from scipy.spatial import distance
import numpy as np
import sys
from tqdm import tqdm
import time


class VirusModel(Model):

    def __init__(self):
        self.schedule = RandomActivation(self)
        self.grid = MultiGrid(41, 41, False)
        self.tick = 0

        #From graphical interface
        self.number_of_nodes = 1000
        self.average_node_degree = 6
        self.initial_outbreak_size = 3
        self.virus_spread_chance = 3
        self.virus_check_frequency = 1
        self.recovery_chance = 5.0
        self.gain_resistance_chance = 5.0

    def run(self, n_nodes: int = 100, n_tick: int = 1500):
        self.setup(n_nodes)
        for i in tqdm(range(n_tick)):
            self.step()


    def setup_nodes(self):
        for i in range(self.number_of_nodes):
            new_node = Node(i ,self)
            self.schedule.add(new_node)
            # Add the agent to a random grid cell
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            new_node.position = (x,y)
            self.grid.place_agent(new_node, (x, y))
            # We do not need become-susceptible
            # and also to set the virus time frequency


    def setup_spatially_clustered_network(self):
        num_links = (self.average_node_degree * self.number_of_nodes)
        while np.sum([len(node.neighbors) for node in self.schedule.agents]) < num_links:
            alter = self.random.choice(self.schedule.agents)
            choice = sorted([ego for ego in self.schedule.agents if ego != alter and ego not in alter.neighbors],
                            key=lambda x: self.get_distance(alter,x))[0]
            if choice:
                alter.create_link_with(choice)


    def setup(self, n_nodes):
        self.number_of_nodes = n_nodes
        self.setup_nodes()
        self.setup_spatially_clustered_network()
        for agent in self.random.choices(self.schedule.agents, k=self.initial_outbreak_size):
            agent.become_infected()

    @staticmethod
    def get_distance(alter, ego):
        return distance.euclidean(alter.position, ego.position)

    def step(self):
        # if all([not agent.infected for agent in self.schedule.agents]):
        #     sys.exit("Immunity reached in " + str(self.tick) + str(" ticks"))
        for agent in self.schedule.agents:
            agent.virus_check_timer += 1
            if agent.virus_check_timer >= self.virus_check_frequency:
                agent.virus_check_timer = 0

        for agent in self.schedule.agent_buffer(shuffled=True):
            if agent.infected:
                for neighbor in agent.neighbors:
                    if not neighbor.resistant and self.random.uniform(1,100) < self.virus_spread_chance:
                        neighbor.become_infected()
        self.schedule.step()


class Node(Agent):

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.neighbors = set()
        self.position = 0
        self.infected = False  # if true, the turtle is infectious
        self.resistant = False  # if true, the turtle can't be infected
        self.virus_check_timer = self.model.random.uniform(1, self.model.virus_check_frequency)  # number of ticks since this turtle's last virus-check


    def __repr__(self):
        return "Node: " + str(self.unique_id)


    def create_link_with(self, ego):
        self.neighbors.add(ego)
        ego.neighbors.add(self)

    def become_infected(self):
        self.infected = True
        self.resistant = False

    def become_resistant(self):
        self.infected = False
        self.resistant = True

    def become_susceptible(self):
        self.infected = False
        self.resistant = False

    def step(self):
        if self.virus_check_timer == 0 and self.infected:
            if self.model.random.uniform(1,100) < self.model.recovery_chance:
                if self.model.random.uniform(1,100) < self.model.gain_resistance_chance:
                    self.become_resistant()
                else:
                    self.become_susceptible()

def plot_grid():
    import matplotlib
    matplotlib.use('Qt5Agg')
    import matplotlib.pyplot as plt
    x = [agent.position[0] for agent in model.schedule.agents]
    y = [agent.position[1] for agent in model.schedule.agents]
    labels = [agent.unique_id for agent in model.schedule.agents]
    # plt.show()
    fig, ax = plt.subplots()
    ax.scatter(x, y)
    for i, txt in enumerate(labels):
        ax.annotate(txt, (x[i], y[i]))
    for agent in model.schedule.agents:
        if agent.neighbors:
            for neighbor in agent.neighbors:
                plt.plot((agent.position[0], neighbor.position[0]),
                         (agent.position[1], neighbor.position[1]), "-ro")
    plt.show()


model = VirusModel()
model.run()

plot_grid()




