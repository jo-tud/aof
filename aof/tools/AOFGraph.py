from rdflib import Dataset, Namespace
from rdflib.plugins.memory import IOMemory
from aof.tools.Singleton import Singleton

__all__ = [
    'AOFGraph'
]

'''
This class extends Dataset which in turn extends ConjunctiveGraph, initializes a store and makes it a Singleton
'''
@Singleton
class AOFGraph(Dataset):

    def __init__(self):
        store = IOMemory() # TODO: Change the storage mechanism to a persistent one and implement caching
        Dataset.__init__(self, store=store,default_union=True)

# Will only be called when executed from shell
if __name__ == "__main__":
    s = AOFGraph.Instance()
    print("This graph is a singleton and currently contains %i triples" %(s.__len__() ) )