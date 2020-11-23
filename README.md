# How to convert an agent based model from Netlogo to Python.

...and other stuff that will help you avoid headaches. 

In this little guide we will take a model written in [Netlogo](https://github.com/NetLogo/NetLogo) and we will transform it into a Python model. We will take the [NetLogo Virus on a Network model](https://ccl.northwestern.edu/netlogo/models/VirusonaNetwork) developed by Stonedahl and Wilensky in 2008, as example written in Netlogo. The model demonstrates the spread of a virus within a network, composed of nodes that can assume 3 states: **S**usceptible, **I**nfected, or **R**esistant. In the academic literature models of this type are called **SIR** models. Infected nodes can transmit the virus to their neighbors, susceptible nodes can be infected and resistant nodes cannot contract the virus. What happens at each temporal step we will see later. For now it is important to emphasize that in almost every Agent based model (from now ABM), including this one, there are two main phases: the setup, where we create our synthetic environment and the runtime, where the agents interact with each other. These two phases are clearly separable from each other even on an abstract level. 

###### What tools will we use?

As much as possible, there are endless ways to write a procedure in Python in this guide we will try to cover some of them. We will use the following packages: 

- [Mesa](https://github.com/projectmesa/mesa): an agent-based modeling framework in Python
- [NetworkX](https://networkx.org/): a Python package for the creation, manipulation, and study of the structure, dynamics, and functions of complex networks.

------

##### Step 1, Create the blueprints

At a high level of abstraction the model we are going to create can be defined as a single object, a class. This object has its **attributes**, such as the number of agents or nodes in our case, and its **methods**, the procedures specific to our model such as the algorithm that generates the network. So let's start by creating our model. In python each object has its own `__init__` method, this method is called every time a new VirusModel object is instantiated, it is good practice to define here all the attributes of our model. ( here is where we define all the variables that in Netlogo are under the name [globals](http://ccl.northwestern.edu/netlogo/docs/dict/globals.html)) The first attribute we define is `VirusModel.number_of_nodes` which simply represents the number of nodes. We don't want a fixed number of nodes so we insert as parameter of the `__init__` the keyword `number_of_nodes` specify the type `int`, and give it a default value (150). In this way every time a new Model object is instantiated we can define a number of nodes, if we don't do it `VirusModel.number_of_nodes` will be equal to default value. Now it's time to introduce the global attributes, including those that in Netlogo are stored in the graphical interface, and give them a default value. These are: gain-resistance-chance, recovery-chance, virus-spread-chance, virus-check-frequency, initial-outbreak-size, average-node-degree. Now we must define the size of the graphic space, in netlogo this information is contained in the Interface section or by opening the .nlogo file with a text editor in the `GRAPHICS-WINDOW` section. From here we can see that the width of the space goes from -20 to 20 and the height from -20 to 20, in python for simplicity we will say that the `ViruslModel.space_width = 40` and `ViruslModel.space_heigh = 40`. So our space will go from 0 to 40 in the x-axis and y-axis. We want a model that has style, so we name our model object using the special `__repr__` method, every time we print an instance of the VirusModel this method is called. 

We have our simple model, now it is time to create nodes, the agents of our model. So we create the Node class and define the special `__init__` method, here we will insert the attributes of each agent. The attributes of agents in a Netlogo model are contained within the primitive turtle-related `<breeds>-own`. In the example model nodes have these properties: 

```
turtles-own
[
  infected?           ;; if true, the turtle is infectious
  resistant?          ;; if true, the turtle can't be infected
  virus-check-timer   ;; number of ticks since this turtle's last virus-check
]
```

We insert these attributes inside the `__init__` method and give it a default value. At this point, however, we want every single node to be able to access the attributes of the model. To do this, we add a new parameter to the `__init__` method, `model`, and create a `Node.model` attribute. Through this attribute it will be possible to access the properties of the already instantiated model. We also want each Node to stand out from the others. For this reason we pass to the `__init__` another parameter, `Node.unique_id`, a number that describes the single node. Each node will have its position on a plane, defined with two x and y coordinates, for now we will give it 0 as default parameter. And since we have style, we give a name to each Node, something like: " Node: 1" could be fine. Our blueprint is almost ready. 

```python
class VirusModel(Model):

    def __init__(self, number_of_nodes = 150):
        self.number_of_nodes = number_of_nodes
        self.space_width = 40
        self.space_height = 40
        self.gain_resistence_chance = 5.0
        self.recovery_chance = 5.0
        self.virus_spread_chance: 2.5
        self.virus_check_frequency = 1
        self.initial_outbreak_size = 3
        self.average_node_degree = 6


    def __repr__(self):
        return "Virus Model"


class Node():

    def __init__(self, model, unique_id):
        self.model = model
        self.unique_id = unique_id
        self.x = 0
        self.y = 0
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

Before we go to write the procedures of our model and our agents, we must have a machine that has the necessary functionality. The mesa package gives us some interesting tools to enhance our model, which otherwise were to be implemented from scratch. The [two basic mesa modules](https://mesa.readthedocs.io/en/master/apis/init.html) are mesa.agent and mesa.model, these modules give us the basic mesa.model.Model and mesa.agent.Agent classes. These two classes, have their methods and attributes that we want to implement within our VirusModel (our model) and Node (our agents). In Python this mechanism is implementable through inheritance, when we create a new class, passing as parameter an existing class, the new class will inherit all methods and attributes. 

```python
from mesa.model import Model
from mesa.agent import Agent

class VirusModel(Model):
	def __init__(self, number_of_nodes = 150, seed):
        super().__init__(seed=seed)

        
class Node(Agent):
    def __init__(self, model, unique_id):
        super().__init__(unique_id, model)
```

The `super().__init__(parameters)` function also allows you to inherit the parameters of the superclass `__init__`. On an abstract level you can imagine that VirusModel is the child of the mesa.model.Model class. In order to better understand how this mechanism works I suggest to have a look inside [mesa.agent](https://github.com/projectmesa/mesa/blob/master/mesa/agent.py) and [mesa.model](https://github.com/projectmesa/mesa/blob/master/mesa/model.py).

###### Random

The mesa.model.Model class gives us a fundamental functionality for an ABM: a random generator. When we instantiate a VriusModel object the pyhton interpreter executes the special `__new__` method of the mesa.model.Model class, this method instantiates for us a [random.Random](https://docs.python.org/3/library/random.html) object, and since the child class inherits all the attributes of the parent class, we can access this attribute from the VirusModel object. You can test this generator by simply instantiating a VirusModel object, accessing the random attribute and then the random.Random.random() method, this method will return a random float between 0 and 1.

```python
if __name__ == "__main__":
    model = VirusModel()
    print(model.random.random())
```

The built-in random module offers many options and for a basic model like our example should be enough. But if you want a more complete random generator you have to use [numpy.random.default_rng](https://numpy.org/doc/stable/reference/random/generator.html#numpy.random.default_rng). How do we implement it? Easy, first of all we import the module `from numpy.random import default_rng`, then we add an attribute to the VirusModel class `self.rng = default_rng()` this will be our random generator. At this point, however, it should be noted that we have two random generators, this in theory is not good practice, but if it is necessary we have no other choice. In addition to this, some modules of the mesa package such as mesa.time (which we will see later) work through the random.Random instance generated by the mesa.model.Model class. This is a problem because the two generators (random and numpy.random) have two different seeds. We need to make sure that the generators receive the same seed so it will be possible to create deterministic simulations. To do this we give a default parameter to the seed in the VirusModel class, we import the time module and take the time in seconds, this will be our seed that we will give to both instances (random and numpy.random), we also create a seed attribute so that it is externally accessible. If we want to reproduce two identical simulations we will just use the same seed, moreover if we do not provide a seed our model will generate a pseudo-random seed that we can access to replicate the simulation. Fantastic, isn't it?

###### Scheduler

When we create our Nodes we would need a place to store them, to solve this problem the mesa package offers us the mesa.time module. This module offers us 3 classes that we have to choose according to our modeling needs, we will not go into detail as they are perfectly explained on the [mesa.time module documentation.](https://mesa.readthedocs.io/en/master/apis/time.html) For our model we will use the class mesa.time.RandomActivation, the scheduler of this class activates agents randomly for each step, in short it clones the [ask primitive of Netlogo](http://ccl.northwestern.edu/netlogo/docs/dict/ask.html). Let's start implementing the scheduler, the first step is to import RandomActivation from the mesa.time module. 

```
from mesa.time import RandomActivation
```

Then we create a new VirusModel attribute that will be an instance of the RandomActivation class.

```
self.schedule = RandomActivation(self)
```

This object will manage the list of our nodes, every time we create a new node we will add it to self.schedule with the `self.schedule.add(Node)` method, in the same way every time we want to delete an agent we will extract it with the `self.schedule.remove(Node)` method.

```python
from mesa.model import Model
from mesa.agent import Agent
from mesa.time import RandomActivation
from numpy.random import default_rng
import time


class VirusModel(Model):

    def __init__(self, number_of_nodes = 150, seed = int(time.time() % 60)):
        super().__init__(seed=seed)
        self.seed = seed
        self.tick = 0
        self.space_width = 40
        self.space_height = 40
        self.rng = default_rng(self.seed)
        self.schedule = RandomActivation(self)
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

    def __init__(self, model, unique_id):
        super().__init__(unique_id, model)
        self.model = model
        self.unique_id = unique_id
        self.x = 0
        self.y = 0
        self.infected = False
        self.resistant = False
        self.virus_check_timer = 0


    def __repr__(self):
        return "Node: " + str(self.unique_id)


if __name__ == "__main__":
    model = VirusModel()
    node = Node(model, 1)
```



##### Step 3, Create the setup

We have our blueprint now is the time to implement the procedures that organize the initial status of the model, simply everything in Netlogo is included in the "setup" procedure. This part consists of the following procedures that we will analyze and translate into python one by one:

```Netlogo
to setup
  clear-all
  setup-nodes
  setup-spatially-clustered-network
  ask n-of initial-outbreak-size turtles
    [ become-infected ]
  ask links [ set color white ]
  reset-ticks
end
```

###### setup-nodes

This procedure defines a default form for all agents, a circle, then generates as many agents as required by the number-of-nodes parameter and assigns to each one an x value and a random y value on a plane activates the become-susceptible procedure and assigns a random value to the virus-check-timer attribute.

```
to setup-nodes
  set-default-shape turtles "circle"
  create-turtles number-of-nodes
  [
    setxy (random-xcor * 0.95) (random-ycor * 0.95)
    become-susceptible
    set virus-check-timer random virus-check-frequency
  ]
end
```

Let's start the translation, first of all, for now we will not deal with the instructions related to the visualization ( `set-default-shape turtles "circle"`) then let's go directly to the node generation.  In netlogo the primitive [create-turtles number [ commands ]](http://ccl.northwestern.edu/netlogo/docs/dict/create-turtles.html) does nothing but create number agents and immediately execute the commands, in python we can emulate this behavior with a simple for cycle. Inside the model we define a new setup-nodes method, we implement a simple for loop using the built-in range(number_of_nodes) function so the loop will do as many iterations as number_of_nodes. For each cycle we instantiate a new node, pass it the model and iteration number (this parameter will assign a unique_id to the single node based on the iteration number) as parameters and add the node to the scheduler. At this point within the for cycle we have to make each node execute the following instructions:

1. `setxy (random-xcor * 0.95) (random-ycor * 0.95)`

