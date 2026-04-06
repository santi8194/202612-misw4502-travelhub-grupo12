# Remote State for Terraform Stacks

This repository uses a multi-stack Terraform layout:

- `stacks/container_registry`
- `stacks/eks`

Both stacks now use an S3 backend with native lock files stored in the same bucket and isolated by stack-specific state keys.

## Backend Settings

- Bucket: `travelhub-tfstate-dev-us-east-1`
- Region: `us-east-1`
- Locking: `use_lockfile = true`
- Encryption: `encrypt = true`

State keys:

- `container_registry/dev/terraform.tfstate`
- `eks/dev/terraform.tfstate`

## Manual Initialization

Run these commands manually after pulling the changes:

```powershell
cd Infraestructura/terraform/stacks/container_registry
terraform init -reconfigure

cd ../eks
terraform init -reconfigure
```

`terraform init -reconfigure` forces Terraform to forget any cached backend settings and re-initialize the stack using the backend declared in `config.tf`.

If a stack already has a local `terraform.tfstate` that must be preserved, handle state migration explicitly before continuing with normal plan/apply operations.

## Verify State in S3

Check the `container_registry` state:

```powershell
aws s3 ls s3://travelhub-tfstate-dev-us-east-1/container_registry/dev/
```

Check the `eks` state:

```powershell
aws s3 ls s3://travelhub-tfstate-dev-us-east-1/eks/dev/
```

Expected object after state is created:

- `terraform.tfstate`

## Verify Native Locking

While a `terraform plan` or `terraform apply` is running, inspect the same prefixes:

```powershell
aws s3 ls s3://travelhub-tfstate-dev-us-east-1/container_registry/dev/
aws s3 ls s3://travelhub-tfstate-dev-us-east-1/eks/dev/
```

Expected during execution:

- `terraform.tfstate.tflock`

Expected after Terraform exits cleanly:

- the `.tflock` object is removed

## CI/CD Alignment Notes

The current GitHub Actions workflows should be updated later, but not in this change.

Required alignment:

- run Terraform from `Infraestructura/terraform/stacks/container_registry`
- run Terraform from `Infraestructura/terraform/stacks/eks`
- stop passing backend settings via `terraform init -backend-config=...`
- stop referencing `TF_LOCK_TABLE`, because native S3 lock files replace DynamoDB locking
- use the correct per-stack `tfvars` path from each stack working directory

The S3 backend is shared by both stacks, but the state remains isolated by the stack-specific `key` configured in each backend block.
