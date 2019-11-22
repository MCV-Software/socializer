# -*- coding: utf-8 -*-
import sys

### ToDo: Remove this piece of code a month later or something like that, when the migration to the cx_freeze executable will be complete.
def is_pyinstaller():
	if hasattr(sys, 'frozen') and hasattr(sys, '_MEIPASS'):
		return True
	else:
		return False

name = "Socializer"
version = "0.23"
author = "Manuel Cortez"
authorEmail = "manuel@manuelcortez.net"
copyright = "Copyright (C) 2016-2019, Manuel Cortez"
description = name+" Is an accessible VK client for Windows."
url = "http://socializer.su"
# The short name will be used for detecting translation files. See languageHandler for more details.
short_name = "socializer"
translators = ["Darya Ratnikova (Russian)", "Manuel Cortez (Spanish)"]
bts_name = "socializer"
bts_access_token = "U29jaWFsaXplcg"
bts_url = "https://issues.manuelcortez.net"
### Update information
# URL to retrieve the latest updates for the stable branch.
update_stable_url = "https://code.manuelcortez.net/manuelcortez/socializer/raw/master/update-files/socializer.json"
# URL to retrieve update information for the "next" branch. This is a channel made for alpha versions.
# Every commit will trigger an update, so users wanting to have the bleeding edge code will get it as soon as it is committed here and build by a runner.
update_next_url = "https://code.manuelcortez.net/api/v4/projects/4/repository/commits/master"
# Short_id of the last commit, this is set to none here because it will be set manually by the building tools.
update_next_version = "03286a44"