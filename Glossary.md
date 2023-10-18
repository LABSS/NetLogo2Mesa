## Glossary NetLogo2Python

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



### Big three instructions ask, with, of:

1. *ask*: "The specified agent or agentset runs the given commands."  [source](http://ccl.northwestern.edu/netlogo/docs/dict/ask.html)

```
ask patches [ set pcolor red ]
```

```python
for agent in model.random.permuted(model.agentset):
	agent.color = "red"
    print(agent, agent.color)
```

2. *of*: "For an agent, reports the value of the reporter for that agent (turtle or patch). For an agentset, reports a list that contains the value of the reporter for each agent in the agentset (in random order)." [source](http://ccl.northwestern.edu/netlogo/docs/dict/of.html)

```
show [pxcor] of patch 3 5
```

```python
print(model.agentset[1].color)
print(model.random.permuted([agent.color for agent in model.agentset]))
```

3.  *with*: "Reports a new agentset containing only those agents that reported true, the agents satisfying the given condition." [source](http://ccl.northwestern.edu/netlogo/docs/dict/with.html)

```netlogo
show count patches with [pcolor = red]
```

```python
print(len([agent for agent in model.agentset if agent.color == "red"]))
```

### Extractions

1. *n-of*: "Reports an agentset of size size randomly chosen from the input set, with no repeats." [source](http://ccl.northwestern.edu/netlogo/docs/dict/n-of.html)

```
ask n-of 50 patches [ set pcolor green ]
```

```python
for agent in model.random.choice(model.agentset, 10, replace=False):
	agent.color = "green"
	print(agent, agent.color)
```

