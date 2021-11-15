# -*- coding: utf-8 -*-
import sys
import application
import platform
import os
import languageHandler
from cx_Freeze import setup, Executable, winmsvcr
from babel.messages import frontend as babel

languageHandler.setLanguage("en")

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

base = None
if sys.platform == 'win32':
    base = 'Win32GUI'

build_exe_options = dict(
        build_exe="dist",
        optimize=1,
        include_msvcr=False,
        zip_include_packages=["accessible_output2", "sound_lib", "arrow"],
        replace_paths = [("*", "")],
        include_files=["session.defaults", "cacert.pem", "app-configuration.defaults", "locales", "sounds", "documentation", "../windows-dependencies/x86/oggenc2.exe", "../windows-dependencies/x86/bootstrap.exe", find_sound_lib_datafiles(), find_accessible_output2_datafiles(), ("../windows-dependencies/dictionaries", "lib/enchant/data/mingw32/share/enchant/hunspell")],
        packages=["interactors", "presenters", "views", "wxUI"],
        )

executables = [
    Executable('main.py', base=base, targetName="socializer")
]

# Empty list of files to be copied, as this might cause conflicts with microsoft's redistributable packages we have already in the repo.
winmsvcr.FILES = ()
winmsvcr.FILES_TO_DUPLICATE = ()

setup(name='Socializer',
      version=application.version,
      description=application.description,
      # Register babel commands in setup file.
      cmdclass = {'compile_catalog': babel.compile_catalog,
                'extract_messages': babel.extract_messages,
                'init_catalog': babel.init_catalog,
                'update_catalog': babel.update_catalog},
      message_extractors = {"socializer": [('**.py',                'python', None)]},
      options = {"build_exe": build_exe_options},
      executables=executables
      )
