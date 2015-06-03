from rdflib import Dataset, Namespace
from rdflib.plugins.memory import IOMemory
from aof.orchestration.Singleton import Singleton
from aof.orchestration.namespaces import AOF

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

        # Make sure the aof namespace is always known to AOFGraph
        self.bind('aof', AOF)
