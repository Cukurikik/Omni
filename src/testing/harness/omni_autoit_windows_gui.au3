; OMNI Tooling & Windows System Layer
; AutoIt script for automated GUI testing of the Omni Desktop Client (e.g., Delphi/WPF)
; Ensures the native Windows client properly interfaces with the Omni DLL.

#include <MsgBoxConstants.au3>

; Enforce strict mode for AutoIt compilation
AutoItSetOption("MustDeclareVars", 1)

Global $appName = "Omni Legacy Bridge Client"
Global $appPath = "C:\Users\IKYY\Downloads\Omni\bin\OmniDesktopClient.exe"

Func RunOmniGUITest()
    ConsoleWrite("OMNI AutoIt: Starting GUI integration test..." & @CRLF)
    
    ; 1. Launch the application
    Local $pid = Run($appPath)
    If $pid = 0 Then
        MsgBox($MB_ICONERROR, "OMNI Error", "Failed to launch the Omni Desktop Client.")
        Exit
    EndIf

    ; 2. Wait for the main window to become active
    WinWaitActive($appName, "", 10)
    If Not WinActive($appName) Then
        MsgBox($MB_ICONERROR, "OMNI Error", "Application window did not appear.")
        ProcessClose($pid)
        Exit
    EndIf

    ; 3. Simulate user input: Typing a prompt into the input field
    ; Assuming Control ID 1001 is the input text box
    ControlSetText($appName, "", 1001, "AutoIt Automated Inference Test Request.")
    
    ; 4. Simulate clicking the "Generate" button (Control ID 1002)
    ControlClick($appName, "", 1002)
    
    ; 5. Wait for inference processing (simulated wait)
    Sleep(3000)
    
    ; 6. Read the result from the output text box (Control ID 1003)
    Local $resultText = ControlGetText($appName, "", 1003)
    
    If StringLen($resultText) > 0 Then
        ConsoleWrite("OMNI AutoIt: Test Passed. Output received: " & StringLeft($resultText, 50) & "..." & @CRLF)
    Else
        ConsoleWrite("OMNI AutoIt: Test Failed. No output from C-ABI." & @CRLF)
    EndIf
    
    ; Close the application
    WinClose($appName)
EndFunc

RunOmniGUITest()
