$ErrorActionPreference = "Stop"

$namespace = "travelhub"
$region = "us-east-1"

$services = @(
    @{
        AwsSecret = "travelhub/dev/authservice/db-credentials"
        K8sSecret = "authservice-db-secret"
    },
    @{
        AwsSecret = "travelhub/dev/booking/db-credentials"
        K8sSecret = "booking-db-secret"
    },
    @{
        AwsSecret = "travelhub/dev/catalog/db-credentials"
        K8sSecret = "catalog-db-secret"
    },
    @{
        AwsSecret = "travelhub/dev/search/db-credentials"
        K8sSecret = "search-db-secret"
    }
)

function Get-AwsSecretObject {
    param(
        [string]$SecretId
    )

    $rawSecret = aws secretsmanager get-secret-value --region $region --secret-id $SecretId
    if (-not $rawSecret) {
        throw "No se pudo obtener el secreto $SecretId desde AWS."
    }

    $secretEnvelope = $rawSecret | ConvertFrom-Json
    return $secretEnvelope.SecretString | ConvertFrom-Json
}

function Set-KubernetesDbSecret {
    param(
        [string]$SecretName,
        [object]$DbSecret
    )

    $dbHost = [string]$DbSecret.host
    $dbPort = [string]$DbSecret.port
    $dbName = [string]$DbSecret.dbname
    $dbUser = [string]$DbSecret.username
    $dbPassword = [string]$DbSecret.password

    kubectl create secret generic $SecretName `
        --namespace $namespace `
        --from-literal=DB_HOST=$dbHost `
        --from-literal=DB_PORT=$dbPort `
        --from-literal=DB_NAME=$dbName `
        --from-literal=DB_USER=$dbUser `
        --from-literal=DB_PASSWORD=$dbPassword `
        --dry-run=client -o yaml | kubectl apply -f -
}

foreach ($service in $services) {
    Write-Host "==> Syncing $($service.K8sSecret) from AWS Secrets Manager"
    $dbSecret = Get-AwsSecretObject -SecretId $service.AwsSecret
    Set-KubernetesDbSecret -SecretName $service.K8sSecret -DbSecret $dbSecret
}

Write-Host "==> Restarting database-backed deployments"
kubectl rollout restart deployment/authservice -n $namespace
kubectl rollout restart deployment/booking -n $namespace
kubectl rollout restart deployment/catalog -n $namespace
kubectl rollout restart deployment/search -n $namespace

Write-Host "==> Waiting for rollouts"
kubectl rollout status deployment/authservice -n $namespace --timeout=240s
kubectl rollout status deployment/booking -n $namespace --timeout=240s
kubectl rollout status deployment/catalog -n $namespace --timeout=240s
kubectl rollout status deployment/search -n $namespace --timeout=240s

Write-Host ""
Write-Host "Minikube is now using the AWS RDS credentials for authservice, booking, catalog, and search."
