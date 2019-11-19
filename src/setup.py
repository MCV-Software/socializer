# -*- coding: utf-8 -*-
import sys
import application
from cx_Freeze import setup, Executable
import platform
import os
from glob import glob

def find_sound_lib_datafiles():
	import os
	import platform
	import sound_lib
	path = os.path.join(sound_lib.__path__[0], 'lib')
	if platform.architecture()[0] == '32bit' or platform.system() == 'Darwin':
		arch = 'x86'
	else:
		arch = 'x64'
	dest_dir = os.path.join('sound_lib', 'lib', arch)
	source = os.path.join(path, arch)
	return (source, dest_dir)

def find_accessible_output2_datafiles():
	import os
	import accessible_output2
	path = os.path.join(accessible_output2.__path__[0], 'lib')
	dest_dir = os.path.join('accessible_output2', 'lib')
	return (path, dest_dir)

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
	zip_include_packages=["accessible_output2", "sound_lib", "arrow"],
#	zip_exclude_packages=["lxml", "wx", "sound_lib", "enchant", "accessible_output2"],
	include_files=["session.defaults", "cacert.pem", "app-configuration.defaults", "locales", "sounds", "documentation", "../windows-dependencies/x86/oggenc2.exe", "../windows-dependencies/x86/bootstrap.exe", ("../windows-dependencies/dictionaries", "lib/enchant/share/enchant/myspell"), find_sound_lib_datafiles(), find_accessible_output2_datafiles()],
	packages=["interactors", "presenters", "views", "wxUI"],
	)

executables = [
    Executable('main.py', base=base, targetName="socializer")
]

setup(name='Socializer',
      version=application.version,
      description=application.description,
      options = {"build_exe": build_exe_options},
      executables=executables
      )
