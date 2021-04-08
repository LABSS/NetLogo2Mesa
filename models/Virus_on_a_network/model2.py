from mesa.model import Model
from mesa.agent import Agent
from mesa.time import RandomActivation
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import time
from scipy.spatial import distance
import os
import sys
from tqdm import tqdm
import numpy as np
from mesa.datacollection import DataCollector
from matplotlib.pylab import *
import matplotlib.animation as animation

class VirusModel(Model):

    def __init__(self, number_of_nodes=150, seed=int.from_bytes(os.urandom(4), sys.byteorder)):
        self.seed = seed
        self.tick = 0
        self.random = np.random.default_rng(self.seed)
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
        self.collector = DataCollector(
            model_reporters={
                "infected": lambda x: len([node for node in x.schedule.agents if node.infected]),
                "resistant": lambda x: len([node for node in x.schedule.agents if node.resistant]),
                "susceptible": lambda x: len([node for node in x.schedule.agents if not
                node.infected and not node.resistant])
            })


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
        self.schedule.step()
        self.spread_virus()
        self.do_virus_check()
        self.collector.collect(self)
        self.tick += 1

    def spread_virus(self):
        for inf_node in self.random.permutation([node for node in self.schedule.agents if
                                             node.infected]):

            for node in self.random.permutation([node for node in inf_node.neighbors if
                                              not node.resistant]):

                if self.random.uniform(0,100) < self.virus_spread_chance:
                    node.infected = True

    def do_virus_check(self):
        for inf_node in self.random.permutation([node for node in self.schedule.agents if
                                             node.infected and node.virus_check_timer == 0]):
            if self.random.uniform(0,100) < self.recovery_chance:
                if self.random.uniform(0,100) < self.gain_resistence_chance:
                    inf_node.resistant = True
                    inf_node.infected = False
                else:
                    inf_node.infected = False

    def setup_spatially_clustered_network(self):
        num_links = (self.average_node_degree * self.number_of_nodes) / 2
        while sum([len(node.neighbors) for node in self.schedule.agents]) / 2 < num_links:
            from_node = self.random.choice(self.schedule.agents)
            to_node = min([node for node in self.schedule.agents if node != from_node and node not in from_node.neighbors],
                            key=lambda node: from_node.get_distance(node))
            if to_node:
                from_node.create_link_with(to_node)

    def run(self, n_step=150, n_nodes=None, verbose=True):
        if n_nodes is not None:
            self.number_of_nodes = n_nodes
        self.setup()
        pbar = tqdm(np.arange(1, n_step + 1)) if verbose else range(1, n_step + 1)
        for _tick in pbar:
            self.step()
            if verbose:
                pbar.set_description("tick: %s" % _tick)
                pbar.set_postfix({'infected': len([node for node in self.schedule.agents if
                                                     node.infected])})

    def show_space(self):
        fig, ax = plt.subplots()
        for agent in self.schedule.agents:
            ax.scatter(agent.x, agent.y, c= "tab:red" if agent.infected else (
                "tab:green" if agent.resistant else "tab:grey"))
            ax.annotate(agent.unique_id, (agent.x + 0.2, agent.y + 0.2), color="tab:purple")
            if agent.neighbors:
                for neighbor in agent.neighbors:
                    plt.plot((agent.x, neighbor.x),
                             (agent.y, neighbor.y), "--",
                             alpha=0.2,
                             color="tab:orange",
                             linewidth=1)
        plt.show()
        
    def dump_data(self, path, name):
        self.collector.get_model_vars_dataframe().to_csv(os.path.join(path, name + ".csv"))
        print("Saved!")


    def updateData(self, curr, infected, resistant, susceptible, tick):
        self.step()

        infected.append(len([node for node in self.schedule.agents if node.infected]))
        resistant.append(len([node for node in self.schedule.agents if node.resistant]))
        susceptible.append(len([node for node in self.schedule.agents
                               if not node.infected and not node.resistant]))
        tick.append(model.tick)

        for ax in (self.ax1, self.ax2, self.ax3):
            ax.clear()

        self.ax1.set_title("tick: " + str(self.tick))
        for agent in self.schedule.agents:
            self.ax1.scatter(agent.x, agent.y, c="tab:red" if agent.infected else (
                "tab:green" if agent.resistant else "tab:grey"))
            self.ax1.annotate(agent.unique_id, (agent.x + 0.2, agent.y + 0.2), color="tab:purple")
            if agent.neighbors:
                for neighbor in agent.neighbors:
                    self.ax1.plot((agent.x, neighbor.x),
                             (agent.y, neighbor.y), "--",
                             alpha=0.2,
                             color="tab:orange",
                             linewidth=0.5)

        self.ax2.set_title("Infected")
        self.ax3.set_title("Resistant")
        self.ax4.set_title("Susceptible")
        self.ax2.plot(tick, infected, c="red")
        self.ax3.plot(tick, resistant, c="green")
        self.ax4.plot(tick, susceptible, c="gray")



    def visulize_run(self):
        self.setup()
        self.fig = plt.figure()
        self.ax1 = self.fig.add_subplot(1, 2, 1)
        self.ax2 = self.fig.add_subplot(3, 2, 2)
        self.ax3 = self.fig.add_subplot(3, 2, 4)
        self.ax4 = self.fig.add_subplot(3, 2, 6)
        infected = list()
        resistant = list()
        susceptible = list()
        tick = list()
        self.simulation = animation.FuncAnimation(self.fig,
                                                  self.updateData,
                                                  fargs=(infected, resistant, susceptible, tick),
                                                  interval=1000,
                                                  repeat=False)
        self.fig.show()


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
        self.virus_check_timer += 1
        if self.virus_check_timer >= self.model.virus_check_frequency:
            self.virus_check_timer = 0

if __name__ == "__main__":
    model = VirusModel()
    model.number_of_nodes = 150
    model.initial_outbreak_size = 10
    # model.setup()
    model.visulize_run()

    # def visulize_run():
    #     model.setup()
    #     fig = plt.figure()
    #     ax1 = fig.add_subplot(1, 2, 1)
    #     ax2 = fig.add_subplot(2, 2, 2)
    #     ax3 = fig.add_subplot(2, 2, 4)
    #     def updateData(curr, infected, resistant, tick):
    #         model.step()
    #         infected.append(len([node for node in model.schedule.agents if node.infected]))
    #         resistant.append(len([node for node in model.schedule.agents if node.resistant]))
    #         tick.append(model.tick)
    #         for ax in (ax1, ax2, ax3):
    #             ax.clear()
    #
    #         ax1.set_title("tick: " + str(model.tick))
    #         for agent in model.schedule.agents:
    #             ax1.scatter(agent.x, agent.y, c="tab:red" if agent.infected else (
    #                 "tab:green" if agent.resistant else "tab:grey"))
    #             ax1.annotate(agent.unique_id, (agent.x + 0.2, agent.y + 0.2), color="tab:purple")
    #             if agent.neighbors:
    #                 for neighbor in agent.neighbors:
    #                     ax1.plot((agent.x, neighbor.x),
    #                              (agent.y, neighbor.y), "--",
    #                              alpha=0.2,
    #                              color="tab:orange",
    #                              linewidth=0.5)
    #         ax2.plot(tick, infected, c = "red")
    #         ax2.set_title("Infected")
    #         ax3.set_title("Resistant")
    #         ax3.plot(tick, resistant, c = "red")
    #         plt.xticks(ha='right')
    #     infected = list()
    #     resistant = list()
    #     tick = list()
    #     simulation = animation.FuncAnimation(fig, updateData,
    #                                          fargs=(infected, resistant, tick),
    #                                          interval=1000,
    #                                          repeat=False)
    #     plt.show()
    #
    # # model.run(n_nodes=100, n_step=10000)

