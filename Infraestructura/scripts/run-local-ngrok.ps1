[CmdletBinding()]
param(
    [string]$EnvFile = (Join-Path $PSScriptRoot '..\docker\.env.local.rds.dev'),
    [switch]$SkipBuild
)

$ErrorActionPreference = 'Stop'

$dockerDir = (Resolve-Path (Join-Path $PSScriptRoot '..\docker')).Path
$composeFiles = @(
    '-f', 'docker-compose.yml',
    '-f', 'docker-compose.local.yml'
)

function Get-EnvValues {
    param([string]$Path)

    $values = @{}
    foreach ($line in Get-Content -LiteralPath $Path) {
        if ($line -match '^\s*#' -or $line -notmatch '=') {
            continue
        }

        $key, $value = $line -split '=', 2
        $values[$key.Trim()] = $value.Trim()
    }
    return $values
}

function Wait-ForHttp {
    param(
        [string]$Url,
        [int]$TimeoutSeconds = 120
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    do {
        try {
            $response = Invoke-WebRequest -UseBasicParsing -Uri $Url -TimeoutSec 5
            if ($response.StatusCode -ge 200 -and $response.StatusCode -lt 500) {
                return
            }
        } catch {
            Start-Sleep -Seconds 2
        }
    } while ((Get-Date) -lt $deadline)

    throw "No se pudo obtener respuesta de $Url antes del timeout."
}

function Get-NgrokPublicUrl {
    param([int]$TimeoutSeconds = 120)

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    do {
        try {
            $payload = Invoke-RestMethod -Uri 'http://127.0.0.1:4040/api/tunnels' -TimeoutSec 5
            $httpsTunnel = $payload.tunnels | Where-Object { $_.proto -eq 'https' } | Select-Object -First 1
            if ($httpsTunnel.public_url) {
                return $httpsTunnel.public_url.TrimEnd('/')
            }
        } catch {
            Start-Sleep -Seconds 2
        }
    } while ((Get-Date) -lt $deadline)

    throw 'No se pudo obtener la URL publica HTTPS de ngrok desde http://127.0.0.1:4040/api/tunnels.'
}

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    throw 'Docker no esta disponible en PATH.'
}

$resolvedEnvFile = (Resolve-Path -LiteralPath $EnvFile).Path
$envValues = Get-EnvValues -Path $resolvedEnvFile
$requiredKeys = @(
    'NGROK_AUTHTOKEN',
    'WOMPI_PUBLIC_KEY',
    'WOMPI_PRIVATE_KEY',
    'WOMPI_INTEGRITY_SECRET',
    'WOMPI_EVENTS_SECRET'
)

$missingKeys = $requiredKeys | Where-Object {
    -not $envValues.ContainsKey($_) -or [string]::IsNullOrWhiteSpace($envValues[$_])
}

if ($missingKeys.Count -gt 0) {
    throw "Faltan variables requeridas en ${resolvedEnvFile}: $($missingKeys -join ', ')"
}

Push-Location $dockerDir
try {
    $composeBaseArgs = @('--env-file', $resolvedEnvFile) + $composeFiles

    if ($SkipBuild) {
        & docker compose @composeBaseArgs up -d
    } else {
        & docker compose @composeBaseArgs up -d --build
    }
    if ($LASTEXITCODE -ne 0) {
        throw 'docker compose up fallo.'
    }

    Wait-ForHttp -Url 'http://localhost:4200'
    Wait-ForHttp -Url 'http://localhost:5001/payment/health'
    Wait-ForHttp -Url 'http://localhost:4040'

    $publicUrl = Get-NgrokPublicUrl
    $env:PUBLIC_APP_BASE_URL = $publicUrl

    & docker compose @composeBaseArgs build user-web
    if ($LASTEXITCODE -ne 0) {
        throw 'No fue posible reconstruir user-web con la URL publica de ngrok.'
    }

    & docker compose @composeBaseArgs up -d user-web
    if ($LASTEXITCODE -ne 0) {
        throw 'No fue posible recrear user-web con la URL publica de ngrok.'
    }

    Wait-ForHttp -Url 'http://localhost:4200'

    Write-Host ''
    Write-Host 'Entorno local Wompi listo:' -ForegroundColor Green
    Write-Host "  User web local:      http://localhost:4200"
    Write-Host "  Partner web local:   http://localhost:4300"
    Write-Host "  Gateway backend:     http://localhost:5001"
    Write-Host "  Ngrok public URL:    $publicUrl"
    Write-Host "  Wompi webhook URL:   $publicUrl/payment/webhook"
    Write-Host ''
    Write-Host 'Configura la URL de eventos de Wompi Sandbox con la URL de webhook anterior.' -ForegroundColor Yellow
    Write-Host 'Si ngrok muestra su pantalla de advertencia gratuita, abre primero la URL publica y continua una vez en el navegador.' -ForegroundColor Yellow
}
finally {
    Pop-Location
}
