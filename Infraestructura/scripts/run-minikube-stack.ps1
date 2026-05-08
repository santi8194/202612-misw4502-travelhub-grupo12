$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$minikube = Join-Path $env:USERPROFILE "AppData\Local\Programs\minikube\minikube.exe"

if (-not (Test-Path $minikube)) {
    throw "Minikube no esta instalado en la ruta esperada: $minikube"
}

function Invoke-Step {
    param(
        [string]$Message,
        [scriptblock]$Script
    )

    Write-Host "==> $Message"
    & $Script
}

Push-Location $repoRoot

try {
    Invoke-Step "Starting Minikube" {
        & $minikube start --driver=docker --container-runtime=docker --kubernetes-version=v1.31.0
    }

    Invoke-Step "Setting kubectl context to Minikube" {
        kubectl config use-context minikube | Out-Null
    }

    Invoke-Step "Enabling ingress addon" {
        & $minikube addons enable ingress
    }

    $images = @(
        @{ Name = "travelhub/authservice:minikube"; Context = "Backend/authservice" },
        @{ Name = "travelhub/catalog:minikube"; Context = "Backend/catalog" },
        @{ Name = "travelhub/booking:minikube"; Context = "Backend/booking" },
        @{ Name = "travelhub/search:minikube"; Context = "Backend/search" },
        @{ Name = "travelhub/notification:minikube"; Context = "Backend/notification" },
        @{ Name = "travelhub/payment:minikube"; Context = "Backend/payment" },
        @{ Name = "travelhub/pmsintegration:minikube"; Context = "Backend/pms-integration" },
        @{ Name = "travelhub/partnermanagement:minikube"; Context = "Backend/partner-management" }
    )

    foreach ($image in $images) {
        Invoke-Step "Building $($image.Name)" {
            & $minikube image build -t $image.Name $image.Context
        }
    }

    Invoke-Step "Applying namespace and secrets" {
        kubectl apply -f Infraestructura/k8s/minikube/local-secrets.yaml
    }

    Invoke-Step "Applying postgres manifests" {
        kubectl apply -f Infraestructura/k8s/minikube/postgres.yaml
    }

    Invoke-Step "Applying application manifests" {
        kubectl apply -f Infraestructura/k8s/minikube/apps.yaml
    }

    Invoke-Step "Waiting for postgres" {
        kubectl rollout status deployment/postgres -n travelhub --timeout=180s
    }

    $deployments = @(
        "rabbitmq-broker",
        "authservice",
        "booking",
        "catalog",
        "search",
        "notification-deployment",
        "payment-deployment",
        "pmsintegration-deployment",
        "partnermanagement-deployment",
        "booking-saga-worker"
    )

    foreach ($deployment in $deployments) {
        Invoke-Step "Waiting for deployment/$deployment" {
            kubectl rollout status "deployment/$deployment" -n travelhub --timeout=240s
        }
    }

    Write-Host ""
    Write-Host "TravelHub stack deployed on Minikube."
    Write-Host "Namespace: travelhub"
    Write-Host "Ingress test URL: http://127.0.0.1:8080"
    Write-Host "Use 'kubectl -n ingress-nginx port-forward service/ingress-nginx-controller 8080:80' to access it locally."
}
finally {
    Pop-Location
}
