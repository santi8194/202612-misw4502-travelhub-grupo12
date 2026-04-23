param(
    [string]$EnvFile = ".env",
    [string]$Host = "127.0.0.1",
    [int]$Port = 8000
)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$paymentRoot = Split-Path -Parent $scriptDir
$pythonPath = Join-Path $paymentRoot ".venv\Scripts\python.exe"
$loadEnvScript = Join-Path $scriptDir "load-env.ps1"

if (-not (Test-Path -LiteralPath $pythonPath)) {
    throw "No se encontró el intérprete virtual en $pythonPath"
}

. $loadEnvScript -EnvFile (Join-Path $paymentRoot $EnvFile) -ValidateRequired

Write-Host "Iniciando payment en http://$Host`:$Port"
& $pythonPath -m uvicorn app:app --host $Host --port $Port --reload
