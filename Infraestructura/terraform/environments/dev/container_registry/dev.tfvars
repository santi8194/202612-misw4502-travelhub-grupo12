# container_registry/dev.tfvars
#
# Active variables consumed by the current stack.
# Each variable includes why it is present and whether it is:
# - required by Terraform
# - added to avoid hidden defaults

# Required by Terraform.
# The stack provider needs an explicit AWS region and the backend is also in us-east-1.
region = "us-east-1"

# Required by Terraform.
# Used by provider default_tags so created resources are tagged with ownership metadata.
owner = "grupo12"

# Required by Terraform.
# Each repository name must match the runtime naming used by the CD pipeline and Kubernetes manifests.
authservice_repository_name = "authservice"
search_repository_name      = "search"

# Added to avoid hidden defaults.
# The stack has a default of 5, but dev should set retention explicitly to control storage cost.
keep_tags_number = 3

# Pending externalization for MVP stability; these are currently hardcoded in the module
# and are documented here so dev behavior is explicit.
#
# Added to avoid hidden defaults.
# Dev should keep tag mutability explicit because it affects release behavior.
# image_tag_mutability = "MUTABLE"
#
# Added to avoid hidden defaults.
# Dev can allow force delete, but this should be a conscious choice.
# force_delete = true
#
# Added to avoid hidden defaults.
# Dev keeps scan-on-push disabled to minimize cost and friction.
# scan_on_push = false
