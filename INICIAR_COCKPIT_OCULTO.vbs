Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)

WshShell.Run "python """ & scriptDir & "\servidor_local.py""", 0, False

WScript.Sleep 1000
WshShell.Run "cmd /c start http://localhost:8088/index.html", 0, False
