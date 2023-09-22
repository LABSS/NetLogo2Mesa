# How to convert a model from NetLogo to mesa

## Create conversion patterns

### conversion patterns for the big three instructions: ask, of, with.

Let us assume that the agents are represented by the agentset `turtles` in NetLogo and by the list 'agents' in Python.


1. *ask* pattern: ```ask turtles [ believe ]``` becomes:
```
for x in self.schedule.agents: x.believe()
```

For the next patterns we use *list comprehension* (https://en.wikipedia.org/wiki/List_comprehension).


1. *of* pattern: ```let a [ shell ] of turtles``` becomes:
```
[x.shell for x in self.schedule.agents]
```

1. usage of *with* will depend on the main form (ask, of) and will just turn in a ```if``` construct, in one of the two following ways:
```
#ask turtles with [ miscredent? ] [ believe ]
for x in self.schedule.agents if x.miscredent: x.believe()

#let a [ shell ] of turtles with [ into-soup? ]
a = [x.shell for x in self.schedule.agents if x.into-soup]

### extractions

1. ```n-of```

```
# let a n-of 10 turtles
import random
a = random.sample(a, 10)
# 6.1.1 style
a = a if len(a) < 10 else random.sample(a,10)
```

### conversion of advanced structures

There are some patterns I use a lot. Random extraction is one of them; in NetLogo, there's the really useful ```rnd:weighted_one_of``` construct that will appear again and again. A possible conversion pattern is as follows:

```
#let chosen rnd:weighted-one-of turtles [ holiness-weight ]
import numpy as np
chosen = np.random.choice(self.schedule.agents,
    p = [x.holiness_weight for x in self.schedule.agents],
	size.self.schedule.agents=1,
	replace=False)[0]
```

Note that the ```replace=False``` makes little sense here, but helps when turning this into a pattern for ```rnd:weighted_n_of```, which is left as an exercise for the reader.


