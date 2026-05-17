#!/bin/bash
set -e

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
# Repo root is two levels up from Infraestructura/scripts
REPO_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

function invoke_step {
    local message=$1
    echo "==> $message"
}

cd "$REPO_ROOT"

try_block() {
    invoke_step "Starting Minikube"
    minikube start --driver=docker --container-runtime=docker --kubernetes-version=v1.31.0

    invoke_step "Setting kubectl context to Minikube"
    kubectl config use-context minikube

    invoke_step "Enabling ingress addon"
    minikube addons enable ingress

    # Array of images to build: "Name|Context"
    images=(
        "travelhub/authservice:minikube|Backend/authservice"
        "travelhub/catalog:minikube|Backend/catalog"
        "travelhub/booking:minikube|Backend/booking"
        "travelhub/search:minikube|Backend/search"
        "travelhub/notification:minikube|Backend/notification"
        "travelhub/payment:minikube|Backend/payment"
        "travelhub/pmsintegration:minikube|Backend/pms-integration"
        "travelhub/partnermanagement:minikube|Backend/partner-management"
    )

    for item in "${images[@]}"; do
        IFS="|" read -r name context <<< "$item"
        invoke_step "Building $name"
        minikube image build -t "$name" "$context"
    done

    invoke_step "Applying namespace and secrets"
    kubectl apply -f Infraestructura/k8s/minikube/local-secrets.yaml

    invoke_step "Applying postgres manifests"
    kubectl apply -f Infraestructura/k8s/minikube/postgres.yaml

    invoke_step "Applying application manifests"
    kubectl apply -f Infraestructura/k8s/minikube/apps.yaml

    invoke_step "Waiting for postgres"
    kubectl rollout status deployment/postgres -n travelhub --timeout=180s

    deployments=(
        "rabbitmq-broker"
        "authservice"
        "booking"
        "catalog"
        "search"
        "notification-deployment"
        "payment-deployment"
        "pmsintegration-deployment"
        "partnermanagement-deployment"
        "booking-saga-worker"
    )

    for deployment in "${deployments[@]}"; do
        invoke_step "Waiting for deployment/$deployment"
        kubectl rollout status "deployment/$deployment" -n travelhub --timeout=240s
    done

    echo ""
    echo "TravelHub stack deployed on Minikube."
    echo "Namespace: travelhub"
    echo "Ingress test URL: http://127.0.0.1:8080"
    echo "Use 'kubectl -n ingress-nginx port-forward service/ingress-nginx-controller 8080:80' to access it locally."
}

try_block
