# How to convert an agent based model from Netlogo to Python.

...and other stuff that will help you avoid headaches. 

In this little guide we will take a model written in [Netlogo](https://github.com/NetLogo/NetLogo) and we will transform it into a Python model. We will take the [NetLogo Virus on a Network model](https://ccl.northwestern.edu/netlogo/models/VirusonaNetwork) developed by Stonedahl and Wilensky in 2008, as example written in Netlogo. The model demonstrates the spread of a virus within a network, composed of nodes that can assume 3 states: **S**usceptible, **I**nfected, or **R**esistant. In the academic literature models of this type are called **SIR** models. Infected nodes can transmit the virus to their neighbors, susceptible nodes can be infected and resistant nodes cannot contract the virus. What happens at each temporal step we will see later. For now it is important to emphasize that in almost every Agent based model (from now ABM), including this one, there are two main phases: the setup, where we create our synthetic environment and the runtime, where the agents interact with each other. These two phases are clearly separable from each other even on an abstract level. 

###### What tools will we use?

As much as possible, there are endless ways to write a procedure in Python in this guide we will try to cover some of them. We will use the following packages: 

- [Mesa](https://github.com/projectmesa/mesa): an agent-based modeling framework in Python
- [NetworkX](https://networkx.org/): a Python package for the creation, manipulation, and study of the structure, dynamics, and functions of complex networks.

------

##### Step 1, Create the blueprints

At a high level of abstraction the model we are going to create can be defined as a single object, a class. This object has its **attributes**, such as the number of agents or nodes in our case, and its **methods**, the procedures specific to our model such as the algorithm that generates the network. So let's start by creating our model. In python each object has its own `__init__` method, this method is called every time a new VirusModel object is instantiated, it is good practice to define here all the attributes of our model. ( here is where we define all the variables that in Netlogo are under the name [globals](http://ccl.northwestern.edu/netlogo/docs/dict/globals.html)) The first attribute we define is `VirusModel.number_of_nodes` which simply represents the number of nodes. We don't want a fixed number of nodes so we insert as parameter of the `__init__` the keyword `number_of_nodes` specify the type `int`, and give it a default value (150). In this way every time a new Model object is instantiated we can define a number of nodes, if we don't do it `VirusModel.number_of_nodes` will be equal to default value. Now it's time to introduce the global attributes, including those that in Netlogo are stored in the graphical interface, and give them a default value. These are: gain-resistance-chance, recovery-chance, virus-spread-chance, virus-check-frequency, initial-outbreak-size, average-node-degree. We want a model that has style, so we name our model object using the special `__repr__` method, every time we print an instance of the VirusModel this method is called. 

We have our simple model, now it is time to create nodes, the agents of our model. So we create the Node class and define the special `__init__` method, here we will insert the attributes of each agent. The attributes of agents in a Netlogo model are contained within the primitive turtle-related `<breeds>-own`. In the example model nodes have these properties: 

```
turtles-own
[
  infected?           ;; if true, the turtle is infectious
  resistant?          ;; if true, the turtle can't be infected
  virus-check-timer   ;; number of ticks since this turtle's last virus-check
]
```

We insert these attributes inside the `__init__` method and give it a default value. At this point, however, we want every single node to be able to access the attributes of the model. To do this, we add a new parameter to the `__init__` method, `model`, and create a `Node.model` attribute. Through this attribute it will be possible to access the properties of the already instantiated model. We also want each Node to stand out from the others. For this reason we pass to the `__init__` another parameter, `Node.unique_id`, a number that describes the single node. And since we have style, we give a name to each Node, something like: " Node: 1" could be fine. Our blueprint is almost ready. 

```python
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


class Node():

    def __init__(self, model: VirusModel, unique_id: int) -> None:
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
    
```

##### Step 2, Enhance Core classes

Before we go to write the procedures of our model and our agents, we must have a machine that has the necessary functionality. The mesa package gives us some interesting tools to enhance our model, which otherwise were to be implemented from scratch. The [two basic mesa modules](https://mesa.readthedocs.io/en/master/apis/init.html) are mesa.agent and mesa.model, these modules give us the basic mesa.model.Model and mesa.agent.Agent classes. These two classes, have their methods and attributes that we want to implement within our VirusModel (our model) and Node (our agents). In Python this mechanism is implementable through inheritance, when we create a new class, passing as parameter an existing class, the new class will inherit all methods and attributes. On an abstract level you can imagine that VirusModel is the child of the mesa.model.Model class. In order to better understand how this mechanism works I suggest to have a look inside [mesa.agent](https://github.com/projectmesa/mesa/blob/master/mesa/agent.py) and [mesa.model](https://github.com/projectmesa/mesa/blob/master/mesa/model.py).

###### Random

The mesa.model.Model class gives us a fundamental functionality for an ABM: a random generator. When we instantiate a VriusModel object the pyhton interpreter executes the special `__new__` method of the mesa.model.Model class, this method instantiates for us a [random.Random](https://docs.python.org/3/library/random.html) object, and since the child class inherits all the attributes of the parent class, we can access this attribute from the VirusModel object. You can test this generator by simply instantiating a VirusModel object, accessing the random attribute and then the random.Random.random() method, this method will return a random float between 0 and 1.

```python
if __name__ == "__main__":
    model = VirusModel()
    print(model.random.random())
```

The built-in random module offers many options and for a basic model like our example should be enough. 





```python
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
```







