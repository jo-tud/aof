from aof.tools.AppEnsemble import AppEnsemble
from pyramid.path import AssetResolver
from os import path
import zipfile
#
a = AssetResolver()
a_path = a.resolve('aof:static/App-Ensembles/Demo/ae.ttl').abspath()
#
print("File = %s" % a_path)
# print("Is Zipfile = %s" % zipfile.is_zipfile(a_path))
#
# ae = AppEnsemble(a_path)
# ae2 = AppEnsemble(a_path)
#
# ae3 = AppEnsemble(a_path)
# print("Number of instances: %i" % ae.counter)
# print(ae.namelist())
# ae.extract("ae.ttl")

ae = AppEnsemble(a_path)

print("ae_file = %s" %ae.ae_file)
a = set()
a.add(ae)