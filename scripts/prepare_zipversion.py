#! /usr/bin/env python# -*- coding: iso-8859-1 -*-
import  shutil
import os
import sys

def create_archive():
	os.chdir("..\\src")
	print("Creating zip archive...")
	folder = "socializer.dist"
	shutil.make_archive("socializer", "zip", folder)
#	if os.path.exists("dist"):
#		shutil.rmtree("dist")
	if os.path.exists("build"):
		shutil.rmtree("build")
	os.chdir("..\\scripts")

create_archive()