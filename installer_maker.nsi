Outfile "JinadaInstaller.exe"

InstallDir $PROGRAMFILES\Jinada

RequestExecutionLevel admin

Section "Install Jinada" SEC01

  # Set the output directory where files will be installed
  SetOutPath $INSTDIR

  # Copy the main executable (Jinada.exe) to the install directory
  File "dist\Jinada\Jinada.exe"

  # Create the _internal folder in the installation directory
  SetOutPath $INSTDIR\_internal

  # Recursively copy all files from the _internal directory to the _internal folder
  File /r "dist\Jinada\_internal\*"

  # Ensure python310.dll is placed in the _internal folder as well
  File "dist\Jinada\_internal\python310.dll"

  # Create a Start Menu shortcut
  CreateShortCut "$SMPrograms\Jinada.lnk" "$INSTDIR\Jinada.exe"

  # Modify the PATH environment variable
  # Read the current PATH value
  ReadEnvStr $0 "PATH"

  # Append the _internal folder to the PATH (for this session or system-wide)
  StrCpy $0 "$INSTDIR\_internal;$0"

  # Write the new PATH value to the registry (for the current user)
  WriteRegStr HKCU "Environment" "PATH" $0

  # Write the uninstaller to the installation directory
  WriteUninstaller "$INSTDIR\uninstaller.exe"

SectionEnd

Section "Uninstall"

  # Delete the installed executable
  Delete "$INSTDIR\Jinada.exe"
  
  # Delete the Start Menu shortcut
  Delete "$SMPrograms\Jinada.lnk"

  # Recursively remove the _internal directory
  RMDir /r $INSTDIR\_internal

  # Remove the installation directory
  RMDir $INSTDIR

  # Remove the PATH modification
  DeleteRegValue HKCU "Environment" "PATH"

  # Delete the uninstaller
  Delete "$INSTDIR\uninstaller.exe"

SectionEnd