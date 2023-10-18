```python
from numpy.random import default_rng


class Model:
    def __init__(self):
        self.agentset = list()
        self.random = default_rng()

    def create_agents(self):
        for i in range(30):
            new_agent = Agent(unique_id=i, color="red" if i % 2 == 0 else "blue")
            self.agentset.append(new_agent)


class Agent:
    def __init__(self, unique_id, color):
        self.unique_id = unique_id
        self.color = color

    def __repr__(self):
        return "Agent: " + str(self.unique_id)


if __name__ == '__main__':
    model = Model()
    model.create_agents()
```


1. *with*: reports a new agentset containing only those agents that reported true, the agents satisfying the given condition.
    """
    show count patches with [pcolor = red]
    """
    print(len([agent for agent in model.agentset if agent.color == "red"]))

    """
    of:
    For an agent, reports the value of the reporter for that agent. For an agentset, reports a 
    list that contains the value of the reporter for each agent in the 
    agentset (in random order).

    show [pxcor] of patch 3 5
    """

    print(model.agentset[1].color)
    print(model.random.permuted([agent.color for agent in model.agentset]))

    """
    ask:
    The specified agent or agentset runs the given commands. Because agentset members 
    are always read in a random order, when ask is used with an agentset each agent 
    will take its turn in a random order.

    ask patches [ set pcolor red ]
    """
    for agent in model.random.permuted(model.agentset):
        agent.color = "red"
        print(agent, agent.color)

    """
    n-of:
    reports an agentset of size size randomly chosen from the input set, with no repeats.

    ask n-of 50 patches [ set pcolor green ]
    """
    for agent in model.random.choice(model.agentset, 10, replace=False):
        agent.color = "green"
        print(agent, agent.color)

    #or

    new_agentset = model.random.choice(model.agentset, 10, replace=False)

    #or one-of

    random_agent = model.random.choice(model.agentset, 1, replace=False)

    """
    count:
    Reports the number of agents in the given agentset.

    show count turtles
    """

    print(len(model.agentset))

