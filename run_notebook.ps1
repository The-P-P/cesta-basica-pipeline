# Inicia o Jupyter Notebook usando pastas locais do projeto
# (evita erro de permissao em AppData\Roaming\jupyter\runtime)

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$JupyterDir = Join-Path $ProjectRoot ".jupyter"
$RuntimeDir = Join-Path $JupyterDir "runtime"

New-Item -ItemType Directory -Force -Path $RuntimeDir | Out-Null

$env:JUPYTER_CONFIG_DIR = $JupyterDir
$env:JUPYTER_RUNTIME_DIR = $RuntimeDir

Set-Location $ProjectRoot
& "$ProjectRoot\venv\Scripts\jupyter.exe" notebook notebooks/analise_completa.ipynb
