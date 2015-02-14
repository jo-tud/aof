import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.txt')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.txt')) as f:
    CHANGES = f.read()

requires = [
    'pyramid',
    'pyramid_chameleon',
    'pyramid_mako',
    'pyramid_debugtoolbar',
    'waitress',
    'rdflib',
    'rdflib-jsonld',
    'nose',
    'simpleconfigparser'
    ]

setup(name='AOF',
      version='0.0',
      description='AOF',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='Johannes Pfeffer',
      author_email='johannes.pfeffer@tu-dresden.de',
      url='',
      keywords='rdf, semantic web, linked data, app-orchestration, app-ensembles',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=requires,
      test_suite="aof",
      entry_points="""\
      [paste.app_factory]
      main = aof:main
      """,
      )
