region           = "us-east-1"
owner            = "grupo12"
eks_state_bucket = "travelhub-tfstate-dev-us-east-1"
eks_state_key    = "eks/dev/terraform.tfstate"

namespace          = "ingress-nginx"
ingress_class_name = "nginx"
chart_version      = "4.11.2"
