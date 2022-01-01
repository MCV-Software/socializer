!include "MUI2.nsh"
!include "LogicLib.nsh"
!include "x64.nsh"
Unicode true
CRCCheck on
ManifestSupportedOS all
XPStyle on
Name "Socializer"
OutFile "socializer_setup.exe"
InstallDir "$PROGRAMFILES\socializer"
InstallDirRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\socializer" "InstallLocation"
RequestExecutionLevel admin
SetCompress auto
SetCompressor /solid lzma
SetDatablockOptimize on
VIAddVersionKey ProductName "Socializer"
VIAddVersionKey LegalCopyright "Copyright 2019 Manuel Cortez."
VIAddVersionKey ProductVersion "0.24"
VIAddVersionKey FileVersion "0.24"
VIProductVersion "0.24.0.0"
VIFileVersion "0.24.0.0"
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
var StartMenuFolder
!insertmacro MUI_PAGE_STARTMENU startmenu $StartMenuFolder
!insertmacro MUI_PAGE_INSTFILES
!define MUI_FINISHPAGE_LINK "Visit Socializer website"
!define MUI_FINISHPAGE_LINK_LOCATION "http://socializer.su"
!define MUI_FINISHPAGE_RUN "$INSTDIR\socializer.exe"
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_LANGUAGE "Russian"
!insertmacro MUI_LANGUAGE "English"
!insertmacro MUI_LANGUAGE "Spanish"

!insertmacro MUI_RESERVEFILE_LANGDLL
Section
SetShellVarContext All
SetOutPath "$INSTDIR"
${If} ${RunningX64}
File /r program64\*
${Else}
File /r program32\*
${EndIf}
CreateShortCut "$DESKTOP\socializer.lnk" "$INSTDIR\socializer.exe"
!insertmacro MUI_STARTMENU_WRITE_BEGIN startmenu
CreateDirectory "$SMPROGRAMS\$StartMenuFolder"
CreateShortCut "$SMPROGRAMS\$StartMenuFolder\socializer.lnk" "$INSTDIR\socializer.exe"
CreateShortCut "$SMPROGRAMS\$StartMenuFolder\Socializer on the web.lnk" "http://socializer.su"
CreateShortCut "$SMPROGRAMS\$StartMenuFolder\Uninstall.lnk" "$INSTDIR\Uninstall.exe"
!insertmacro MUI_STARTMENU_WRITE_END
WriteUninstaller "$INSTDIR\Uninstall.exe"
WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\socializer" "DisplayName" "Socializer"
WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\socializer" "UninstallString" '"$INSTDIR\uninstall.exe"'
WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall" "InstallLocation" $INSTDIR
WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall" "Publisher" "Manuel Cortez"
WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\socializer" "DisplayVersion" "0.24"
WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\socializer" "URLInfoAbout" "http://socializer.su"
WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\socializer" "VersionMajor" 0
WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\socializer" "VersionMinor" 19
WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\socializer" "NoModify" 1
WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\socializer" "NoRepair" 1
SectionEnd
Section "Uninstall"
SetShellVarContext All
DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\socializer"
RMDir /r /REBOOTOK $INSTDIR
Delete "$DESKTOP\socializer.lnk"
!insertmacro MUI_STARTMENU_GETFOLDER startmenu $StartMenuFolder
RMDir /r "$SMPROGRAMS\$StartMenuFolder"
SectionEnd
Function .onInit
!insertmacro MUI_LANGDLL_DISPLAY
${If} ${RunningX64}
StrCpy $instdir "$programfiles64\socializer"
${EndIf}
FunctionEnd
