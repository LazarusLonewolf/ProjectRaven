
# PowerShell Launcher for Project_Raven GUI
$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$env:PROJECT_RAVEN_ROOT = $projectRoot

# Set working directory
Set-Location "$projectRoot\container\aeris_core\app\ui"

# Launch the Raven GUI using Python
& "C:\Program Files\Python311\python.exe" "raven_gui.py"
