from aof.orchestration.AOFGraph import AOFGraph
from aof.orchestration.AppEnsemble import AppEnsemble
from aof.orchestration.AppPool import AppPool
from pyramid.path import AssetResolver
import os

def initializeExistingAE():
    app_ensembles = dict()
    a = AssetResolver()
    ae_dir = a.resolve(AppEnsemble.ae_folder_path).abspath()

    for i in os.listdir(ae_dir):
        if i.endswith(AppEnsemble.ae_extension):
            i = i[:-3]
            g = AOFGraph.Instance()
            # Check if
            if g.get_context(i):
                g.remove_graph(i)

            ae = AppEnsemble(i)
            app_ensembles[i] = ae

    return app_ensembles

def getNumberOfAE():
    ae_ctr = 0
    a = AssetResolver()
    ae_dir = a.resolve(AppEnsemble.ae_folder_path).abspath()

    for i in os.listdir(ae_dir):
        if i.endswith(AppEnsemble.ae_extension):
            ae_ctr += 1
    return ae_ctr

# Will only be called when executed from shell
if __name__ == "__main__":
    os.chdir("/home/jo/Dokumente/Orchestration/AOF")
    ap = AppPool.Instance("http://localhost:8081/static/App-Pool/pool.ttl")

    print("This graph is a singleton and currently contains %i triples" %(ap.__len__() ) )

    #print(res.serialize(format="txt").decode())