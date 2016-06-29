@echo off
echo Generating file list..
dir ..\doc\*.py /L /B /S > %TEMP%\listfile.txt
echo Generating .POT file...
xgettext --language=Python -o socializer-documentation.pot --keyword=_   -d socializer  -f %TEMP%\listfile.txt -c --no-location --no-wrap
del %TEMP%\listfile.txt
echo Done.
