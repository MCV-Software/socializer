# -*- coding: utf-8 -*-
import sys
import application
from cx_Freeze import setup, Executable
import platform
import os
from glob import glob

def get_data():
    """ Get data files for the project. """
    import accessible_output2
    import sound_lib
    datas = [
        (["session.defaults", "app-configuration.defaults", "cacert.pem"], ""),]+get_sounds()+get_locales()+get_documentation()+get_architecture_files()
    print(datas)
    return datas

base = None
if sys.platform == 'win32':
    base = 'Win32GUI'

build_exe_options = dict(
	build_exe="dist",
	optimize=2,
	include_msvcr=True,
#	zip_include_packages="*",
#	zip_exclude_packages=["lxml", "wx", "sound_lib", "enchant", "accessible_output2"],
	include_files=["session.defaults", "app-configuration.defaults", "cacert.pem", "locales", "sounds", "documentation", "../windows-dependencies/x86/oggenc2.exe", "../windows-dependencies/x86/bootstrap.exe"],
	)

executables = [
    Executable('main.py', base=base)
]

setup(name='Socializer',
      version=application.version,
      description=application.description,
      options = {"build_exe": build_exe_options},
      executables=executables
      )
