@echo off
echo Generating file list..
dir ..\src\*.py /L /B /S > %TEMP%\listfile.txt
echo Generating .POT file...
xgettext --language=Python --from-code=utf-8 -o socializer.pot --keyword=_   -d socializer  -f %TEMP%\listfile.txt -c --no-location --no-wrap
del %TEMP%\listfile.txt
echo Done.
