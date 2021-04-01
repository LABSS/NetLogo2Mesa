from mesa.model import Model
from mesa.agent import Agent
from mesa.time import RandomActivation
from numpy.random import default_rng
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
import time
from scipy.spatial import distance
import os
import sys

class VirusModel(Model):

    def __init__(self, number_of_nodes=150, seed=int.from_bytes(os.urandom(4), sys.byteorder)):
        self.seed = seed
        self.tick = 0
        self.random = default_rng(self.seed)
        self.schedule = RandomActivation(self)
        self.space_width = 41
        self.space_height = 41
        self.number_of_nodes = number_of_nodes
        self.gain_resistence_chance = 5.0
        self.recovery_chance = 5.0
        self.virus_spread_chance= 2.5
        self.virus_check_frequency = 1
        self.initial_outbreak_size = 3
        self.average_node_degree = 6

    def __repr__(self):
        return "Virus Model"


    def setup_nodes(self):
        for id in range(self.number_of_nodes):
            new_node = Node(model=self, unique_id=id)
            self.schedule.add(new_node)

    def setup(self):
        self.setup_nodes()
        self.setup_spatially_clustered_network()
        for agent in self.random.choice(self.schedule.agents, self.initial_outbreak_size):
            agent.infected = True

    def step(self):
        if not any([agent.infected for agent in self.schedule.agents]):
            sys.exit()


    def setup_spatially_clustered_network(self):
        num_links = (self.average_node_degree * self.number_of_nodes) / 2
        while sum([len(node.neighbors) for node in self.schedule.agents]) / 2 < num_links:
            from_node = self.random.choice(self.schedule.agents)
            to_node = min([node for node in self.schedule.agents if node != from_node and node not in from_node.neighbors],
                            key=lambda node: from_node.get_distance(node))
            if to_node:
                from_node.create_link_with(to_node)


    def show_space(self):
        fig, ax = plt.subplots()
        for agent in self.schedule.agents:
            ax.scatter(agent.x, agent.y, c="tab:red" if agent.infected else "tab:grey")
            ax.annotate(agent.unique_id, (agent.x + 0.2, agent.y + 0.2), color="tab:purple")
            if agent.neighbors:
                for neighbor in agent.neighbors:
                    plt.plot((agent.x, neighbor.x),
                             (agent.y, neighbor.y), "--",
                             alpha=0.2,
                             color="tab:orange",
                             linewidth=1)
        plt.show()

    def step(self):
        self.schedule.step()


class Node(Agent):

    def __init__(self, model, unique_id):
        super().__init__(unique_id, model)
        self.neighbors = set()
        self.model = model
        self.unique_id = unique_id
        self.x = self.model.random.integers(0,self.model.space_width)
        self.y = self.model.random.integers(0,self.model.space_height)
        self.infected = False
        self.resistant = False
        self.virus_check_timer = self.model.random.integers(0, self.model.virus_check_frequency)


    def __repr__(self):
        return "Node: " + str(self.unique_id)

    def __hash__(self):
        return self.unique_id


    def create_link_with(self, ego):
        self.neighbors.add(ego)
        ego.neighbors.add(self)


    def get_distance(self, node):
        return distance.euclidean((self.x,self.y), (node.x, node.y))

    def step(self):
        print(self.__repr__())

if __name__ == "__main__":
    model = VirusModel()
    model.setup()
    model.show_space()
