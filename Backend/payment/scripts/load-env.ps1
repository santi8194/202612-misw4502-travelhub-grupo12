param(
    [string]$EnvFile = ".env",
    [switch]$ValidateRequired
)

$resolvedEnvFile = Resolve-Path -LiteralPath $EnvFile -ErrorAction Stop

Get-Content -LiteralPath $resolvedEnvFile | ForEach-Object {
    $line = $_.Trim()
    if (-not $line -or $line.StartsWith("#")) {
        return
    }

    $name, $value = $line -split "=", 2
    if (-not $name) {
        return
    }

    $safeValue = ""
    if ($null -ne $value) {
        $safeValue = $value.Trim()
    }

    [System.Environment]::SetEnvironmentVariable($name.Trim(), $safeValue, "Process")
}

if ($ValidateRequired) {
    $required = @(
        "WOMPI_PUBLIC_KEY",
        "WOMPI_PRIVATE_KEY",
        "WOMPI_INTEGRITY_SECRET",
        "WOMPI_EVENTS_SECRET"
    )

    $missing = @($required | Where-Object { -not [System.Environment]::GetEnvironmentVariable($_, "Process") })
    if ($missing.Count -gt 0) {
        throw "Faltan variables requeridas en el entorno: $($missing -join ', ')"
    }
}

Write-Host "Variables de entorno cargadas desde $resolvedEnvFile"
