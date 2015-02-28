from aof.orchestration.AppEnsemble import AppEnsemble
from pyramid.path import AssetResolver
import os

def getExistingAE():
    app_ensembles = dict()
    a = AssetResolver()
    ae_dir = a.resolve('aof:static/App-Ensembles/').abspath()

    for i in os.listdir(ae_dir):
        if i.endswith(".ae"):
            i = i[:-3]
            ae = AppEnsemble(i)
            app_ensembles[i] = ae

    return app_ensembles

def getRequiredApps(ae):
    #TODO: Adapt to new ontology
    res = ae.query("""
        PREFIX o: <http://comvantage.eu/ontologies/iaf/2013/0/Orchestration.owl#>
        SELECT DISTINCT ?uri ?name
        WHERE {
            [] o:instanceOf ?app;
               o:Name ?name .
        }
    """)
    return res


# Will only be called when executed from shell
if __name__ == "__main__":
    a = getExistingAE()
    #print(a)
    #a.add(AppEnsemble())
    #print(a)
    for id, ae in a.items():
        #print(ae.serialize().decode()[:200])
        #print(id, ae.identifier)
        pass

    res = getRequiredApps(a.get('Demo'))
    print(res.serialize(format="json").decode())