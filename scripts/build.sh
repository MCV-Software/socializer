#!/bin/bash
# Define paths for a regular use, if there are not paths for python32 or 64, these commands will be taken.
pythonpath32="/C/python27x86"
pandocpath="pandoc.exe"

help () {
	echo -e "$0 | usage:"
	echo -e "$0 | \t./build.sh [-py32path <path to python for 32 bits> | -h]"
}

# parsing options from the command line
while [[ $# > 1 ]]
	do
	key="$1"
	shift

case $key in
	-py32path)
		pythonpath32="$1"
		shift
	;;
		-help)
		help
	;;
	*)
	help
esac
done

cd ../src
if [ -d build/ ];
	then
	rm -rf build
fi
if [ -d dist/ ];
	then
	rm -rf dist
fi
if [ -d documentation/ ];
	then
	rm -rf documentation
fi
mkdir documentation
cp ../changelog.md documentation/changelog.md
cd documentation
$pandocpath -s changelog.md -o changelog.html
rm changelog.md
cd ..
cd ../doc
$pythonpath32/python.exe generator.py
mv -f en ../src/documentation/
mv -f es ../src/documentation/
cd ../src
$pythonpath32/python.exe "setup.py" "py2exe" "--quiet"
mv -f dist ../nightly/socializer
rm -rf build
cd ../nightly
$pythonpath32/python.exe make_zipversion.py