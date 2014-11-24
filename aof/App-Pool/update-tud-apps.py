#! /usr/bin/python2
# -*- coding: utf8 -*-4

'''
This script updates all TUD apps in the app pool (in the "apps" subdirectory). 
It must be executed from the App Pool folder
The apps are downloaded from our Jenkins server. 
Therefore, it only works from our internal network.
'''
 
import cStringIO
import json
import pycurl
import os
import sys
import hashlib
 
##########
# configuration
 
build_host = "dev.plt.et.tu-dresden.de:8085/jenkins"
viewAPIURL = "http://" + build_host + "/view/IAF/api/json"
lastBuildAPIURL = "http://" + build_host + "/job/%s/lastSuccessfulBuild/api/json"
lastBuildArtifactLURL = "http://" + build_host + "/job/%s/lastSuccessfulBuild/artifact/%s"
fingerprintInfoURL= "http://" + build_host + "/fingerprint/%s/api/json"
localSaveDir = "apps"
artifactExtension=".apk"

def getJobs():
	buf = cStringIO.StringIO()
	viewURL = viewAPIURL
	c = pycurl.Curl()
	c.setopt(c.URL, viewURL)
	c.setopt(c.WRITEFUNCTION, buf.write)
	c.perform()
	jsonstr = buf.getvalue()
	# print jsonstr
	jd = json.loads(jsonstr)
	# print jd
	buf.close()
	jobs = jd['jobs']
	jobnames = list()
	for job in jobs:
		#print(job['name'])
		jobnames.append(job['name'])
	return jobnames
  
def getBuildNumberfromHash(hash):
	buf = cStringIO.StringIO()
	url = fingerprintInfoURL % (hash)
	c = pycurl.Curl()
	c.setopt(c.URL, url)
	c.setopt(c.WRITEFUNCTION, buf.write)
	c.perform()
	if (c.getinfo(pycurl.HTTP_CODE) != 200):
	  return "error"
	jsonstr = buf.getvalue()
	# print jsonstr
	#print(url)
	#print(jsonstr)
	jd = json.loads(jsonstr)
	# print jd
	buf.close()
	original = jd['original']
	# print(original['number'])
	return original['number']

# list of jobs from jenkins, they are expected to be URL encoded already

jobList = getJobs()
#print(jobList)
##########
# UDFs
 
def downloadFile(url,filename):
	# print("==> Downloading File: "+filename+" URL: "+url)
	fp = open(filename, "wb")
	curl = pycurl.Curl()
	curl.setopt(pycurl.URL, url)
	curl.setopt(pycurl.WRITEDATA, fp)
	curl.perform()
	curl.close()
	fp.close()
 
 
###########
# start
 
print("Checking Jenkins for app updates ... ")
 
if not os.path.exists(localSaveDir):
	print("==> Creating Dir %s" % (localSaveDir))
	os.makedirs(localSaveDir)
 
for job in jobList:
	buf = cStringIO.StringIO()
	job = job.encode('ascii','ignore')
	jobURL = lastBuildAPIURL % (job)
	c = pycurl.Curl()
	c.setopt(c.URL, jobURL)
	c.setopt(c.WRITEFUNCTION, buf.write)
	c.perform()
	jsonstr = buf.getvalue()
	# print(jsonstr)
	jd = json.loads(jsonstr)
	buf.close()
	artifacts = jd['artifacts']
	#print(artifacts)
 
	for art in artifacts:
		if art['fileName'].find(artifactExtension) > -1:
			artURL = lastBuildArtifactLURL % (job,art['relativePath'])
			# if the apk exists in the app pool, check if we have to download it
			if os.path.isfile(localSaveDir+"/"+str(art['fileName'])):
				hash = hashlib.md5(open(localSaveDir+"/"+str(art['fileName'])).read()).hexdigest()
				localBN = getBuildNumberfromHash(hash)
				print (str(art['fileName'])+ " - build "+ str(localBN))
				if (localBN == "error"):
					print("Hash for " + str(art['fileName']) + " was not found on Jenkins server.")
					break
				remoteBN = jd['number']
				if (localBN < remoteBN):
					sys.stdout.write("Updating "+str(art['fileName'])+" from build "+str(localBN)+" to build "+str(remoteBN)+" ... ")
					sys.stdout.flush()
					downloadFile(str(artURL),localSaveDir + "/" + str(art['fileName']))
					print("Done\n")
				elif (localBN == remoteBN):
					break
				else:
					break
			else:
				sys.stdout.write("Downloading new app "+str(art['fileName'])+". Build "+str(remoteBN)+" ... ")
				sys.stdout.flush()
				downloadFile(str(artURL),localSaveDir + "/" + str(art['fileName']))
				print("Done")
				
buf.close()
sys.exit(0)