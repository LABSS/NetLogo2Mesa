from mesa.model import Model
from mesa.agent import Agent
from mesa.time import RandomActivation
from numpy.random import default_rng
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
import time


class VirusModel(Model):

    def __init__(self, number_of_nodes=150, seed=int(time.time() % 60)):
        super().__init__(seed=seed)
        self.seed = seed
        self.tick = 0
        self.rng = default_rng(self.seed)
        self.schedule = RandomActivation(self)
        self.space_width = 41
        self.space_height = 41
        self.number_of_nodes = number_of_nodes
        self.gain_resistence_chance = 5.0
        self.recovery_chance = 5.0
        self.virus_spread_chance: 2.5
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

    def show_space(self):
        x = [agent.x for agent in self.schedule.agents]
        y = [agent.y for agent in self.schedule.agents]
        labels = [agent.unique_id for agent in self.schedule.agents]
        fig, ax = plt.subplots()
        ax.scatter(x, y)
        for i, txt in enumerate(labels):
            ax.annotate(txt, (x[i]+0.1, y[i]+0.1), color="red")
        plt.show()




class Node(Agent):

    def __init__(self, model, unique_id):
        super().__init__(unique_id, model)
        self.model = model
        self.unique_id = unique_id
        self.x = self.model.rng.integers(0,self.model.space_width)
        self.y = self.model.rng.integers(0,self.model.space_height)
        self.infected = False
        self.resistant = False
        self.virus_check_timer = self.model.rng.integers(0, self.model.virus_check_frequency)


    def __repr__(self):
        return "Node: " + str(self.unique_id)


if __name__ == "__main__":
    model = VirusModel()
    model.setup()
    model.show_space()
