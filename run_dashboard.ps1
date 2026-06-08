# Inicia o dashboard Streamlit do projeto

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

Set-Location $ProjectRoot
& "$ProjectRoot\venv\Scripts\streamlit.exe" run dashboard/app.py
