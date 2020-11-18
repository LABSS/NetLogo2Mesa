from mesa.model import Model
from mesa.agent import Agent


class VirusModel(Model):

    def __init__(self, number_of_nodes: int = 150) -> None:
        self.number_of_nodes = number_of_nodes
        self.gain_resistence_chance = 5.0
        self.recovery_chance = 5.0
        self.virus_spread_chance: 2.5
        self.virus_check_frequency = 1
        self.initial_outbreak_size = 3
        self.average_node_degree = 6


    def __repr__(self):
        return "Virus Model"


class Node(Agent):

    def __init__(self, model: VirusModel, unique_id: int) -> None:
        super().__init__(unique_id, model)
        self.model = model
        self.unique_id = unique_id
        self.infected = False
        self.resistant = False
        self.virus_check_timer = 0


    def __repr__(self):
        return "Node: " + str(self.unique_id)


if __name__ == "__main__":
    model = VirusModel()
    node = Node(model, 1)



    # class Model:
    #     def __init__(self):
    #         self.model_variable = 0
    #
    # class MyModel(Model):
    #     def __init__(self):
    #         super().__init__()
    #         self.my_model_variable = 0
    #
    # class Foo:
    #     def __init__(self, model: Model):
    #         self.model = model
    #         print(self.model.model_variable)
    #         print(self.model.my_model_variable)
    #
    # mymodel = MyModel()
    # foo = Foo(mymodel)