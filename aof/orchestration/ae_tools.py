from aof.orchestration.AOFGraph import AOFGraph
from aof.orchestration.AppEnsemble import AppEnsemble
from aof.orchestration.AppPool import AppPool
from pyramid.path import AssetResolver
import os

def initializeExistingAE():
    app_ensembles = dict()
    a = AssetResolver()
    ae_dir = a.resolve('aof:static/App-Ensembles/').abspath()

    for i in os.listdir(ae_dir):
        if i.endswith(".ae"):
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
    ae_dir = a.resolve('aof:static/App-Ensembles/').abspath()

    for i in os.listdir(ae_dir):
        if i.endswith(".ae"):
            ae_ctr += 1
    return ae_ctr



def getRequiredApps(ae):
    #TODO: Adapt to new vocabulary
    res = ae.query("""
        PREFIX o: <http://comvantage.eu/ontologies/iaf/2013/0/Orchestration.owl#>
        SELECT DISTINCT ?uri ?name
        WHERE {
            [] o:instanceOf ?app;
               o:Name ?name .
        }
    """)
    return res

def getAppDetails(uri):
    isAndroidAppQuery = ("""
        # AOF PREFIXES
        PREFIX aof: <http://eatld.et.tu-dresden.de/aof/>

        ASK
        WHERE {
                <%(uri)s> a aof:AndroidApp .
        }
    """) % {'uri': uri}

    appDetailsQuery = ("""
        # AOF PREFIXES
        PREFIX aof: <http://eatld.et.tu-dresden.de/aof/>

        SELECT *
        WHERE {
            # This is only for Android apps
            <%(uri)s> a aof:AndroidApp ;

                # Label & comment
                rdfs:label ?label ;
                rdfs:comment ?comment .

            # Role
            OPTIONAL {
                <%(uri)s> aof:hasRole ?role .
            }

            # Main screenshot
            OPTIONAL {
                <%(uri)s> a aof:AndroidApp ;
                    aof:MainScreenshot [
                    aof:hasScreenshot ?main_screenshot_uri ;
                    aof:hasScreenshotThumbnail ?main_screenshot_thumb_uri
                ] .
                OPTIONAL {
                    <%(uri)s> a aof:AndroidApp ;
                        aof:MainScreenshot [
                        rdfs:comment ?main_screenshot_comment
                    ] .
                }
            }

            # Creator
            <%(uri)s> dc:creator [
                foaf:name ?creator_name ;
                foaf:mbox ?creator_mbox ;
                foaf:homepage ?creator_homepage
            ]
        }
    """) % {'uri': uri}

    # Get all additional screenshots
    screenshotQuery = ("""
        # AOF PREFIXES
        PREFIX aof: <http://eatld.et.tu-dresden.de/aof/>

        SELECT *
        WHERE {
            OPTIONAL {
                <%(uri)s> a aof:AndroidApp ;
                    aof:Screenshot [
                    aof:hasScreenshot ?main_screenshot_uri ;
                    aof:hasScreenshotThumbnail ?main_screenshot_thumb_uri
                ] .
                OPTIONAL {
                    <%(uri)s> a aof:AndroidApp ;
                        aof:Screenshot [
                        rdfs:comment ?main_screenshot_comment
                    ] .
                }
            }
        }
    """) % {'uri': uri}

    # Get details for all entry points
    entryPointsQuery = ("""
        # AOF PREFIXES
        PREFIX aof: <http://eatld.et.tu-dresden.de/aof/>
        PREFIX android: <http://schemas.android.com/apk/res/android>

        SELECT *
        WHERE {
            OPTIONAL {
                <%(uri)s> aof:providesEntryPoint ?entryPoint .

                ?entryPoint a android:action ;
                    rdfs:label ?label ;
                    rdfs:comment ?comment ;
                    android:name ?androidActionName .
            }
        }
    """) % {'uri': uri}

    # Get all inputs for all entry points
    entryPointsInputsQuery = ("""
        # AOF PREFIXES
        PREFIX aof: <http://eatld.et.tu-dresden.de/aof/>
        PREFIX android: <http://schemas.android.com/apk/res/android>

        SELECT ?entryPoint ?input ?isRequired ?datatype ?androidExtraName
        WHERE {
            OPTIONAL {
                <%(uri)s> aof:providesEntryPoint ?entryPoint .

                ?entryPoint a android:action ;
                    aof:hasInput ?input .

                ?input a android:extra ;
                    aof:isRequired ?isRequired ;
                    aof:datatype ?datatype ;
                    android:name ?androidExtraName .
            }
        }
    """) % {'uri': uri}

    # Get details for all exit points
    exitPointsQuery = ("""
        # AOF PREFIXES
        PREFIX aof: <http://eatld.et.tu-dresden.de/aof/>
        PREFIX android: <http://schemas.android.com/apk/res/android>

        SELECT *
        WHERE {
            OPTIONAL {
                <%(uri)s> aof:providesExitPoint ?exitPoint .

                ?exitPoint a android:action ;
                    rdfs:label ?label ;
                    rdfs:comment ?comment .
            }
        }
    """) % {'uri': uri}

    # Get all inputs for all entry points
    exitPointsOutputsQuery = ("""
        # AOF PREFIXES
        PREFIX aof: <http://eatld.et.tu-dresden.de/aof/>
        PREFIX android: <http://schemas.android.com/apk/res/android>

        SELECT ?entryPoint ?output ?isGuaranteed ?datatype ?androidExtraName
        WHERE {
            OPTIONAL {
                <%(uri)s> aof:providesEntryPoint ?entryPoint .

                ?entryPoint a android:action ;
                    aof:hasOutput ?output .

                ?output a android:extra ;
                    aof:isGuaranteed ?isGuaranteed ;
                    aof:datatype ?datatype ;
                    android:name ?androidExtraName .
            }
        }
    """) % {'uri': uri}

    ap = ap = AppPool.Instance()
    isAndroidApp = ap.query(isAndroidAppQuery).askAnswer
    appDetails = ap.query(appDetailsQuery).bindings[0]
    screenshots = ap.query(screenshotQuery).bindings
    entryPoints = ap.query(entryPointsQuery).bindings
    entryPointInputs = ap.query(entryPointsInputsQuery).bindings
    exitPoints = ap.query(exitPointsQuery).bindings
    exitPointOutputs = ap.query(exitPointsOutputsQuery).bindings

    #print(res.bindings[0]['?creator_name'])
    #print("Is the app an aof:AndroidApp? %s \n" % isAndroidApp)
    #print("App Details: %s \n" % appDetails)
    #print("Screenshots: %s \n" % screenshots)

    #print("Entry Points: %s \n" % entryPoints)
    #print("Entry Point Inputs: %s" % entryPointInputs)

    #print("Exit Points: %s \n" % exitPoints)
    #print("Exit Point Outputs: %s" % exitPointOutputs)




# Will only be called when executed from shell
if __name__ == "__main__":
    os.chdir("/home/jo/Dokumente/Orchestration/AOF")
    ap = AppPool.Instance("http://localhost:8081/static/App-Pool/pool.ttl")

    print("This graph is a singleton and currently contains %i triples" %(ap.__len__() ) )

    res = getAppDetails("http://dev.plt.et.tu-dresden.de:8085/jenkins/job/AOFConductor")
    #print(res.serialize(format="txt").decode())