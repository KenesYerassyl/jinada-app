!define PRODUCT_NAME "Jinada"
!define PRODUCT_VERSION "1.0"
!define PRODUCT_DIR_REGKEY "Software\Jinada"

OutFile "JinadaWinInstaller.exe"
InstallDir "$PROGRAMFILES\Jinada"
Page Directory
Page InstFiles
Page UninstConfirm

RequestExecutionLevel admin
SetCompressor /SOLID lzma

Section "Install"
    SetOutPath "$INSTDIR"
    File "dist\Jinada.exe"

    ; Write the installation directory to the registry
    WriteRegStr HKLM "${PRODUCT_DIR_REGKEY}" "Install_Dir" "$INSTDIR"
    WriteRegStr HKLM "${PRODUCT_DIR_REGKEY}" "Version" "${PRODUCT_VERSION}"

    ; Create a desktop shortcut
    CreateShortcut "$DESKTOP\${PRODUCT_NAME}.lnk" "$INSTDIR\Jinada.exe" "" "$INSTDIR\Jinada.exe" 0

    ; Create a start menu entry
    CreateDirectory "$SMPROGRAMS\${PRODUCT_NAME}"
    CreateShortcut "$SMPROGRAMS\${PRODUCT_NAME}\${PRODUCT_NAME}.lnk" "$INSTDIR\Jinada.exe" "" "$INSTDIR\Jinada.exe" 0
    CreateShortcut "$SMPROGRAMS\${PRODUCT_NAME}\Uninstall ${PRODUCT_NAME}.lnk" "$INSTDIR\Uninstall.exe"

    ; Write the uninstaller
    WriteUninstaller "$INSTDIR\Uninstall.exe"
SectionEnd

Section "Uninstall"
    ; Remove installed files
    Delete $INSTDIR\uninstall.exe
    RMDir $INSTDIR

    ; Remove desktop shortcut
    Delete "$DESKTOP\${PRODUCT_NAME}.lnk"

    ; Remove start menu entry
    Delete "$SMPROGRAMS\${PRODUCT_NAME}\${PRODUCT_NAME}.lnk"
    Delete "$SMPROGRAMS\${PRODUCT_NAME}\Uninstall ${PRODUCT_NAME}.lnk"
    RMDir "$SMPROGRAMS\${PRODUCT_NAME}"

    ; Remove registry keys
    DeleteRegKey HKLM "${PRODUCT_DIR_REGKEY}"
SectionEnd
