class Foo:
    def __init__(self, id):
        self.id = id

    def __hash__(self):
        return self.id

    def __repr__(self):
        return str(self.id)

set_foo = set()
for i in reversed(range(10)):
    new_a = Foo(i)
    set_foo.add(new_a)

for i in set_foo:
    print(i)


import numpy as np
from numpy.random import default_rng
rand = default_rng(32432)

x = list(a_s)
print(x)
print(sorted(x, key=lambda x: x.__hash__()))

