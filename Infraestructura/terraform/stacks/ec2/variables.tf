variable "region" {
  description = "AWS Region where the EC2 resources will be managed."
  type        = string
  nullable    = false
}

variable "owner" {
  description = "Owner tag used for academic purposes."
  type        = string
  nullable    = false
}

variable "instance_name" {
  description = "Name tag for the DEV EC2 instance."
  type        = string
}

variable "instance_type" {
  description = "EC2 instance type for the DEV host."
  type        = string
}

variable "vpc_id" {
  description = "VPC where the DEV EC2 instance will be deployed."
  type        = string
  nullable    = false
}

variable "subnet_id" {
  description = "Subnet where the DEV EC2 instance will be deployed."
  type        = string
  nullable    = false
}

variable "ssh_ingress_cidr_blocks" {
  description = "Restricted CIDR blocks allowed to reach SSH."
  type        = list(string)
  default     = []
}

variable "root_volume_size_gib" {
  description = "Size in GiB of the EC2 root volume."
  type        = number
  default     = 20
}

variable "key_name" {
  description = "Optional EC2 key pair for manual SSH access."
  type        = string
  default     = null
}
