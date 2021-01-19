# socializer 

[![pipeline status](https://gitlab.com/socializer1/socializer/badges/master/pipeline.svg)](https://gitlab.com/socializer1/socializer/commits/master)

> Note: this project has two different main repositories. [Here is the official repository, hosted in GitLab,](https://gitlab.com/socializer1/socializer) [Here is a mirror repository hosted in GitHub.](https://github.com/manuelcortez/socializer) Github repository will accept pull requests and issues reported by github users, while Gitlab's repository will provide the wiki, documentation, and support for user reported issues.

A desktop application for handling [vk.com](https://vk.com) in an easy way.

[See Socializer's website](http://socializer.su)

> Note: this is the developer oriented documentation. If you want to read the user manual of socializer, [read the manual in the project's website](http://socializer.su/documentation)

## running

This document describes how to run Socializer from source and how to build a binary version which doesn't need Python and the other dependencies to run.

### Required dependencies

Although most dependencies (except Python) can be found in the windows-dependencies directory, we provide links to their official websites.

* [Python,](http://python.org) version 3.7.7

#### Dependencies that must be installed using pip

Python installs a tool called Pip that allows to install packages in a simple way. You can find it in the python scripts directory. To install packages using Pip, you have to navigate to the scripts directory using a command prompt, for example:  
    cd C:\python37\scripts

You can also add the scripts folder to your path environment variable or choose the corresponding option when installing Python.  
Pip is able to install packages listed in a special text file, called the requirements file. To install all remaining dependencies, perform the following command:  
    pip install -r requirements.txt  
Note that if you perform the command from the path where Pip is located, you need to specify the path to your Socializer root folder where the requirements file is located, for example:  
    pip install -r D:\repos\socializer\requirements.txt  

Pip will automatically get the additional libraries that the listed packages need to work properly.

If you need to update your dependencies, perform the following command:

pip install --upgrade -r requirements.txt

#### Other dependencies

These dependencies are located in the windows-dependencies directory. You don't need to install or modify them.

* Bootstrap 1.2.1: included in dependencies directory.  
This dependency has been built using pure basic 4.61. Its source can be found at http://hg.q-continuum.net/updater
* [oggenc2.exe,](http://www.rarewares.org/ogg-oggenc.php) version 2.87  
* Microsoft Visual c++ 2017 redistributable dlls.

#### Dependencies required to build the installer

* [NSIS,](http://nsis.sourceforge.net/) version 3.04

### Running Socializer from source

Now that you have installed all these packages, you can run Socializer from source using a command prompt. Navigate to the repo's `src` directory, and type the following command:

    python main.py

	If necessary, change the first part of the command to reflect the location of your python executable.

### Generating the documentation

To generate the documentation in html format, ensure you are in the doc folder inside this repo. After that, run these commands:  
    copy ..\changelog.md .  
    python document_importer.py  
    cd ..\src  
    python ..\doc\generator.py  

The documentation will be generated, placing each language in a separate folder in the doc directory.

### Building a binary version

A binary version doesn't need python and the other dependencies to run, it's the same version that you will find on the Socializer's website if you download the zip files or the Alpha versions.

To build it, run the following command from the src folder:

    python setup.py build

	You will find the binaries in the dist directory.

### Building an installer

If you want to install Socializer on your computer, you must create the installer first. Follow these steps:

* Navigate to the src directory, and Write the latest alpha version in the application file, so this version will be able to check updates and get the alpha channel: c:\python37\python.exe write_version_data.py
* create a binary version: C:\python37\python setup.py build
* run the installer script: C:\nsis\makensis.exe installer.nsi

## Contributing

If you are interested in this project, you can help it by [translating this program](https://code.manuelcortez.net/manuelcortez/socializer/wikis/translate) into your native language and give more people the possibility of using it. Thank you in advance!

## contact

If you have questions, don't esitate to contact me in [Twitter,](https://twitter.com/manuelcortez00) or sending me an email to manuel(at)manuelcortez(dot)net. Just replace the words in parentheses with the original signs.