# Inicia o Jupyter Notebook usando pasta local de runtime (evita erro de permissão no AppData)

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$RuntimeDir = Join-Path $ProjectRoot ".jupyter\runtime"
$DataDir = Join-Path $ProjectRoot ".jupyter\data"

New-Item -ItemType Directory -Force -Path $RuntimeDir | Out-Null
New-Item -ItemType Directory -Force -Path $DataDir | Out-Null

$env:JUPYTER_RUNTIME_DIR = $RuntimeDir
$env:JUPYTER_DATA_DIR = $DataDir

Set-Location $ProjectRoot
& "$ProjectRoot\venv\Scripts\jupyter-notebook.exe" notebooks/analise_completa.ipynb
