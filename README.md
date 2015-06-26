# AOF README

To install do the following:

    git checkout https://github.com/plt-tud/aof.git

If you want to use a virtualenv activate it now.

Cd into the project directory and execute

    python setup.py develop

Currently the most interesting branch is *distributed*. You can check it out like this:

    git checkout -b distributed origin/distributed

To start the AOF webserver execute

    pserve development.ini
   
Or 
    
    $VENV/bin/pserve development.ini
   
Now the AOF web app will be reachable locally on

    http://localhost:8081
