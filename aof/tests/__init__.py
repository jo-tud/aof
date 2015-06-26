

# Test-Settings

settings=dict()
settings["app_pool_path"]="aof:tests/res/test_pool.ttl"
settings["app_ensemble_folder"]="aof:resources/App-Ensembles"
settings["documentation_docs_path"]="aof:resources/docs"
settings["META"]="{'appname':'Application Orchestration Framework','acronym':'AOF'}"
settings["test_resources_path"]="aof:tests/res"
settings["ae_name"]='testAppEnsemble'


# Helper-Functions

from pyramid.path import AssetResolver
import os
from shutil import copyfile
import zipfile
from aof.orchestration.AppEnsemble import AppEnsemble

def _create_test_html_file():
        path_from=AssetResolver().resolve(settings["test_resources_path"]).abspath()
        path_to=AssetResolver().resolve(settings["documentation_docs_path"]).abspath()
        copyfile(os.path.join(path_from,"test.html"), os.path.join(path_to,"test.html"))

def _delete_test_html_file():
    path_to=AssetResolver().resolve(settings["documentation_docs_path"]).abspath()
    os.remove(os.path.join(path_to,"test.html"))

def _create_test_AppEnsemble():
    # creates an test archive with test-files and saves it into the App-Ensembles Folder

    a = AssetResolver()
    #Path where the files for the zip are located
    originsPath=a.resolve(settings['test_resources_path']).abspath()

    # Destination of the zip archive
    destTestArchive= os.path.join(a.resolve(settings['app_ensemble_folder']).abspath(), settings["ae_name"] + AppEnsemble.ae_extension)

    # Creation of the zip archive
    zip_ae = zipfile.ZipFile(destTestArchive, mode='w')
    try:
        zip_ae.write(os.path.join(originsPath,'test_ae.ttl'),AppEnsemble.ae_filename)
        zip_ae.write(os.path.join(originsPath,'test_ae.bpmn'),AppEnsemble.bpmn_filename)
        zip_ae.write(os.path.join(originsPath,'max_test.ttl'),'apps/max_test.ttl')
        zip_ae.write(os.path.join(originsPath,'min_test.ttl'),'apps/min_test.ttl')
    finally:
        zip_ae.close()

def _delete_test_AppEnsemble():
    destTestArchive= os.path.join(AssetResolver().resolve(settings['app_ensemble_folder']).abspath(), settings["ae_name"] + AppEnsemble.ae_extension)
    os.remove(destTestArchive)