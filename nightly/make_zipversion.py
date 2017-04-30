#! /usr/bin/env python# -*- coding: iso-8859-1 -*-
import  shutil

def create_build():
	os.chdir("../src")
	print "Current path is {0}".format(os.getcwd())
	subprocess.call(["C:\python27x86\python.exe", "setup.py", "py2exe"])

def create_archive():
	print "Creating zip archive..."
	shutil.make_archive("socializer-nightly-build", "zip", "socializer")
	shutil.rmtree("socializer")

create_build()
create_archive()