#! /usr/bin/env python# -*- coding: iso-8859-1 -*-
import shutil
import os
import accessible_output2
import sound_lib
import enchant

dist_folder = "socializer.dist"

accessible_output2_files = accessible_output2.find_datafiles()
final_folder = os.path.join(dist_folder, accessible_output2_files[0][0])
module_dir = os.path.dirname(accessible_output2_files[0][1][0])
shutil.copytree(module_dir, final_folder)

soundlib_files = sound_lib.find_datafiles()
final_folder = os.path.join(dist_folder, soundlib_files[0][0])
os.makedirs(final_folder, exist_ok=True)
for file in soundlib_files[0][1]:
    shutil.copy(file, final_folder)

enchant_path = os.path.dirname(enchant.__file__)
final_folder = os.path.join(dist_folder, "enchant")
if os.path.exists(final_folder):
    os.remove(final_folder)
os.makedirs(final_folder, exist_ok=True)
shutil.copytree(os.path.join(enchant_path, "data"), os.path.join(final_folder, "data"))