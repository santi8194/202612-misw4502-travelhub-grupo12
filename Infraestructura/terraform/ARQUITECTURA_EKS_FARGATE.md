# TravelHub — Arquitectura EKS Fargate (Dev)

## Visión General

```
Internet
   │
   ▼
[AWS NLB]  ←── creado automáticamente por ingress-nginx (LoadBalancer + nlb)
   │
   ▼
[ingress-nginx controller]  ←── Fargate pod · namespace: ingress-nginx
   │
   ├── /auth*        → authservice:80    (authservice-ingress.yaml)
   ├── /search/*     → search:80         ┐
   ├── /booking/*    → booking:80        │ backend-ingress.yaml
   └── /catalog/*    → catalog:80        ┘

[Microservicios]  ←── Fargate pods · namespace: default
  authservice │ search │ booking │ catalog
        │
        ▼
[RDS PostgreSQL db.t3.micro]  ←── única instancia compartida
  authservice_db │ search_db │ booking_db │ catalog_db
```

### Stacks de Terraform (orden de despliegue)

| # | Stack | Ruta | State Key (S3) |
|---|-------|------|----------------|
| 1 | container_registry | `stacks/container_registry/` | `container_registry/dev/terraform.tfstate` |
| 2 | eks | `stacks/eks/` | `eks/dev/terraform.tfstate` |
| 3 | database | `stacks/database/` | `database/terraform.tfstate` |
| 4 | ingress | `stacks/ingress/` | `ingress/dev/terraform.tfstate` |

**Backend S3:** `travelhub-tfstate-dev-us-east-1` · región `us-east-1` · locking nativo (`use_lockfile = true`)

---

## Pre-requisitos

```bash
# Herramientas requeridas
terraform --version   # >= 1.10
aws --version         # AWS CLI v2 configurado con credenciales de grupo12
kubectl version       # >= 1.30
psql --version        # para el bootstrap de la BD
```

```bash
# Verificar credenciales AWS
aws sts get-caller-identity
```

---

## Paso 1 — Container Registry (ECR)

Crea los repositorios ECR para las imágenes Docker.

```bash
cd Infraestructura/terraform/stacks/container_registry

terraform init -reconfigure

terraform plan  -var-file=../../environments/dev/container_registry/dev.tfvars
terraform apply -var-file=../../environments/dev/container_registry/dev.tfvars
```

Repositorios creados: `authservice`, `search`, `booking`, `catalog`.

---

## Paso 2 — Clúster EKS Fargate

Crea el clúster EKS con tres Fargate profiles: `kube-system`, `default`, `ingress-nginx`.

```bash
cd Infraestructura/terraform/stacks/eks

terraform init -reconfigure

terraform plan  -var-file=../../environments/dev/eks/dev.tfvars
terraform apply -var-file=../../environments/dev/eks/dev.tfvars
```

Configurar `kubectl` tras el apply:

```bash
aws eks update-kubeconfig \
  --name grupo12-travelhub-eks \
  --region us-east-1

kubectl get nodes   # con Fargate los "nodos" aparecen como fargate-*
```

> **Nota CoreDNS en Fargate:** EKS despliega CoreDNS en `kube-system`. En Fargate puede necesitar un patch para eliminar la toleration de EC2:
> ```bash
> kubectl patch deployment coredns \
>   -n kube-system \
>   --type json \
>   -p='[{"op":"remove","path":"/spec/template/metadata/annotations/eks.amazonaws.com~1compute-type"}]'
> ```

---

## Paso 3 — Base de Datos RDS

Crea la instancia RDS PostgreSQL `db.t3.micro` y los secretos en AWS Secrets Manager.

```bash
cd Infraestructura/terraform/stacks/database

terraform init \
  -backend-config=../../environments/dev/database/backend.tfvars

terraform plan \
  -var-file=../../environments/dev/database/terraform.tfvars \
  -var-file=database.secrets.tfvars

terraform apply \
  -var-file=../../environments/dev/database/terraform.tfvars \
  -var-file=database.secrets.tfvars
```

### Bootstrap SQL — crear bases de datos y usuarios

Ejecutar **una sola vez** tras crear la instancia RDS. Obtener el endpoint:

```bash
terraform output rds_address
```

```bash
# Desde la raíz del repositorio
psql -h <RDS_ENDPOINT> \
     -U travelhub \
     -d postgres \
     -v authservice_password='Grupo12.2026' \
     -v booking_password='Grupo12.2026' \
     -v catalog_password='Grupo12.2026' \
     -v search_password='Grupo12.2026' \
     -f Infraestructura/sql/rds/bootstrap_service_databases.sql
```

Bases de datos creadas: `authservice_db`, `booking_db`, `catalog_db`, `search_db`.

---

## Paso 4 — Ingress Controller (ingress-nginx)

Instala ingress-nginx vía Helm. Requiere que el clúster EKS ya esté disponible.

```bash
cd Infraestructura/terraform/stacks/ingress

terraform init -reconfigure

terraform plan  -var-file=../../environments/dev/ingress/dev.tfvars
terraform apply -var-file=../../environments/dev/ingress/dev.tfvars
```

Obtener la URL del NLB creado:

```bash
kubectl get svc -n ingress-nginx
# Copiar el EXTERNAL-IP (hostname del NLB)
```

---

## Paso 5 — Secretos en Kubernetes

Los deployments leen secretos de K8s que deben crearse **antes** de aplicar los manifiestos.
Los valores vienen de los secretos de AWS Secrets Manager creados en el Paso 3.

```bash
RDS_HOST=$(cd Infraestructura/terraform/stacks/database && terraform output -raw rds_address)

# search
kubectl create secret generic search-db-secret \
  --from-literal=DB_HOST=$RDS_HOST \
  --from-literal=DB_PORT=5432 \
  --from-literal=DB_NAME=search_db \
  --from-literal=DB_USER=search_app \
  --from-literal=DB_PASSWORD=Grupo12.2026

# authservice
kubectl create secret generic authservice-db-secret \
  --from-literal=DB_HOST=$RDS_HOST \
  --from-literal=DB_PORT=5432 \
  --from-literal=DB_NAME=authservice_db \
  --from-literal=DB_USER=authservice_app \
  --from-literal=DB_PASSWORD=Grupo12.2026

kubectl create secret generic authservice-app-secret \
  --from-literal=SECRET_KEY=super_secret_key_change_in_production_12345

# booking
kubectl create secret generic booking-db-secret \
  --from-literal=DB_HOST=$RDS_HOST \
  --from-literal=DB_PORT=5432 \
  --from-literal=DB_NAME=booking_db \
  --from-literal=DB_USER=booking_app \
  --from-literal=DB_PASSWORD=Grupo12.2026

# catalog
kubectl create secret generic catalog-db-secret \
  --from-literal=DB_HOST=$RDS_HOST \
  --from-literal=DB_PORT=5432 \
  --from-literal=DB_NAME=catalog_db \
  --from-literal=DB_USER=catalog_app \
  --from-literal=DB_PASSWORD=Grupo12.2026
```

---

## Paso 6 — Manifiestos Kubernetes

```bash
# Desde la raíz del repositorio
K8S=Infraestructura/k8s/aws

# Search
kubectl apply -f $K8S/search-deployment.yaml
kubectl apply -f $K8S/search-service.yaml

# Authservice
kubectl apply -f $K8S/authservice-deployment.yaml
kubectl apply -f $K8S/authservice-service.yaml

# Booking
kubectl apply -f $K8S/booking-deployment.yaml
kubectl apply -f $K8S/booking-service.yaml

# Catalog
kubectl apply -f $K8S/catalog-deployment.yaml
kubectl apply -f $K8S/catalog-service.yaml

# Ingress rules
kubectl apply -f $K8S/backend-ingress.yaml
kubectl apply -f $K8S/authservice-ingress.yaml
```

Verificar estado de los pods:

```bash
kubectl get pods -n default
kubectl get pods -n ingress-nginx
kubectl describe pod <nombre-pod>   # para debug
```

---

## Verificación End-to-End

```bash
NLB_URL=$(kubectl get svc ingress-nginx-controller -n ingress-nginx \
  -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')

echo "NLB: $NLB_URL"

curl http://$NLB_URL/search/health
curl http://$NLB_URL/auth/health
curl http://$NLB_URL/booking/health
curl http://$NLB_URL/catalog/health
```

---

## Teardown (solo si es necesario)

> ⚠️ **Requiere autorización explícita antes de ejecutar.**

```bash
# Eliminar manifiestos K8s primero
kubectl delete -f Infraestructura/k8s/aws/

# Destruir stacks en orden inverso
cd Infraestructura/terraform/stacks/ingress && terraform destroy -var-file=../../environments/dev/ingress/dev.tfvars
cd Infraestructura/terraform/stacks/database && terraform destroy -var-file=../../environments/dev/database/terraform.tfvars -var-file=database.secrets.tfvars
cd Infraestructura/terraform/stacks/eks && terraform destroy -var-file=../../environments/dev/eks/dev.tfvars
cd Infraestructura/terraform/stacks/container_registry && terraform destroy -var-file=../../environments/dev/container_registry/dev.tfvars
```
