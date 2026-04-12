variable "region" {
  description = "La región de AWS donde se desplegarán los recursos."
  type        = string
  nullable    = false
}

variable "eks_log_retention_in_days" {
  description = "Retencion deseada del log group de control plane de EKS."
  type        = number
  default     = 7
}

variable "cluster_name" {
  description = "El nombre del clúster EKS."
  type        = string
}

variable "k8s_cluster_version" {
  description = "La versión de Kubernetes para el clúster EKS."
  type        = string
}

variable "cluster_endpoint_public_access" {
  description = "Habilita o deshabilita el acceso público al endpoint del clúster EKS."
  type        = bool
}

variable "vpc_id" {
  description = "El ID de la VPC donde se desplegará el clúster EKS."
  type        = string
  nullable    = false
}

variable "subnet_ids" {
  description = "Lista de subnets donde se desplegará el clúster EKS y sus node groups."
  type        = list(string)
  nullable    = false
}

variable "node_instance_types" {
  description = "Tipos de instancia EC2 permitidos para el managed node group."
  type        = list(string)
  nullable    = false
}

variable "node_desired_size" {
  description = "Cantidad deseada de nodos en el managed node group."
  type        = number
}

variable "node_min_size" {
  description = "Cantidad mínima de nodos en el managed node group."
  type        = number
}

variable "node_max_size" {
  description = "Cantidad máxima de nodos en el managed node group."
  type        = number
}

variable "owner" {
  description = "Dueño de los recursos. Para propósito académico."
  type        = string
  nullable    = false
}
