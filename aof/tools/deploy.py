#!/usr/bin/python3
# encoding: utf-8
#
# Copyright 2013 Professur fuer Prozessleittechnik
# http://www.et.tu-dresden.de/ifa/?id=plt
#
# Licensed under the EUPL, Version 1.1 or – as soon they
# will be approved by the European Commission - subsequent
# versions of the EUPL (the "Licence");
# You may not use this work except in compliance with the
# Licence.
#
# You may obtain a copy of the Licence at:
# http://ec.europa.eu/idabc/eupl
#
# Unless required by applicable law or agreed to in
# writing, software distributed under the Licence is
# distributed on an "AS IS" basis,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied.
# See the Licence for the specific language governing
# permissions and limitations under the Licence.
#


'''
deploy -- Deploy an App Ensemble

The deploy script will use a target's SDK tools to deploy an App Ensemble to a device. Please make sure the required tools are in your PATH variable or supply the directory using the appropriate parameter.

@author:     Johannes Pfeffer

@version:    0.5

@release:    elephant
'''

import os # os abstraction (e.g. listdir)
from os import listdir
from os import path

from subprocess import Popen, PIPE

import sys # e.g. for exit()

import time # local time for App Ensemble name
import shutil # for filesystem operations
from simpleconfigparser import simpleconfigparser

config = simpleconfigparser()
config.read(os.path.join(os.path.dirname(os.path.abspath(__file__)),os.pardir,os.pardir)+'/aof.conf')

# Simulate?
SIMULATE = False

# Target Platform
PLATFORM = "Android"

sdkdir = path.normpath(config.Paths.adb_location)

remoteIafFolder = "/sdcard/ComVantage-IAF/"

# Mode
MODE = "Install"
# Maybe later add mode REMOVE

class CLIError(Exception):
    '''Generic exception to raise and log different fatal errors.'''
    def __init__(self, msg):
        super(CLIError).__init__(type(self))
        self.msg = "E: %s" % msg
    def __str__(self):
        return self.msg
    def __unicode__(self):
        return self.msg

def execadbshell(cmd):
    ''' executes the command trough adb shell and uses a trick to extract the return code '''
    return int(os.popen(sdkdir + 'adb shell \"' + cmd + ' > /dev/null 2>&1; echo $? \"').read().strip())

class Device:
    def __init__(self):
        f = os.popen(path.join(sdkdir,'adb devices -l'))
        result = f.read()
        print(result)
        content = result.split('attached')
        back = content[1].find('device')
        if back > 1:
            self.has = 1
        if back == -1:
            self.has = 0

    def getStatus(self):
        return self.has

class Deploy:
    def __init__(self, aePath):
        self.aePath = aePath

        # set App-Ensemble File
        aeFullPath = self.aePath

        if (aeFullPath == ""):
            print("An App Ensemble description file must be supplied")
            sys.exit(1)
        elif (".ttl" not in os.path.splitext(aeFullPath) ):
            print("Please choose the App Ensemble description file which must have a .ttl extension")
            sys.exit(1)

        # Derive some things from the App-Ensemble folder
        descrFilename = os.path.split(aeFullPath)[1]
        print("Local App Ensemble: " + aeFullPath + "\n")

        ###########################################
        # Check & create necessary directories on device
        ###########################################

        if PLATFORM == "Android":
            # Check if a device is present
            if (str.split(os.popen(sdkdir + 'adb devices').read(),'\n')[1] == ""):
                print("No device seems to be attached")

             # Does the selected App Ensemble file exist?
            if not os.path.exists(aeFullPath):
                print("The App Ensemble seems to be incorrect. \n" + aeFullPath + " does not exist.")
            if not os.path.exists(os.path.join(os.path.dirname(aeFullPath),"apps")):
                print("There must be an 'apps' directory in your App Ensemble folder. \n")
            if not os.path.exists(aeFullPath):
                print("There must be a description file in your App Ensemble that has the same name as the App Ensemble folder and the file extension '.ttl'. \n")

            # Do the necessary directories exist on the device (Android)
            if not os.popen(sdkdir + 'adb shell \"test -d /sdcard && echo 1\"').read():
                print("The folder /sdcard/ was not found on the device.")

            # Does the folder ComVantage-IAF exist on the device? If not, create it.
            if execadbshell("test -d /sdcard/ComVantage-IAF") is not 0:
                if not SIMULATE:
                    if execadbshell("mkdir -p /sdcard/ComVantage-IAF") is 0:
                        print("The folder '/sdcard/ComVantage-IAF/' was created on the device.")
                    else:
                        print("The folder '/sdcard/ComVantage-IAF/' could not be created on the device.")

        ###########################################
        # Push files to device
        ###########################################
        # Set for gathering files to push
        ERRORS = False

        files = set()
        apps = set()

        # List files in apps directory
        filelist = os.listdir(os.path.join(os.path.dirname(aeFullPath),"apps"))
        for filename in filelist:
            # print(filename)
            apps.add(os.path.join(os.path.dirname(aeFullPath),"apps",filename))

        print("A total of "+str(len(apps))+" apps will be installed.\n")

        files.add(aeFullPath)

        if PLATFORM == "Android":
            if MODE == "Install":
                for fileName in files:
                    print("Pushing " + os.path.split(fileName)[1])
                    if not SIMULATE:
                        message = os.popen(sdkdir+'adb push "'+fileName+'" '+remoteIafFolder+os.path.split(fileName)[1]).read()
                        # Debug:
                        # print(sdkdir+'adb push "'+fileName+'" '+remoteIafFolder+os.path.split(fileName)[1])
                        if ("failed" in message):
                            ERRORS = True
                            print(" ... " + message[message.find("[")+1:message.find("]")])
                print()
                result = dict()
                for app in apps:
                    key = ""
                    value = ""
                    print(str("Installing " + os.path.split(app)[1] + " ... "), end="", flush=True)
                    key = os.path.split(app)[1]
                    if not SIMULATE:
                        message = Popen(sdkdir+'adb install -r "'+app+'"', shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, bufsize=0).stdout.read().decode().rstrip('\n')
                        if ("Success" in message):
                            print("Success")
                            value = "Success"
                        else:
                            ERRORS = True
                            print(message[message.find("[")+1:message.find("]")])
                            value = message[message.find("[")+1:message.find("]")]
                    result[key] = value
                print()
            self.json = buildJson(result)

    def getJSON(self):
        return self.json
      
if __name__ == "__main__":

    from argparse import ArgumentParser # for command line arguments

    ###########################################
    # Command line arguments
    ###########################################

    parser = ArgumentParser()

    # Add more options if you like
    parser.add_argument("--simulate", dest="simulate",
        help="Simulate the deployment. Don't actually deploy.", action='store_true')
    parser.add_argument("--sdk", dest="sdk",
        help="If the SDK tools are not in your PATH, you can provide their location here.")
    parser.add_argument("-ae",dest="path", metavar="PATH",
        help="Set the aeFullPath to the description file of the App Ensemble. If not set a file chooser will be used")
    parser.add_argument("--remote-iaf-folder", dest="remoteIafFolder",
        help="Override the default remote IAF folder", metavar="PATH")
    args = parser.parse_args()

    if args.simulate == True:
        SIMULATE= args.simulate
    if isinstance(args.sdk, str):
        sdkdir = args.sdk
    if isinstance(args.path, str):
        ae = os.path.abspath(args.path)
    if isinstance(args.sdk, str):
        remoteIafFolder = args.remoteIafFolder
    Deploy(ae)

def buildJson(result):
    jsonString = '{devices:['
    lenth = len(result.items())
    keys = result.keys()
    keys_list = list(keys)
    for i in range(0,lenth-2):
        name = keys_list[i]
        status = result.get(name)
        jsonString = jsonString + add(name,status)

    name_last = keys_list[lenth-1]
    status_last = result.get(name_last)
    jsonString = jsonString + lastadd(name_last,status_last)
    return jsonString

def add(name,status):
        item = '{name:' + "'" + name + "'" + ',' + 'status:' + "'" + status + "'" + '},'
        return item

def lastadd(name,status):
        item = '{name:' + "'" + name + "'" + ',' + 'status:' + "'" + status + "'" + '}]}'
        return item

